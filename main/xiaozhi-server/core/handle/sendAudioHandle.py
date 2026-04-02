import json
import time
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler
from core.utils import textUtils
from core.utils.util import audio_to_data
from core.providers.tts.dto.dto import SentenceType
from core.utils.audioRateController import AudioRateController

TAG = __name__
# Audio frame duration in milliseconds.
AUDIO_FRAME_DURATION = 60
# Number of packets to pre-buffer and send immediately to reduce latency.
PRE_BUFFER_COUNT = 5


async def sendAudioMessage(conn: "ConnectionHandler", sentenceType, audios, text):
    if conn.tts.tts_audio_first_sentence:
        conn.logger.bind(tag=TAG).info(f"Sending the first speech segment: {text}")
        conn.tts.tts_audio_first_sentence = False

    if sentenceType == SentenceType.FIRST:
        # Queue follow-up packets for the same sentence; send others immediately.
        if (
            hasattr(conn, "audio_rate_controller")
            and conn.audio_rate_controller
            and getattr(conn, "audio_flow_control", {}).get("sentence_id")
            == conn.sentence_id
        ):
            conn.audio_rate_controller.add_message(
                lambda: send_tts_message(conn, "sentence_start", text)
            )
        else:
            # Send immediately for a new sentence or before flow control starts.
            await send_tts_message(conn, "sentence_start", text)

    await sendAudio(conn, audios)
    # Send the sentence status update.
    if sentenceType is not SentenceType.MIDDLE:
        conn.logger.bind(tag=TAG).info(
            f"Sending audio message: {sentenceType}, {text}"
        )

    # Send the final status update for the last text fragment.
    if sentenceType == SentenceType.LAST:
        await send_tts_message(conn, "stop", None)
        conn.client_is_speaking = False
        if conn.close_after_chat:
            await conn.close()


async def _wait_for_audio_completion(conn: "ConnectionHandler"):
    """
    Wait for the audio queue to drain and for the pre-buffered packets to finish
    playback.

    Args:
        conn: Connection object.
    """
    if hasattr(conn, "audio_rate_controller") and conn.audio_rate_controller:
        rate_controller = conn.audio_rate_controller
        conn.logger.bind(tag=TAG).debug(
            f"Waiting for audio delivery to finish; {len(rate_controller.queue)} packets remain in the queue"
        )
        await rate_controller.queue_empty_event.wait()

        # Wait for the pre-buffered packets to finish playback.
        # The first N packets are sent immediately, plus two packets of jitter
        # margin to allow the client to finish playing them.
        frame_duration_ms = rate_controller.frame_duration
        pre_buffer_playback_time = (PRE_BUFFER_COUNT + 2) * frame_duration_ms / 1000.0
        await asyncio.sleep(pre_buffer_playback_time)

        conn.logger.bind(tag=TAG).debug("Audio delivery complete")


async def _send_to_mqtt_gateway(
    conn: "ConnectionHandler", opus_packet, timestamp, sequence
):
    """
    Send an Opus packet with a 16-byte header to the MQTT gateway.

    Args:
        conn: Connection object.
        opus_packet: Opus packet payload.
        timestamp: Packet timestamp.
        sequence: Packet sequence number.
    """
    # Add a 16-byte header to the Opus payload.
    header = bytearray(16)
    header[0] = 1  # type
    header[2:4] = len(opus_packet).to_bytes(2, "big")  # payload length
    header[4:8] = sequence.to_bytes(4, "big")  # sequence
    header[8:12] = timestamp.to_bytes(4, "big")  # timestamp
    header[12:16] = len(opus_packet).to_bytes(4, "big")  # opus payload length

    # Send the complete packet including the header.
    complete_packet = bytes(header) + opus_packet
    await conn.websocket.send(complete_packet)


async def sendAudio(
    conn: "ConnectionHandler", audios, frame_duration=AUDIO_FRAME_DURATION
):
    """
    Send audio packets with precise flow control via AudioRateController.

    Args:
        conn: Connection object.
        audios: A single Opus packet (`bytes`) or a list of Opus packets.
        frame_duration: Frame duration in milliseconds. Defaults to
            `AUDIO_FRAME_DURATION`.
    """
    if audios is None or len(audios) == 0:
        return

    send_delay = conn.config.get("tts_audio_send_delay", -1) / 1000.0
    is_single_packet = isinstance(audios, bytes)

    # Initialize or reuse the rate controller.
    rate_controller, flow_control = _get_or_create_rate_controller(
        conn, frame_duration, is_single_packet
    )

    # Normalize the input into a list.
    audio_list = [audios] if is_single_packet else audios

    # Deliver the audio packets.
    await _send_audio_with_rate_control(
        conn, audio_list, rate_controller, flow_control, send_delay
    )


def _get_or_create_rate_controller(
    conn: "ConnectionHandler", frame_duration, is_single_packet
):
    """
    Get or create the rate controller and the flow-control state.

    Args:
        conn: Connection object.
        frame_duration: Frame duration.
        is_single_packet: Whether the input is a single streaming packet
            (`True`) or a batch of packets (`False`).

    Returns:
        (rate_controller, flow_control)
    """
    # Determine whether the controller needs to be reset.
    need_reset = False

    if not hasattr(conn, "audio_rate_controller"):
        # Create the controller on first use.
        need_reset = True
    else:
        rate_controller = conn.audio_rate_controller

        # Reset when the background sender is no longer running.
        if (
            not rate_controller.pending_send_task
            or rate_controller.pending_send_task.done()
        ):
            need_reset = True
        # Reset when the sentence changes.
        elif (
            getattr(conn, "audio_flow_control", {}).get("sentence_id")
            != conn.sentence_id
        ):
            need_reset = True

    if need_reset:
        # Create or reset the rate controller.
        if not hasattr(conn, "audio_rate_controller"):
            conn.audio_rate_controller = AudioRateController(frame_duration)
        else:
            conn.audio_rate_controller.reset()

        # Initialize the flow-control state.
        conn.audio_flow_control = {
            "packet_count": 0,
            "sequence": 0,
            "sentence_id": conn.sentence_id,
        }

        # Start the background sending loop.
        _start_background_sender(
            conn, conn.audio_rate_controller, conn.audio_flow_control
        )

    return conn.audio_rate_controller, conn.audio_flow_control


