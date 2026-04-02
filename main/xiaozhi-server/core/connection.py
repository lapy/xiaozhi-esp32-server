import os
import sys
import copy
import json
import uuid
import time
import queue
import asyncio
import threading
import traceback
import subprocess
import websockets

from core.utils.util import (
    extract_json_from_string,
    check_vad_update,
    check_asr_update,
    filter_sensitive_info,
)
from typing import Dict, Any
from collections import deque
from core.utils.modules_initialize import (
    initialize_modules,
    initialize_tts,
    initialize_asr,
)
from core.handle.reportHandle import report, enqueue_tool_report
from core.providers.tts.default import DefaultTTS
from concurrent.futures import ThreadPoolExecutor
from core.utils.dialogue import Message, Dialogue
from core.providers.asr.dto.dto import InterfaceType
from core.handle.textHandle import handleTextMessage
from core.providers.tools.unified_tool_handler import UnifiedToolHandler
from plugins_func.loadplugins import auto_import_modules
from plugins_func.register import Action
from core.auth import AuthenticationError
from config.config_loader import get_private_config_from_api
from core.providers.tts.dto.dto import ContentType, TTSMessageDTO, SentenceType
from config.logger import setup_logging, build_module_string, create_connection_logger
from config.manage_api_client import DeviceNotFoundException, DeviceBindException
from core.utils.prompt_manager import PromptManager
from core.utils.voiceprint_provider import VoiceprintProvider
from core.utils.util import get_system_error_response
from core.utils import textUtils


TAG = __name__

# Tool-calling rules injected into the prompt at runtime.
TOOL_CALLING_RULES = """
<tool_calling>
Core principle: you are an assistant with tool access. When the user asks for real-time information or wants an action performed, call the appropriate tool and do not invent an answer.

- **When tool use is required:**
  1. Real-time information requests such as news, non-local weather, stock prices, or exchange rates.
  2. Actions such as playing music, controlling a device, taking a photo, or setting an alarm.
  3. Knowledge base retrieval when `search_from_ragflow` is available and the user intent calls for it.
  4. Lunar calendar questions about any day other than today, such as tomorrow's lunar date, taboos, or solar terms.
  5. When the user says "take a photo", call `self_camera_take_photo` and default the `question` parameter to "Describe the items you can see".

- **When tool use is not required:**
  1. Information already present in `<context>`, such as the current time, today's date, today's lunar calendar, or local weather.
  2. Normal conversation, greetings, small talk, emotional support, or storytelling.
  3. General knowledge questions that do not depend on real-time data.

- **Tool-calling requirements:**
  1. Judge each request independently and do not reuse historical tool results. Fetch fresh data when the request needs it.
  2. When a request contains multiple tasks, call every required tool in order and summarize each result in order.
  3. Follow tool parameter requirements strictly and provide every required argument.
  4. If you are unsure, ask for clarification or explain the limitation instead of guessing or fabricating.
  5. Do not call tools that are not available. If an earlier tool is mentioned but unavailable now, ignore it or explain that it is unavailable.

- **Anti-shortcut rules (highest priority):**
  1. **Re-evaluate every request independently:** even if a previous turn did not require tools, this turn might.
  2. **Do not imitate prior response patterns:** previous non-tool replies do not justify skipping tools now.
  3. **Self-check before replying:** ask yourself, "Does this request involve real-time information or an action? If so, did I call the right tool?"
  4. **History does not override the present:** each user request must be treated as a fresh decision point.
</tool_calling>
"""

auto_import_modules("plugins_func.functions")


class TTSException(RuntimeError):
    pass


