import time
import asyncio
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

from core.handle.receiveAudioHandle import startToChat
from core.handle.reportHandle import enqueue_asr_report
from core.handle.sendAudioHandle import send_stt_message, send_tts_message
from core.handle.textMessageHandler import TextMessageHandler
from core.handle.textMessageType import TextMessageType
from core.utils.util import remove_punctuation_and_length
from core.providers.asr.dto.dto import InterfaceType

TAG = __name__

class ListenTextMessageHandler(TextMessageHandler):
    """Handler for listen-state messages from the client."""

    @property
    def message_type(self) -> TextMessageType:
        return TextMessageType.LISTEN

    async def handle(self, conn: "ConnectionHandler", msg_json: Dict[str, Any]) -> None:
        if "mode" in msg_json:
            conn.client_listen_mode = msg_json["mode"]
            conn.logger.bind(tag=TAG).debug(
                f"Client listen mode: {conn.client_listen_mode}"
            )
        if msg_json["state"] == "start":
            # The device is switching from playback mode back to recording mode.
            conn.reset_audio_states()
        elif msg_json["state"] == "stop":
            conn.client_voice_stop = True
            if conn.asr.interface_type == InterfaceType.STREAM:
                # In streaming mode, send a stop request to the ASR backend.
                asyncio.create_task(conn.asr._send_stop_request())
            else:
                # In non-streaming mode, trigger ASR directly from buffered audio.
                if len(conn.asr_audio) > 0:
                    asr_audio_task = conn.asr_audio.copy()
                    conn.reset_audio_states()

                    if len(asr_audio_task) > 0:
                        await conn.asr.handle_voice_stop(conn, asr_audio_task)
        elif msg_json["state"] == "detect":
            conn.client_have_voice = False
            conn.reset_audio_states()
            if "text" in msg_json:
                conn.last_activity_time = time.time() * 1000
                original_text = msg_json["text"]  # Preserve the original text.
                filtered_len, filtered_text = remove_punctuation_and_length(
                    original_text
                )

                # Check whether the text is a wake word.
                is_wakeup_words = filtered_text in conn.config.get("wakeup_words")
                # Check whether wake-word greetings are enabled.
                enable_greeting = conn.config.get("enable_greeting", True)

                if is_wakeup_words and not enable_greeting:
                    # If wake-word greetings are disabled, just stop there.
                    await send_stt_message(conn, original_text)
                    await send_tts_message(conn, "stop", None)
                    conn.client_is_speaking = False
                elif is_wakeup_words:
                    conn.just_woken_up = True
                    # Report wake-word text without attaching audio data.
                    enqueue_asr_report(conn, "Hey, hello there.", [])
                    await startToChat(conn, "Hey, hello there.")
                else:
                    conn.just_woken_up = True
                    # Report plain text without attaching audio data.
                    enqueue_asr_report(conn, original_text, [])
                    # Let the LLM respond to the text normally.
                    await startToChat(conn, original_text)