def _start_background_sender(conn: "ConnectionHandler", rate_controller, flow_control):
    """
    Start the background audio-sending task.

    Args:
        conn: Connection object.
        rate_controller: Rate controller instance.
        flow_control: Flow-control state.
    """

    async def send_callback(packet):
        # Stop cleanly if the client has already aborted.
        if conn.client_abort:
            raise asyncio.CancelledError("Client aborted")

        conn.last_activity_time = time.time() * 1000
        await _do_send_audio(conn, packet, flow_control)

    # Start the background loop through the controller.
    rate_controller.start_sending(send_callback)


async def _send_audio_with_rate_control(
    conn: "ConnectionHandler", audio_list, rate_controller, flow_control, send_delay
):
    """
    Send audio packets through the rate controller.

    Args:
        conn: Connection object.
        audio_list: List of audio packets.
        rate_controller: Rate controller instance.
        flow_control: Flow-control state.
        send_delay: Fixed delay in seconds. `-1` means dynamic flow control.
    """
    for packet in audio_list:
        if conn.client_abort:
            return

        conn.last_activity_time = time.time() * 1000

        # Pre-buffer the first N packets by sending them immediately.
        if flow_control["packet_count"] < PRE_BUFFER_COUNT:
            await _do_send_audio(conn, packet, flow_control)
        elif send_delay > 0:
            # Fixed-delay mode.
            await asyncio.sleep(send_delay)
            await _do_send_audio(conn, packet, flow_control)
        else:
            # Dynamic flow-control mode: queue packets for the background loop.
            rate_controller.add_audio(packet)


async def _do_send_audio(conn: "ConnectionHandler", opus_packet, flow_control):
    """
    Perform the actual audio send.
    """
    packet_index = flow_control.get("packet_count", 0)
    sequence = flow_control.get("sequence", 0)

    if conn.conn_from_mqtt_gateway:
        # Compute a timestamp based on the playback position.
        start_time = time.time()
        timestamp = int(start_time * 1000) % (2**32)
        await _send_to_mqtt_gateway(conn, opus_packet, timestamp, sequence)
    else:
        # Send the raw Opus packet directly.
        await conn.websocket.send(opus_packet)

    # Update flow-control state.
    flow_control["packet_count"] = packet_index + 1
    flow_control["sequence"] = sequence + 1


async def send_tts_message(conn: "ConnectionHandler", state, text=None):
    """Send a TTS status message."""
    if text is None and state == "sentence_start":
        return
    message = {"type": "tts", "state": state, "session_id": conn.session_id}
    if text is not None:
        message["text"] = textUtils.check_emoji(text)

    # Handle the end of TTS playback.
    if state == "stop":
        # Play the stop notification sound if configured.
        tts_notify = conn.config.get("enable_stop_tts_notify", False)
        if tts_notify:
            stop_tts_notify_voice = conn.config.get(
                "stop_tts_notify_voice", "config/assets/tts_notify.mp3"
            )
            audios = await audio_to_data(stop_tts_notify_voice, is_opus=True)
            await sendAudio(conn, audios)
        # Wait for all queued audio packets to finish sending.
        await _wait_for_audio_completion(conn)
        # Stop the background audio-sending loop.
        conn.audio_rate_controller.stop_sending()
        # Clear the server-side speaking state.
        conn.clearSpeakStatus()

    # Send the status update to the client.
    await conn.websocket.send(json.dumps(message))


async def send_stt_message(conn: "ConnectionHandler", text):
    """Send an STT status message."""
    end_prompt_str = conn.config.get("end_prompt", {}).get("prompt")
    if end_prompt_str and end_prompt_str == text:
        await send_tts_message(conn, "start")
        return

    # Parse JSON-wrapped text so only the spoken content is displayed.
    display_text = text
    try:
        # Try to parse the payload as JSON.
        if text.strip().startswith("{") and text.strip().endswith("}"):
            parsed_data = json.loads(text)
            if isinstance(parsed_data, dict) and "content" in parsed_data:
                # For speaker-aware payloads, show only the content text.
                display_text = parsed_data["content"]
                # Persist the speaker metadata on the connection object.
                if "speaker" in parsed_data:
                    conn.current_speaker = parsed_data["speaker"]
    except (json.JSONDecodeError, TypeError):
        # Fall back to the original text when the payload is not JSON.
        display_text = text
    stt_text = textUtils.get_string_no_punctuation_or_emoji(display_text)
    await conn.websocket.send(
        json.dumps({"type": "stt", "text": stt_text, "session_id": conn.session_id})
    )
    await send_tts_message(conn, "start")
    # Keep the server-side speaking state aligned after the start message.
    conn.client_is_speaking = True


async def send_display_message(conn: "ConnectionHandler", text):
    """Send a display-only message."""
    message = {
        "type": "stt",
        "text": text,
        "session_id": conn.session_id
    }
    await conn.websocket.send(json.dumps(message))