class ConnectionHandler:
    def __init__(
            self,
            config: Dict[str, Any],
            _vad,
            _asr,
            _llm,
            _memory,
            _intent,
            server=None,
    ):
        self.common_config = config
        self.config = copy.deepcopy(config)
        self.session_id = str(uuid.uuid4())
        self.logger = setup_logging()
        self.server = server  # Keep a reference to the server instance.

        self.need_bind = False  # Whether the device still needs to be bound.
        self.bind_completed_event = asyncio.Event()
        self.bind_code = None  # Verification code used during device binding.
        self.last_bind_prompt_time = 0  # Last bind prompt playback time in seconds.
        self.bind_prompt_interval = 60  # Interval between bind prompts in seconds.

        self.read_config_from_api = self.config.get("read_config_from_api", False)

        self.websocket: websockets.ServerConnection | None = None
        self.headers = None
        self.device_id = None
        self.client_ip = None
        self.prompt = None
        self.welcome_msg = None
        self.max_output_size = 0
        self.chat_history_conf = 0
        self.audio_format = "opus"
        self.sample_rate = 24000  # Default sample rate, updated from the client hello message.

        # Client state
        self.client_abort = False
        self.client_is_speaking = False
        self.client_listen_mode = "auto"

        # Threading and task state
        self.loop = None  # Captured from the running event loop in handle_connection.
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Reporting worker thread
        self.report_queue = queue.Queue()
        self.report_thread = None
        # These flags can be tuned later if ASR/TTS reporting needs to be split.
        self.report_asr_enable = self.read_config_from_api
        self.report_tts_enable = self.read_config_from_api

        # Dependent components
        self.vad = None
        self.asr = None
        self.tts = None
        self._asr = _asr
        self._vad = _vad
        self.llm = _llm
        self.memory = _memory
        self.intent = _intent

        # Manage voiceprint recognition per connection.
        self.voiceprint_provider = None

        # VAD state
        self.client_audio_buffer = bytearray()
        self.client_have_voice = False
        self.client_voice_window = deque(maxlen=5)
        self.first_activity_time = 0.0  # Time of first activity in milliseconds.
        self.last_activity_time = 0.0  # Unified activity timestamp in milliseconds.
        self.client_voice_stop = False
        self.last_is_voice = False

        # ASR state
        # A shared local ASR instance may be reused across connections, so
        # connection-specific ASR variables stay private to this class.
        self.asr_audio = []
        self.asr_audio_queue = queue.Queue()
        self.current_speaker = None  # Store the current speaker identity.

        # LLM state
        self.dialogue = Dialogue()

        # Tool-call statistics used for monitoring and recovery logic.
        self.tool_call_stats = {
            'last_call_turn': -1,  # Dialogue turn of the last tool call.
            'consecutive_no_call': 0,  # Number of consecutive non-tool turns.
        }

        # TTS state
        self.sentence_id = None
        # Handle cases where TTS returns audio without text.
        self.tts_MessageText = ""

        # IoT state
        self.iot_descriptors = {}
        self.func_handler = None

        self.cmd_exit = self.config["exit_commands"]

        # Whether to close the connection after the current chat finishes.
        self.close_after_chat = False
        self.load_function_plugin = False
        self.intent_type = "nointent"

        self.timeout_seconds = (
                int(self.config.get("close_connection_no_voice_time", 120)) + 60
        )  # Add a secondary 60-second grace period before final close.
        self.timeout_task = None

        # {"mcp": true} means MCP is enabled for this connection.
        self.features = None

        # Track whether the connection originates from the MQTT gateway.
        self.conn_from_mqtt_gateway = False

        # Initialize the prompt manager.
        self.prompt_manager = PromptManager(self.config, self.logger)

    async def handle_connection(self, ws: websockets.ServerConnection):
        try:
            # Capture the running event loop inside async context.
            self.loop = asyncio.get_running_loop()

            # Read and validate headers.
            self.headers = dict(ws.request.headers)
            real_ip = self.headers.get("x-real-ip") or self.headers.get(
                "x-forwarded-for"
            )
            if real_ip:
                self.client_ip = real_ip.split(",")[0].strip()
            else:
                self.client_ip = ws.remote_address[0]
            self.logger.bind(tag=TAG).info(
                f"{self.client_ip} conn - Headers: {self.headers}"
            )

            self.device_id = self.headers.get("device-id", None)

            # Authentication passed, continue handling the connection.
            self.websocket = ws

            # Check whether the request came from the MQTT gateway.
            request_path = ws.request.path
            self.conn_from_mqtt_gateway = request_path.endswith("?from=mqtt_gateway")
            if self.conn_from_mqtt_gateway:
                self.logger.bind(tag=TAG).info("Connection source: MQTT gateway")

            # Initialize activity timestamps.
            self.first_activity_time = time.time() * 1000
            self.last_activity_time = time.time() * 1000

            # Start the timeout monitor task.
            self.timeout_task = asyncio.create_task(self._check_timeout())

            self.welcome_msg = self.config["xiaozhi"]
            self.welcome_msg["session_id"] = self.session_id

            # Read the output sample rate from the configuration.
            self.sample_rate = self.welcome_msg["audio_params"]["sample_rate"]
            self.logger.bind(tag=TAG).info(
                f"Configured output sample rate: {self.sample_rate}"
            )

            # Initialize configuration and components in the background without blocking.
            asyncio.create_task(self._background_initialize())

            try:
                async for message in self.websocket:
                    await self._route_message(message)
            except websockets.exceptions.ConnectionClosed:
                self.logger.bind(tag=TAG).info("Client disconnected")

        except AuthenticationError as e:
            self.logger.bind(tag=TAG).error(f"Authentication failed: {str(e)}")
            return
        except Exception as e:
            stack_trace = traceback.format_exc()
            self.logger.bind(tag=TAG).error(f"Connection error: {str(e)}-{stack_trace}")
            return
        finally:
            try:
                await self._save_and_close(ws)
            except Exception as final_error:
                self.logger.bind(tag=TAG).error(
                    f"Error during final cleanup: {final_error}"
                )
                # Make sure the connection still closes even if memory save fails.
                try:
                    await self.close(ws)
                except Exception as close_error:
                    self.logger.bind(tag=TAG).error(
                        f"Error while forcing connection close: {close_error}"
                    )

    async def _save_and_close(self, ws):
        """Save memory in the background and then close the connection."""
        try:
            if self.memory:
                # Save memory asynchronously using a background thread.
                def save_memory_task():
                    try:
                        # Create a dedicated event loop to avoid conflicts with the main loop.
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            self.memory.save_memory(
                                self.dialogue.dialogue, self.session_id
                            )
                        )
                    except Exception as e:
                        self.logger.bind(tag=TAG).error(f"Failed to save memory: {e}")
                    finally:
                        try:
                            loop.close()
                        except Exception:
                            pass

                # Start the save thread and do not wait for it to finish.
                threading.Thread(target=save_memory_task, daemon=True).start()
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to save memory: {e}")
        finally:
            # Close immediately instead of waiting for memory persistence.
            try:
                await self.close(ws)
            except Exception as close_error:
                self.logger.bind(tag=TAG).error(
                    f"Failed to close connection after saving memory: {close_error}"
                )

    async def _discard_message_with_bind_prompt(self):
        """Discard a message and trigger the bind prompt if needed."""
        current_time = time.time()
        # Check whether it is time to replay the binding prompt.
        if current_time - self.last_bind_prompt_time >= self.bind_prompt_interval:
            self.last_bind_prompt_time = current_time
            # Reuse the existing bind prompt logic.
            from core.handle.receiveAudioHandle import check_bind_device

            asyncio.create_task(check_bind_device(self))

    async def _route_message(self, message):
        """Route incoming messages based on connection state and message type."""
        # Wait until the actual bind state has been resolved.
        if not self.bind_completed_event.is_set():
            # The real state is not ready yet, so wait briefly before discarding.
            try:
                await asyncio.wait_for(self.bind_completed_event.wait(), timeout=1)
            except asyncio.TimeoutError:
                # Still unresolved after the timeout, discard the message.
                await self._discard_message_with_bind_prompt()
                return

        # Bind state is known, so check whether binding is still required.
        if self.need_bind:
            # Binding is still required, so ignore the message.
            await self._discard_message_with_bind_prompt()
            return

        if isinstance(message, str):
            await handleTextMessage(self, message)
        elif isinstance(message, bytes):
            if self.vad is None or self.asr is None:
                return

            # Handle audio frames coming from the MQTT gateway.
            if self.conn_from_mqtt_gateway and len(message) >= 16:
                handled = await self._process_mqtt_audio_message(message)
                if handled:
                    return

            # If no MQTT header handling is required, queue the raw audio payload.
            self.asr_audio_queue.put(message)

    async def _process_mqtt_audio_message(self, message):
        """
        Process an audio message from the MQTT gateway.

        The first 16 bytes are treated as a header. The payload audio is then
        extracted and queued in timestamp order when possible.

        Args:
            message: Audio message with the MQTT gateway header

        Returns:
            bool: Whether the message was successfully processed
        """
        try:
            # Extract header fields.
            timestamp = int.from_bytes(message[8:12], "big")
            audio_length = int.from_bytes(message[12:16], "big")

            # Extract the audio payload.
            if audio_length > 0 and len(message) >= 16 + audio_length:
                # The message declares a valid payload length.
                audio_data = message[16 : 16 + audio_length]
                # Reorder packets by timestamp when possible.
                self._process_websocket_audio(audio_data, timestamp)
                return True
            elif len(message) > 16:
                # Fall back to treating everything after the header as audio.
                audio_data = message[16:]
                self.asr_audio_queue.put(audio_data)
                return True
        except Exception as e:
            self.logger.bind(tag=TAG).error(
                f"Failed to parse WebSocket audio packet: {e}"
            )

        # Return False so the caller can continue with normal handling.
        return False

    def _process_websocket_audio(self, audio_data, timestamp):
        """Process WebSocket audio packets with basic timestamp reordering."""
        # Initialize timestamp buffer management.
        if not hasattr(self, "audio_timestamp_buffer"):
            self.audio_timestamp_buffer = {}
            self.last_processed_timestamp = 0
            self.max_timestamp_buffer_size = 20

        # Process in-order packets immediately.
        if timestamp >= self.last_processed_timestamp:
            self.asr_audio_queue.put(audio_data)
            self.last_processed_timestamp = timestamp

            # Flush any buffered packets that can now be processed in order.
            processed_any = True
            while processed_any:
                processed_any = False
                for ts in sorted(self.audio_timestamp_buffer.keys()):
                    if ts > self.last_processed_timestamp:
                        buffered_audio = self.audio_timestamp_buffer.pop(ts)
                        self.asr_audio_queue.put(buffered_audio)
                        self.last_processed_timestamp = ts
                        processed_any = True
                        break
        else:
            # Store out-of-order packets temporarily when the buffer allows it.
            if len(self.audio_timestamp_buffer) < self.max_timestamp_buffer_size:
                self.audio_timestamp_buffer[timestamp] = audio_data
            else:
                self.asr_audio_queue.put(audio_data)

    async def handle_restart(self, message):
        """Handle a server restart request."""
        try:

            self.logger.bind(tag=TAG).info("Received server restart command")

            # Send an acknowledgement before restarting.
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "server",
                        "status": "success",
                        "message": "Server restart in progress...",
                        "content": {"action": "restart"},
                    }
                )
            )

            # Restart asynchronously so the event loop stays responsive.
            def restart_server():
                """Perform the actual restart."""
                time.sleep(1)
                self.logger.bind(tag=TAG).info("Restarting server process")
                subprocess.Popen(
                    [sys.executable, "app.py"],
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    start_new_session=True,
                )
                os._exit(0)

            # Run the restart in a thread to avoid blocking the event loop.
            threading.Thread(target=restart_server, daemon=True).start()

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Restart failed: {str(e)}")
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "server",
                        "status": "error",
                        "message": f"Restart failed: {str(e)}",
                        "content": {"action": "restart"},
                    }
                )
            )

    def _initialize_components(self):
        try:
            if self.tts is None:
                self.tts = self._initialize_tts()
            # Open the TTS audio channels.
            asyncio.run_coroutine_threadsafe(
                self.tts.open_audio_channels(self), self.loop
            )
            if self.need_bind:
                self.bind_completed_event.set()
                return
            self.selected_module_str = build_module_string(
                self.config.get("selected_module", {})
            )
            self.logger = create_connection_logger(self.selected_module_str)

            """Initialize runtime components."""
            if self.config.get("prompt") is not None:
                user_prompt = self.config["prompt"]
                # Use the quick prompt path for initial setup.
                prompt = self.prompt_manager.get_quick_prompt(user_prompt)
                self.change_system_prompt(prompt)
                self.logger.bind(tag=TAG).info(
                    f"Quick initialization complete with prompt: {prompt[:50]}..."
                )

            """Initialize local components."""
            if self.vad is None:
                self.vad = self._vad
            if self.asr is None:
                self.asr = self._initialize_asr()

            # Initialize voiceprint recognition.
            self._initialize_voiceprint()
            # Open the ASR audio channels.
            asyncio.run_coroutine_threadsafe(
                self.asr.open_audio_channels(self), self.loop
            )

            """Load memory."""
            self._initialize_memory()
            """Load intent recognition."""
            self._initialize_intent()
            """Initialize reporting threads."""
            self._init_report_threads()
            """Refresh the system prompt."""
            self._init_prompt_enhancement()

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to initialize components: {e}")

    def _init_prompt_enhancement(self):

        # Refresh context information before rebuilding the prompt.
        self.prompt_manager.update_context_info(self, self.client_ip)
        enhanced_prompt = self.prompt_manager.build_enhanced_prompt(
            self.config["prompt"], self.device_id, self.client_ip
        )
        if enhanced_prompt:
            self.change_system_prompt(enhanced_prompt)
            self.logger.bind(tag=TAG).debug("System prompt refreshed with enhancements")

    def _init_report_threads(self):
        """Initialize reporting threads for ASR and TTS events."""
        if not self.read_config_from_api or self.need_bind:
            return
        if self.chat_history_conf == 0:
            return
        if self.report_thread is None or not self.report_thread.is_alive():
            self.report_thread = threading.Thread(
                target=self._report_worker, daemon=True
            )
            self.report_thread.start()
            self.logger.bind(tag=TAG).info("TTS reporting thread started")

    def _initialize_tts(self):
        """Initialize the TTS provider for this connection."""
        tts = None
        if not self.need_bind:
            tts = initialize_tts(self.config)

        if tts is None:
            tts = DefaultTTS(self.config, delete_audio_file=True)

        return tts

    def _initialize_asr(self):
        """Initialize the ASR provider for this connection."""
        if (
                self._asr is not None
                and hasattr(self._asr, "interface_type")
                and self._asr.interface_type == InterfaceType.LOCAL
        ):
            # Shared local ASR instances can be reused across connections.
            asr = self._asr
        else:
            # Remote ASR providers need a dedicated instance per connection.
            asr = initialize_asr(self.config)

        return asr

    def _initialize_voiceprint(self):
        """Initialize voiceprint recognition for the current connection."""
        try:
            voiceprint_config = self.config.get("voiceprint", {})
            if voiceprint_config:
                voiceprint_provider = VoiceprintProvider(voiceprint_config)
                if voiceprint_provider is not None and voiceprint_provider.enabled:
                    self.voiceprint_provider = voiceprint_provider
                    self.logger.bind(tag=TAG).info(
                        "Voiceprint recognition enabled for this connection"
                    )
                else:
                    self.logger.bind(tag=TAG).warning(
                        "Voiceprint recognition enabled, but configuration is incomplete"
                    )
            else:
                self.logger.bind(tag=TAG).info("Voiceprint recognition is disabled")
        except Exception as e:
            self.logger.bind(tag=TAG).warning(
                f"Failed to initialize voiceprint recognition: {str(e)}"
            )

    async def _background_initialize(self):
        """Initialize configuration and components in the background."""
        try:
            # Load per-device configuration asynchronously.
            await self._initialize_private_config_async()
            # Initialize runtime components on the worker pool.
            self.executor.submit(self._initialize_components)
        except Exception as e:
            self.logger.bind(tag=TAG).error(
                f"Background initialization failed: {e}"
            )

    async def _initialize_private_config_async(self):
        """Load device-specific configuration asynchronously without blocking."""
        if not self.read_config_from_api:
            self.need_bind = False
            self.bind_completed_event.set()
            return
        try:
            begin_time = time.time()
            private_config = await get_private_config_from_api(
                self.config,
                self.headers.get("device-id"),
                self.headers.get("client-id", self.headers.get("device-id")),
            )
            private_config["delete_audio"] = bool(self.config.get("delete_audio", True))
            self.logger.bind(tag=TAG).info(
                f"Fetched private config asynchronously in {time.time() - begin_time} seconds: "
                f"{json.dumps(filter_sensitive_info(private_config), ensure_ascii=False)}"
            )
            self.need_bind = False
            self.bind_completed_event.set()
        except DeviceNotFoundException as e:
            self.need_bind = True
            private_config = {}
        except DeviceBindException as e:
            self.need_bind = True
            self.bind_code = e.bind_code
            private_config = {}
        except Exception as e:
            self.need_bind = True
            self.logger.bind(tag=TAG).error(
                f"Failed to fetch private config asynchronously: {e}"
            )
            private_config = {}

        init_llm, init_tts, init_memory, init_intent = (
            False,
            False,
            False,
            False,
        )

        init_vad = check_vad_update(self.common_config, private_config)
        init_asr = check_asr_update(self.common_config, private_config)

        if init_vad:
            self.config["VAD"] = private_config["VAD"]
            self.config["selected_module"]["VAD"] = private_config["selected_module"][
                "VAD"
            ]
        if init_asr:
            self.config["ASR"] = private_config["ASR"]
            self.config["selected_module"]["ASR"] = private_config["selected_module"][
                "ASR"
            ]
        if private_config.get("TTS", None) is not None:
            init_tts = True
            self.config["TTS"] = private_config["TTS"]
            self.config["selected_module"]["TTS"] = private_config["selected_module"][
                "TTS"
            ]
        if private_config.get("LLM", None) is not None:
            init_llm = True
            self.config["LLM"] = private_config["LLM"]
            self.config["selected_module"]["LLM"] = private_config["selected_module"][
                "LLM"
            ]
        if private_config.get("VLLM", None) is not None:
            self.config["VLLM"] = private_config["VLLM"]
            self.config["selected_module"]["VLLM"] = private_config["selected_module"][
                "VLLM"
            ]
        if private_config.get("Memory", None) is not None:
            init_memory = True
            self.config["Memory"] = private_config["Memory"]
            self.config["selected_module"]["Memory"] = private_config[
                "selected_module"
            ]["Memory"]
        if private_config.get("Intent", None) is not None:
            init_intent = True
            self.config["Intent"] = private_config["Intent"]
            model_intent = private_config.get("selected_module", {}).get("Intent", {})
            self.config["selected_module"]["Intent"] = model_intent
            # Load plugin configuration.
            if model_intent != "Intent_nointent":
                plugin_from_server = private_config.get("plugins", {})
                for plugin, config_str in plugin_from_server.items():
                    plugin_from_server[plugin] = json.loads(config_str)
                self.config["plugins"] = plugin_from_server
                self.config["Intent"][self.config["selected_module"]["Intent"]][
                    "functions"
                ] = plugin_from_server.keys()
        if private_config.get("prompt", None) is not None:
            self.config["prompt"] = private_config["prompt"]
        # Load voiceprint configuration.
        if private_config.get("voiceprint", None) is not None:
            self.config["voiceprint"] = private_config["voiceprint"]
        if private_config.get("summaryMemory", None) is not None:
            self.config["summaryMemory"] = private_config["summaryMemory"]
        if private_config.get("device_max_output_size", None) is not None:
            self.max_output_size = int(private_config["device_max_output_size"])
        if private_config.get("chat_history_conf", None) is not None:
            self.chat_history_conf = int(private_config["chat_history_conf"])
        if private_config.get("mcp_endpoint", None) is not None:
            self.config["mcp_endpoint"] = private_config["mcp_endpoint"]
        if private_config.get("context_providers", None) is not None:
            self.config["context_providers"] = private_config["context_providers"]

        # Run module initialization on a worker thread to avoid blocking the loop.
        try:
            modules = await self.loop.run_in_executor(
                None,  # Use the default thread pool.
                initialize_modules,
                self.logger,
                private_config,
                init_vad,
                init_asr,
                init_llm,
                init_tts,
                init_memory,
                init_intent,
            )
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to initialize modules: {e}")
            modules = {}
        if modules.get("tts", None) is not None:
            self.tts = modules["tts"]
        if modules.get("vad", None) is not None:
            self.vad = modules["vad"]
        if modules.get("asr", None) is not None:
            self.asr = modules["asr"]
        if modules.get("llm", None) is not None:
            self.llm = modules["llm"]
        if modules.get("intent", None) is not None:
            self.intent = modules["intent"]
        if modules.get("memory", None) is not None:
            self.memory = modules["memory"]

    def _initialize_memory(self):
        if self.memory is None:
            return
        """Initialize the configured memory module."""
        self.memory.init_memory(
            role_id=self.device_id,
            llm=self.llm,
            summary_memory=self.config.get("summaryMemory", None),
            save_to_file=not self.read_config_from_api,
        )

        # Read memory summarization configuration.
        memory_config = self.config["Memory"]
        memory_type = self.config["Memory"][self.config["selected_module"]["Memory"]][
            "type"
        ]
        # Return immediately when memory summarization is disabled.
        if memory_type == "nomem" or memory_type == "mem_report_only":
            return
        # Special handling for mem_local_short mode.
        elif memory_type == "mem_local_short":
            memory_llm_name = memory_config[self.config["selected_module"]["Memory"]][
                "llm"
            ]
            if memory_llm_name and memory_llm_name in self.config["LLM"]:
                # Create a dedicated LLM instance when one is configured explicitly.
                from core.utils import llm as llm_utils

                memory_llm_config = self.config["LLM"][memory_llm_name]
                memory_llm_type = memory_llm_config.get("type", memory_llm_name)
                memory_llm = llm_utils.create_instance(
                    memory_llm_type, memory_llm_config
                )
                self.logger.bind(tag=TAG).info(
                    f"Created dedicated LLM for memory summarization: {memory_llm_name}, type: {memory_llm_type}"
                )
                self.memory.set_llm(memory_llm)
            else:
                # Otherwise, reuse the primary LLM instance.
                self.memory.set_llm(self.llm)
                self.logger.bind(tag=TAG).info(
                    "Using the primary LLM for memory summarization"
                )

    def _initialize_intent(self):
        if self.intent is None:
            return
        self.intent_type = self.config["Intent"][
            self.config["selected_module"]["Intent"]
        ]["type"]
        if self.intent_type == "function_call" or self.intent_type == "intent_llm":
            self.load_function_plugin = True
        """Initialize the configured intent recognition module."""
        # Read intent configuration.
        intent_config = self.config["Intent"]
        intent_type = self.config["Intent"][self.config["selected_module"]["Intent"]][
            "type"
        ]

        # Return immediately when intent recognition is disabled.
        if intent_type == "nointent":
            return
        # Special handling for intent_llm mode.
        elif intent_type == "intent_llm":
            intent_llm_name = intent_config[self.config["selected_module"]["Intent"]][
                "llm"
            ]

            if intent_llm_name and intent_llm_name in self.config["LLM"]:
                # Create a dedicated LLM instance when one is configured explicitly.
                from core.utils import llm as llm_utils

                intent_llm_config = self.config["LLM"][intent_llm_name]
                intent_llm_type = intent_llm_config.get("type", intent_llm_name)
                intent_llm = llm_utils.create_instance(
                    intent_llm_type, intent_llm_config
                )
                self.logger.bind(tag=TAG).info(
                    f"Created dedicated LLM for intent recognition: {intent_llm_name}, type: {intent_llm_type}"
                )
                self.intent.set_llm(intent_llm)
            else:
                # Otherwise, reuse the primary LLM instance.
                self.intent.set_llm(self.llm)
                self.logger.bind(tag=TAG).info(
                    "Using the primary LLM for intent recognition"
                )

        """Load the unified tool handler."""
        self.func_handler = UnifiedToolHandler(self)

        # Initialize the tool handler asynchronously.
        if hasattr(self, "loop") and self.loop:
            asyncio.run_coroutine_threadsafe(self.func_handler._initialize(), self.loop)

    def change_system_prompt(self, prompt):
        self.prompt = prompt
        # Push the latest system prompt into the dialogue context.
        self.dialogue.update_system_message(self.prompt)

    def chat(self, query, depth=0):
        if query is not None:
            self.logger.bind(tag=TAG).info(f"LLM received user message: {query}")

        # Create a new sentence ID and emit the FIRST event for top-level turns.
        if depth == 0:
            self.sentence_id = str(uuid.uuid4().hex)
            self.dialogue.put(Message(role="user", content=query))
            self.tts.tts_text_queue.put(
                TTSMessageDTO(
                    sentence_id=self.sentence_id,
                    sentence_type=SentenceType.FIRST,
                    content_type=ContentType.ACTION,
                )
            )

        # Limit recursive tool-call depth to avoid infinite loops.
        MAX_DEPTH = 5
        force_final_answer = False  # Whether a final answer must be forced.

        if depth >= MAX_DEPTH:
            self.logger.bind(tag=TAG).debug(
                f"Reached maximum tool-call depth {MAX_DEPTH}; forcing a final answer from available context"
            )
            force_final_answer = True
            # Inject a system instruction that requires the LLM to answer directly.
            self.dialogue.put(
                Message(
                    role="user",
                    content="[System Notice] The maximum tool-call limit has been reached. Use all information already gathered and provide the final answer directly. Do not call any more tools.",
                )
            )

        # For longer chats, reinforce correct tool usage when needed.
        force_reminder = False  # Whether to force an additional reminder.

        if depth == 0 and query is not None:
            dialogue_length = len(self.dialogue.dialogue)
            current_turn = dialogue_length // 2

            # Check how many turns have passed since the last tool call.
            if self.tool_call_stats['last_call_turn'] >= 0:
                turns_since_last = current_turn - self.tool_call_stats['last_call_turn']
                if turns_since_last > 3:  # More than three turns without a tool call.
                    self.logger.bind(tag=TAG).warning(
                        f"Detected {turns_since_last} turns without tool usage; injecting a stronger reminder"
                    )
                    force_reminder = True

            # Dialogue truncation guardrail:
            # keep only the most recent turns if history grows too large.
            # max_dialogue_turns = 10
            # if dialogue_length > max_dialogue_turns * 2:
            #     removed = self.dialogue.trim_history(max_turns=max_dialogue_turns)
            #     if removed > 0:
            #         self.logger.bind(tag=TAG).info(
            #             f"Dialogue history grew too large ({dialogue_length} entries); trimmed to the latest {max_dialogue_turns} turns and removed {removed} messages"
            #         )

        # Define intent functions
        functions = None
        # Disable tool calling once maximum recursion depth is reached.
        if (
                self.intent_type == "function_call"
                and hasattr(self, "func_handler")
                and not force_final_answer
        ):
            functions = self.func_handler.get_functions()

        # For longer conversations, dynamically reinforce tool-call rules.
        tool_call_reminder = None
        if depth == 0 and query is not None and functions is not None:
            dialogue_length = len(self.dialogue.dialogue)
            # Inject stronger reminders after the conversation grows beyond a few turns.
            if dialogue_length > 4:
                tool_summary = self._get_tool_summary(functions)
                if tool_summary:
                    # Use different reminder strength depending on conversation length and recent tool usage.
                    if force_reminder:
                        # Strong reminder with the full rules prefix.
                        tool_call_reminder = (
                            TOOL_CALLING_RULES +
                            f"[Important Reminder] Multiple turns passed without using tools. Re-check whether a tool call is required before responding. "
                            f"Available tools: {tool_summary}."
                        )
                        reminder_level = "strong"
                    else:
                        # Medium reminder with the rules prefix.
                        tool_call_reminder = (
                            TOOL_CALLING_RULES +
                            f"Available tools: {tool_summary}. "
                            f"Use them only when the user needs live information lookup or an action to be executed. Regular conversation does not require tool calls."
                        )
                        reminder_level = "medium"
                    self.logger.bind(tag=TAG).debug(
                        f"Long dialogue detected ({dialogue_length} entries); injected {reminder_level} tool-call reminder. Available tools: {tool_summary}"
                    )

        response_message = []

        # Inject the tool reminder as a temporary message when needed.
        if tool_call_reminder:
            self.dialogue.put(Message(role="user", content=tool_call_reminder, is_temporary=True))

        try:
            # Run the dialogue with memory context when available.
            memory_str = None
            # Only query memory when there is an actual user question.
            if self.memory is not None and query:
                future = asyncio.run_coroutine_threadsafe(
                    self.memory.query_memory(query), self.loop
                )
                memory_str = future.result()

            if self.intent_type == "function_call" and functions is not None:
                # Use the streaming interface that supports tool calls.
                llm_responses = self.llm.response_with_functions(
                    self.session_id,
                    self.dialogue.get_llm_dialogue_with_memory(
                        memory_str, self.config.get("voiceprint", {})
                    ),
                    functions=functions,
                )
            else:
                llm_responses = self.llm.response(
                    self.session_id,
                    self.dialogue.get_llm_dialogue_with_memory(
                        memory_str, self.config.get("voiceprint", {})
                    ),
                )
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"LLM processing failed for {query}: {e}")
            return None

        # Process the streaming response.
        tool_call_flag = False
        # Support multiple parallel tool calls by collecting them in a list.
        tool_calls_list = []  # Format: [{"id": "", "name": "", "arguments": ""}]
        content_arguments = ""
        self.client_abort = False
        emotion_flag = True
        try:
            for response in llm_responses:
                if self.client_abort:
                    break
                if self.intent_type == "function_call" and functions is not None:
                    content, tools_call = response
                    if "content" in response:
                        content = response["content"]
                        tools_call = None
                    if content is not None and len(content) > 0:
                        content_arguments += content

                    if not tool_call_flag and content_arguments.startswith("<tool_call>"):
                        # print("content_arguments", content_arguments)
                        tool_call_flag = True

                    if tools_call is not None and len(tools_call) > 0:
                        tool_call_flag = True
                        self._merge_tool_calls(tool_calls_list, tools_call)
                else:
                    content = response

                # Extract the emotion marker only once near the start of each reply.
                if emotion_flag and content is not None and content.strip():
                    asyncio.run_coroutine_threadsafe(
                        textUtils.get_emotion(self, content),
                        self.loop,
                    )
                    emotion_flag = False

                if content is not None and len(content) > 0:
                    if not tool_call_flag:
                        response_message.append(content)
                        self.tts.tts_text_queue.put(
                            TTSMessageDTO(
                                sentence_id=self.sentence_id,
                                sentence_type=SentenceType.MIDDLE,
                                content_type=ContentType.TEXT,
                                content_detail=content,
                            )
                        )
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"LLM stream processing error: {e}")
            self.tts.tts_text_queue.put(
                TTSMessageDTO(
                    sentence_id=self.sentence_id,
                    sentence_type=SentenceType.MIDDLE,
                    content_type=ContentType.TEXT,
                    content_detail=get_system_error_response(self.config),
                )
            )
            if depth == 0:
                self.tts.tts_text_queue.put(
                    TTSMessageDTO(
                        sentence_id=self.sentence_id,
                        sentence_type=SentenceType.LAST,
                        content_type=ContentType.ACTION,
                    )
                )
            return
        # Handle function calls, if any were detected.
        if tool_call_flag:
            bHasError = False
            # Handle tool calls encoded in text form.
            if len(tool_calls_list) == 0 and content_arguments:
                a = extract_json_from_string(content_arguments)
                if a is not None:
                    try:
                        content_arguments_json = json.loads(a)
                        tool_calls_list.append(
                            {
                                "id": str(uuid.uuid4().hex),
                                "name": content_arguments_json["name"],
                                "arguments": json.dumps(
                                    content_arguments_json["arguments"],
                                    ensure_ascii=False,
                                ),
                            }
                        )
                    except Exception as e:
                        bHasError = True
                        response_message.append(a)
                else:
                    bHasError = True
                    response_message.append(content_arguments)
                if bHasError:
                    self.logger.bind(tag=TAG).error(
                        f"function call error: {content_arguments}"
                    )

            if not bHasError and len(tool_calls_list) > 0:
                self.logger.bind(tag=TAG).debug(
                    f"Detected {len(tool_calls_list)} tool calls"
                )

                # Update tool-call statistics.
                if depth == 0:
                    current_turn = len(self.dialogue.dialogue) // 2
                    self.tool_call_stats['last_call_turn'] = current_turn
                    self.tool_call_stats['consecutive_no_call'] = 0
                    self.logger.bind(tag=TAG).debug(
                        f"Tool-call stats updated: current_turn={current_turn}"
                    )

                # Persist any text emitted before the tool call sequence started.
                if len(response_message) > 0:
                    text_buff = "".join(response_message)
                    self.tts_MessageText = text_buff
                    self.dialogue.put(Message(role="assistant", content=text_buff))
                response_message.clear()

                # Collect futures for all tool calls.
                futures_with_data = []
                for tool_call_data in tool_calls_list:
                    self.logger.bind(tag=TAG).debug(
                        f"function_name={tool_call_data['name']}, function_id={tool_call_data['id']}, function_arguments={tool_call_data['arguments']}"
                    )

                    # Report the tool call through the shared reporting helper.
                    tool_input = json.loads(tool_call_data.get("arguments") or "{}")
                    enqueue_tool_report(self, tool_call_data['name'], tool_input)

                    future = asyncio.run_coroutine_threadsafe(
                        self.func_handler.handle_llm_function_call(
                            self, tool_call_data
                        ),
                        self.loop,
                    )
                    futures_with_data.append((future, tool_call_data, tool_input))

                # Wait for all tool calls; total wait time is bounded by the slowest one.
                tool_results = []
                for future, tool_call_data, tool_input in futures_with_data:
                    result = future.result()
                    tool_results.append((result, tool_call_data))

                    # Report tool-call results through the shared reporting helper.
                    enqueue_tool_report(self, tool_call_data['name'], tool_input, str(result.result) if result.result else None, report_tool_call=False)

                # Handle all tool results in one place.
                if tool_results:
                    self._handle_function_result(tool_results, depth=depth)

        # Store the assistant response in the dialogue history.
        if len(response_message) > 0:
            text_buff = "".join(response_message)
            self.tts_MessageText = text_buff
            self.dialogue.put(Message(role="assistant", content=text_buff))

            # Update stats for turns that completed without tool usage.
            if depth == 0 and not tool_call_flag:
                self.tool_call_stats['consecutive_no_call'] += 1

        if depth == 0:
            self.tts.tts_text_queue.put(
                TTSMessageDTO(
                    sentence_id=self.sentence_id,
                    sentence_type=SentenceType.LAST,
                    content_type=ContentType.ACTION,
                )
            )
            # Delay dialogue serialization until DEBUG logging actually consumes it.
            self.logger.bind(tag=TAG).debug(
                lambda: json.dumps(
                    self.dialogue.get_llm_dialogue(), indent=4, ensure_ascii=False
                )
            )

            # Remove temporary reminder messages that were injected for this turn.
            if tool_call_reminder and len(self.dialogue.dialogue) > 0:
                original_length = len(self.dialogue.dialogue)
                self.dialogue.dialogue = [
                    msg for msg in self.dialogue.dialogue
                    if not getattr(msg, 'is_temporary', False)
                ]
                if len(self.dialogue.dialogue) < original_length:
                    self.logger.bind(tag=TAG).debug(
                        "Cleared temporary tool-call reminder messages"
                    )

        return True

    def _get_tool_summary(self, functions: list) -> str:
        """
        Extract a compact tool summary used in reminder injection.

        Args:
            functions: List of tool definitions

        Returns:
            str: Tool names joined into a single string
        """
        if not functions:
            return ""

        datas = []
        for func in functions:
            func_info = func.get("function", {})
            name = func_info.get("name", "")
            datas.append(name)
        result = ", ".join(datas)
        return result

    def _handle_function_result(self, tool_results, depth):
        need_llm_tools = []

        for result, tool_call_data in tool_results:
            if result.action in [
                Action.RESPONSE,
                Action.NOTFOUND,
                Action.ERROR,
            ]:  # Reply directly to the client.
                text = result.response if result.response else result.result
                self.tts.tts_one_sentence(self, ContentType.TEXT, content_detail=text)
                self.dialogue.put(Message(role="assistant", content=text))
            elif result.action == Action.REQLLM:
                # Collect tool results that need a follow-up LLM pass.
                need_llm_tools.append((result, tool_call_data))
            else:
                pass

        if need_llm_tools:
            all_tool_calls = [
                {
                    "id": tool_call_data["id"],
                    "function": {
                        "arguments": (
                            "{}"
                            if tool_call_data["arguments"] == ""
                            else tool_call_data["arguments"]
                        ),
                        "name": tool_call_data["name"],
                    },
                    "type": "function",
                    "index": idx,
                }
                for idx, (_, tool_call_data) in enumerate(need_llm_tools)
            ]
            self.dialogue.put(Message(role="assistant", tool_calls=all_tool_calls))

            for result, tool_call_data in need_llm_tools:
                text = result.result
                if text is not None and len(text) > 0:
                    self.dialogue.put(
                        Message(
                            role="tool",
                            tool_call_id=(
                                str(uuid.uuid4())
                                if tool_call_data["id"] is None
                                else tool_call_data["id"]
                            ),
                            content=text,
                        )
                    )

            self.chat(None, depth=depth + 1)

    def _report_worker(self):
        """Worker thread that reports chat records."""
        while not self.stop_event.is_set():
            try:
                # Read from the queue with a timeout so stop requests are noticed quickly.
                item = self.report_queue.get(timeout=1)
                if item is None:  # Sentinel object
                    break
                try:
                    # Make sure the executor is still available.
                    if self.executor is None:
                        continue
                    # Submit reporting work to the thread pool.
                    self.executor.submit(self._process_report, *item)
                except Exception as e:
                    self.logger.bind(tag=TAG).error(
                        f"Chat-report thread error: {e}"
                    )
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.bind(tag=TAG).error(
                    f"Chat-report worker loop error: {e}"
                )

        self.logger.bind(tag=TAG).info("Chat-report thread exited")

    def _process_report(self, type, text, audio_data, report_time):
        """Process one queued reporting task."""
        try:
            # Execute async reporting work from a synchronous worker context.
            asyncio.run(report(self, type, text, audio_data, report_time))
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Report processing error: {e}")
        finally:
            # Mark the queued task as done.
            self.report_queue.task_done()

    def clearSpeakStatus(self):
        self.client_is_speaking = False
        self.logger.bind(tag=TAG).debug("Cleared server speaking state")

    async def close(self, ws=None):
        """Release connection resources and close open channels."""
        try:
            # Release VAD-side connection resources.
            if (
                    hasattr(self, "vad")
                    and self.vad
                    and hasattr(self.vad, "release_conn_resources")
            ):
                self.vad.release_conn_resources(self)

            # Clear local audio buffers.
            if hasattr(self, "audio_buffer"):
                self.audio_buffer.clear()

            # Cancel the timeout task.
            if self.timeout_task and not self.timeout_task.done():
                self.timeout_task.cancel()
                try:
                    await self.timeout_task
                except asyncio.CancelledError:
                    pass
                self.timeout_task = None

            # Clean up tool-handler resources.
            if hasattr(self, "func_handler") and self.func_handler:
                try:
                    await self.func_handler.cleanup()
                except Exception as cleanup_error:
                    self.logger.bind(tag=TAG).error(
                        f"Error while cleaning up tool handler: {cleanup_error}"
                    )

            # Signal shutdown to worker threads.
            if self.stop_event:
                self.stop_event.set()

            # Clear queued work.
            self.clear_queues()

            # Close the WebSocket connection.
            try:
                if ws:
                    # Close safely after checking connection state when possible.
                    try:
                        if hasattr(ws, "closed") and not ws.closed:
                            await ws.close()
                        elif hasattr(ws, "state") and ws.state.name != "CLOSED":
                            await ws.close()
                        else:
                            # Fall back to a direct close attempt.
                            await ws.close()
                    except Exception:
                        # Ignore close failures here.
                        pass
                elif self.websocket:
                    try:
                        if (
                                hasattr(self.websocket, "closed")
                                and not self.websocket.closed
                        ):
                            await self.websocket.close()
                        elif (
                                hasattr(self.websocket, "state")
                                and self.websocket.state.name != "CLOSED"
                        ):
                            await self.websocket.close()
                        else:
                            # Fall back to a direct close attempt.
                            await self.websocket.close()
                    except Exception:
                        # Ignore close failures here.
                        pass
            except Exception as ws_error:
                self.logger.bind(tag=TAG).error(
                    f"Error while closing WebSocket connection: {ws_error}"
                )

            if self.tts:
                await self.tts.close()
            if self.asr:
                await self.asr.close()

            # Shut down the executor last to avoid blocking cleanup.
            if self.executor:
                try:
                    self.executor.shutdown(wait=False)
                except Exception as executor_error:
                    self.logger.bind(tag=TAG).error(
                        f"Error while shutting down executor: {executor_error}"
                    )
                self.executor = None
            self.logger.bind(tag=TAG).info("Connection resources released")
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error while closing connection: {e}")
        finally:
            # Ensure the stop event is always set.
            if self.stop_event:
                self.stop_event.set()

    def clear_queues(self):
        """Drain all task queues owned by this connection."""
        if self.tts:
            self.logger.bind(tag=TAG).debug(
                f"Starting queue cleanup: TTS text queue={self.tts.tts_text_queue.qsize()}, audio queue={self.tts.tts_audio_queue.qsize()}"
            )

            # Drain queues without blocking.
            for q in [
                self.tts.tts_text_queue,
                self.tts.tts_audio_queue,
                self.report_queue,
            ]:
                if not q:
                    continue
                while True:
                    try:
                        q.get_nowait()
                    except queue.Empty:
                        break

            # Reset the audio rate controller and clear its background state.
            if hasattr(self, "audio_rate_controller") and self.audio_rate_controller:
                self.audio_rate_controller.reset()
                self.logger.bind(tag=TAG).debug("Audio rate controller reset")

            self.logger.bind(tag=TAG).debug(
                f"Queue cleanup finished: TTS text queue={self.tts.tts_text_queue.qsize()}, audio queue={self.tts.tts_audio_queue.qsize()}"
            )

    def reset_audio_states(self):
        """
        Reset all audio-related state, including VAD and ASR buffers.
        """
        # Reset VAD states
        self.client_audio_buffer.clear()
        self.client_have_voice = False
        self.client_voice_stop = False
        self.client_voice_window.clear()
        self.last_is_voice = False

        # Clear ASR buffers
        self.asr_audio.clear()

        self.logger.bind(tag=TAG).debug("All audio states reset.")

    def chat_and_close(self, text):
        """Chat with the user and then close the connection"""
        try:
            # Use the existing chat method
            self.chat(text)

            # After chat is complete, close the connection
            self.close_after_chat = True
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Chat and close error: {str(e)}")

    async def _check_timeout(self):
        """Monitor inactivity and close timed-out connections."""
        try:
            while not self.stop_event.is_set():
                last_activity_time = self.last_activity_time
                if self.need_bind:
                    last_activity_time = self.first_activity_time

                # Check timeout only after activity timestamps have been initialized.
                if last_activity_time > 0.0:
                    current_time = time.time() * 1000
                    if current_time - last_activity_time > self.timeout_seconds * 1000:
                        if not self.stop_event.is_set():
                            self.logger.bind(tag=TAG).info(
                                "Connection timed out, preparing to close"
                            )
                            # Set the stop event first to avoid duplicate handling.
                            self.stop_event.set()
                            # Wrap close in try/except so cleanup errors do not block shutdown.
                            try:
                                await self.close(self.websocket)
                            except Exception as close_error:
                                self.logger.bind(tag=TAG).error(
                                    f"Error while closing timed-out connection: {close_error}"
                                )
                        break
                # Check every 10 seconds to avoid excessive polling.
                await asyncio.sleep(10)
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Timeout monitor error: {e}")
        finally:
            self.logger.bind(tag=TAG).info("Timeout monitor exited")

    def _merge_tool_calls(self, tool_calls_list, tools_call):
        """Merge streamed tool-call fragments into a normalized list.

        Args:
            tool_calls_list: Previously collected tool-call entries
            tools_call: Newly received streamed tool-call data
        """
        for tool_call in tools_call:
            tool_index = getattr(tool_call, "index", None)
            if tool_index is None:
                if tool_call.function.name:
                    # A function name means this is a new tool call.
                    tool_index = len(tool_calls_list)
                else:
                    tool_index = len(tool_calls_list) - 1 if tool_calls_list else 0

            # Grow the list if the streamed index points past the current end.
            if tool_index >= len(tool_calls_list):
                tool_calls_list.append({"id": "", "name": "", "arguments": ""})

            # Update the merged tool-call entry.
            if tool_call.id:
                tool_calls_list[tool_index]["id"] = tool_call.id
            if tool_call.function.name:
                tool_calls_list[tool_index]["name"] = tool_call.function.name
            if tool_call.function.arguments:
                tool_calls_list[tool_index]["arguments"] += tool_call.function.arguments
