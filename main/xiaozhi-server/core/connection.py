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
from core.handle.reportHandle import report
from core.providers.tts.default import DefaultTTS
from concurrent.futures import ThreadPoolExecutor
from core.utils.dialogue import Message, Dialogue
from core.providers.asr.dto.dto import InterfaceType
from core.handle.textHandle import handleTextMessage
from core.providers.tools.unified_tool_handler import UnifiedToolHandler
from plugins_func.loadplugins import auto_import_modules
from plugins_func.register import Action, ActionResponse
from core.auth import AuthMiddleware, AuthenticationError
from config.config_loader import get_private_config_from_api
from core.providers.tts.dto.dto import ContentType, TTSMessageDTO, SentenceType
from config.logger import setup_logging, build_module_string, create_connection_logger
from config.manage_api_client import DeviceNotFoundException, DeviceBindException
from core.utils.prompt_manager import PromptManager
from core.utils.voiceprint_provider import VoiceprintProvider
from core.utils import textUtils

TAG = __name__

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
        self.server = server  # Save server instance reference

        self.auth = AuthMiddleware(config)
        self.need_bind = False
        self.bind_code = None
        self.read_config_from_api = self.config.get("read_config_from_api", False)

        self.websocket = None
        self.headers = None
        self.device_id = None
        self.client_ip = None
        self.prompt = None
        self.welcome_msg = None
        self.max_output_size = 0
        self.chat_history_conf = 0
        self.audio_format = "opus"

        # Client status related
        self.client_abort = False
        self.client_is_speaking = False
        self.client_listen_mode = "auto"

        # Thread task related
        self.loop = asyncio.get_event_loop()
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Add reporting thread pool
        self.report_queue = queue.Queue()
        self.report_thread = None
        # Future can adjust ASR and TTS reporting by modifying here, currently both enabled by default
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

        # Manage voiceprint recognition separately for each connection
        self.voiceprint_provider = None

        # VAD related variables
        self.client_audio_buffer = bytearray()
        self.client_have_voice = False
        self.last_activity_time = 0.0  # Unified activity timestamp (milliseconds)
        self.client_voice_stop = False
        self.client_voice_window = deque(maxlen=5)
        self.last_is_voice = False

        # ASR related variables
        # Because public local ASR might be used in actual deployment, cannot expose variables to public ASR
        # So ASR-related variables need to be defined here, belonging to connection's private variables
        self.asr_audio = []
        self.asr_audio_queue = queue.Queue()

        # LLM related variables
        self.llm_finish_task = True
        self.dialogue = Dialogue()

        # TTS related variables
        self.sentence_id = None
        # Handle TTS response with no text return
        self.tts_MessageText = ""

        # IoT related variables
        self.iot_descriptors = {}
        self.func_handler = None

        self.cmd_exit = self.config["exit_commands"]

        # Whether to close connection after chat ends
        self.close_after_chat = False
        self.load_function_plugin = False
        self.intent_type = "nointent"

        self.timeout_seconds = (
            int(self.config.get("close_connection_no_voice_time", 120)) + 60
        )  # Add 60 seconds on top of original first-level close for second-level close
        self.timeout_task = None

        # {"mcp":true} indicates MCP functionality is enabled
        self.features = None

        # Mark whether connection is from MQTT
        self.conn_from_mqtt_gateway = False

        # Initialize prompt manager
        self.prompt_manager = PromptManager(config, self.logger)

    async def handle_connection(self, ws):
        try:
            # Get and validate headers
            self.headers = dict(ws.request.headers)

            if self.headers.get("device-id", None) is None:
                # Try to get device-id from URL query parameters
                from urllib.parse import parse_qs, urlparse

                # Get path from WebSocket request
                request_path = ws.request.path
                if not request_path:
                    self.logger.bind(tag=TAG).error("Unable to get request path")
                    return
                parsed_url = urlparse(request_path)
                query_params = parse_qs(parsed_url.query)
                if "device-id" in query_params:
                    self.headers["device-id"] = query_params["device-id"][0]
                    self.headers["client-id"] = query_params["client-id"][0]
                else:
                    await ws.send("Port is normal, please use test_page.html if you need to test connection")
                    await self.close(ws)
                    return
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

            # Perform authentication
            await self.auth.authenticate(self.headers)

            # Authentication passed, continue processing
            self.websocket = ws
            self.device_id = self.headers.get("device-id", None)

            # Check if connection is from MQTT
            request_path = ws.request.path
            self.conn_from_mqtt_gateway = request_path.endswith("?from=mqtt_gateway")
            if self.conn_from_mqtt_gateway:
                self.logger.bind(tag=TAG).info("Connection from: MQTT gateway")

            # Initialize activity timestamp
            self.last_activity_time = time.time() * 1000

            # Start timeout check task
            self.timeout_task = asyncio.create_task(self._check_timeout())

            self.welcome_msg = self.config["xiaozhi"]
            self.welcome_msg["session_id"] = self.session_id

            # Get differentiated configuration
            self._initialize_private_config()
            # Asynchronous initialization
            self.executor.submit(self._initialize_components)

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
                self.logger.bind(tag=TAG).error(f"Error during final cleanup: {final_error}")
                # Ensure connection is closed even if memory save fails
                try:
                    await self.close(ws)
                except Exception as close_error:
                    self.logger.bind(tag=TAG).error(
                        f"Error during forced connection close: {close_error}"
                    )

    async def _save_and_close(self, ws):
        """Save memory and close connection"""
        try:
            if self.memory:
                # Use thread pool to asynchronously save memory
                def save_memory_task():
                    try:
                        # Create new event loop (avoid conflicts with main loop)
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            self.memory.save_memory(self.dialogue.dialogue)
                        )
                    except Exception as e:
                        self.logger.bind(tag=TAG).error(f"Failed to save memory: {e}")
                    finally:
                        try:
                            loop.close()
                        except Exception:
                            pass

                # Start thread to save memory, do not wait for completion
                threading.Thread(target=save_memory_task, daemon=True).start()
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to save memory: {e}")
        finally:
            # Immediately close connection, do not wait for memory save completion
            try:
                await self.close(ws)
            except Exception as close_error:
                self.logger.bind(tag=TAG).error(
                    f"Failed to close connection after saving memory: {close_error}"
                )

    async def _route_message(self, message):
        """Message routing"""
        if isinstance(message, str):
            await handleTextMessage(self, message)
        elif isinstance(message, bytes):
            if self.vad is None or self.asr is None:
                return

            # Process audio packets from MQTT gateway
            if self.conn_from_mqtt_gateway and len(message) >= 16:
                handled = await self._process_mqtt_audio_message(message)
                if handled:
                    return

            # When no header processing needed or no header, directly process raw message
            self.asr_audio_queue.put(message)

    async def _process_mqtt_audio_message(self, message):
        """
        Process audio messages from MQTT gateway, parse 16-byte header and extract audio data

        Args:
            message: Audio message containing header

        Returns:
            bool: Whether message was successfully processed
        """
        try:
            # Extract header information
            timestamp = int.from_bytes(message[8:12], "big")
            audio_length = int.from_bytes(message[12:16], "big")

            # Extract audio data
            if audio_length > 0 and len(message) >= 16 + audio_length:
                # Has specified length, extract precise audio data
                audio_data = message[16 : 16 + audio_length]
                # Sort and process based on timestamp
                self._process_websocket_audio(audio_data, timestamp)
                return True
            elif len(message) > 16:
                # No specified length or invalid length, remove header and process remaining data
                audio_data = message[16:]
                self.asr_audio_queue.put(audio_data)
                return True
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to parse WebSocket audio packet: {e}")

        # Processing failed, return False to indicate need to continue processing
        return False

    def _process_websocket_audio(self, audio_data, timestamp):
        """Process WebSocket format audio packets"""
        # Initialize timestamp sequence management
        if not hasattr(self, "audio_timestamp_buffer"):
            self.audio_timestamp_buffer = {}
            self.last_processed_timestamp = 0
            self.max_timestamp_buffer_size = 20

        # If timestamp is increasing, process directly
        if timestamp >= self.last_processed_timestamp:
            self.asr_audio_queue.put(audio_data)
            self.last_processed_timestamp = timestamp

            # Process subsequent packets in buffer
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
            # Out-of-order packet, temporarily store
            if len(self.audio_timestamp_buffer) < self.max_timestamp_buffer_size:
                self.audio_timestamp_buffer[timestamp] = audio_data
            else:
                self.asr_audio_queue.put(audio_data)

    async def handle_restart(self, message):
        """Handle server restart request"""
        try:

            self.logger.bind(tag=TAG).info("Received server restart command, preparing to execute...")

            # Send confirmation response
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "server",
                        "status": "success",
                        "message": "Server restarting...",
                        "content": {"action": "restart"},
                    }
                )
            )

            # Asynchronously execute restart operation
            def restart_server():
                """Method to actually execute restart"""
                time.sleep(1)
                self.logger.bind(tag=TAG).info("Executing server restart...")
                subprocess.Popen(
                    [sys.executable, "app.py"],
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                    start_new_session=True,
                )
                os._exit(0)

            # Use thread to execute restart to avoid blocking event loop
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
            self.selected_module_str = build_module_string(
                self.config.get("selected_module", {})
            )
            self.logger = create_connection_logger(self.selected_module_str)

            """Initialize components"""
            if self.config.get("prompt") is not None:
                user_prompt = self.config["prompt"]
                # Use quick prompt for initialization
                prompt = self.prompt_manager.get_quick_prompt(user_prompt)
                self.change_system_prompt(prompt)
                self.logger.bind(tag=TAG).info(
                    f"Quick component initialization: prompt successful {prompt[:50]}..."
                )

            """Initialize local components"""
            self.logger.bind(tag=TAG).debug("=== STARTING COMPONENT INITIALIZATION ===")
            
            if self.vad is None:
                self.logger.bind(tag=TAG).debug("Initializing VAD...")
                self.vad = self._vad
                self.logger.bind(tag=TAG).debug(f"VAD initialized: {type(self.vad)}")
            else:
                self.logger.bind(tag=TAG).debug(f"VAD already exists: {type(self.vad)}")
                
            if self.asr is None:
                self.logger.bind(tag=TAG).debug("Initializing ASR...")
                self.asr = self._initialize_asr()
                self.logger.bind(tag=TAG).debug(f"ASR initialized: {type(self.asr)}")
            else:
                self.logger.bind(tag=TAG).debug(f"ASR already exists: {type(self.asr)}")

            # Initialize voiceprint recognition
            self.logger.bind(tag=TAG).debug("Initializing voiceprint recognition...")
            self._initialize_voiceprint()
            self.logger.bind(tag=TAG).debug("Voiceprint recognition initialization completed")

            # Open speech recognition channel
            self.logger.bind(tag=TAG).debug("Opening ASR audio channels...")
            asyncio.run_coroutine_threadsafe(
                self.asr.open_audio_channels(self), self.loop
            )
            self.logger.bind(tag=TAG).debug("ASR audio channels opened successfully")
            
            if self.tts is None:
                self.logger.bind(tag=TAG).debug("TTS is None, initializing...")
                self.tts = self._initialize_tts()
            else:
                self.logger.bind(tag=TAG).debug(f"TTS already exists: {type(self.tts)}")
                
            # Open speech synthesis channel
            self.logger.bind(tag=TAG).debug("Opening TTS audio channels...")
            asyncio.run_coroutine_threadsafe(
                self.tts.open_audio_channels(self), self.loop
            )
            self.logger.bind(tag=TAG).debug("TTS audio channels opened successfully")

            """Load memory"""
            self.logger.bind(tag=TAG).debug("Initializing memory...")
            self._initialize_memory()
            self.logger.bind(tag=TAG).debug("Memory initialization completed")
            
            """Load intent recognition"""
            self.logger.bind(tag=TAG).debug("Initializing intent recognition...")
            self._initialize_intent()
            self.logger.bind(tag=TAG).debug("Intent recognition initialization completed")
            
            """Initialize reporting threads"""
            self.logger.bind(tag=TAG).debug("Initializing report threads...")
            self._init_report_threads()
            self.logger.bind(tag=TAG).debug("Report threads initialization completed")
            
            """Update system prompt"""
            self.logger.bind(tag=TAG).debug("Initializing prompt enhancement...")
            self._init_prompt_enhancement()
            self.logger.bind(tag=TAG).debug("Prompt enhancement initialization completed")
            
            self.logger.bind(tag=TAG).debug("=== COMPONENT INITIALIZATION COMPLETED SUCCESSFULLY ===")

        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Failed to instantiate components: {e}")

    def _init_prompt_enhancement(self):
        # Update context information
        self.prompt_manager.update_context_info(self, self.client_ip)
        enhanced_prompt = self.prompt_manager.build_enhanced_prompt(
            self.config["prompt"], self.device_id, self.client_ip
        )
        if enhanced_prompt:
            self.change_system_prompt(enhanced_prompt)
            self.logger.bind(tag=TAG).info("System prompt has been enhanced and updated")

    def _init_report_threads(self):
        """Initialize ASR and TTS reporting threads"""
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
        """Initialize TTS"""
        self.logger.bind(tag=TAG).debug("Initializing TTS service...")
        tts = None
        if not self.need_bind:
            self.logger.bind(tag=TAG).debug("Calling initialize_tts...")
            tts = initialize_tts(self.config)
            self.logger.bind(tag=TAG).debug(f"initialize_tts returned: {type(tts)}")

        if tts is None:
            self.logger.bind(tag=TAG).debug("Using DefaultTTS fallback...")
            tts = DefaultTTS(self.config, delete_audio_file=True)

        self.logger.bind(tag=TAG).debug(f"TTS service initialized: {type(tts)}")
        return tts

    def _initialize_asr(self):
        """Initialize ASR"""
        if self._asr.interface_type == InterfaceType.LOCAL:
            # If public ASR is local service, return directly
            # Because local ASR instance can be shared by multiple connections
            asr = self._asr
        else:
            # If public ASR is remote service, initialize a new instance
            # Because remote ASR involves websocket connections and receiving threads, each connection needs an instance
            asr = initialize_asr(self.config)

        return asr

    def _initialize_voiceprint(self):
        """Initialize voiceprint recognition for current connection"""
        try:
            voiceprint_config = self.config.get("voiceprint", {})
            if voiceprint_config:
                voiceprint_provider = VoiceprintProvider(voiceprint_config)
                if voiceprint_provider is not None and voiceprint_provider.enabled:
                    self.voiceprint_provider = voiceprint_provider
                    self.logger.bind(tag=TAG).info("Voiceprint recognition feature dynamically enabled at connection time")
                else:
                    self.logger.bind(tag=TAG).warning("Voiceprint recognition feature enabled but configuration incomplete")
            else:
                self.logger.bind(tag=TAG).info("Voiceprint recognition feature not enabled")
        except Exception as e:
            self.logger.bind(tag=TAG).warning(f"Voiceprint recognition initialization failed: {str(e)}")

    def _initialize_private_config(self):
        """If obtained from config file, perform secondary instantiation"""
        if not self.read_config_from_api:
            return
        """Get differentiated configuration from API for secondary instantiation, not full re-instantiation"""
        try:
            begin_time = time.time()
            private_config = get_private_config_from_api(
                self.config,
                self.headers.get("device-id"),
                self.headers.get("client-id", self.headers.get("device-id")),
            )
            private_config["delete_audio"] = bool(self.config.get("delete_audio", True))
            self.logger.bind(tag=TAG).info(
                f"{time.time() - begin_time} seconds, successfully obtained differentiated configuration: {json.dumps(filter_sensitive_info(private_config), ensure_ascii=False)}"
            )
        except DeviceNotFoundException as e:
            self.need_bind = True
            private_config = {}
        except DeviceBindException as e:
            self.need_bind = True
            self.bind_code = e.bind_code
            private_config = {}
        except Exception as e:
            self.need_bind = True
            self.logger.bind(tag=TAG).error(f"Failed to get differentiated configuration: {e}")
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
            # Load plugin configuration
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
        # Get voiceprint information
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
        try:
            modules = initialize_modules(
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
            self.logger.bind(tag=TAG).error(f"Failed to initialize components: {e}")
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
        self.logger.bind(tag=TAG).debug("Starting memory initialization...")
        if self.memory is None:
            self.logger.bind(tag=TAG).debug("Memory is None, skipping initialization")
            return
        """Initialize memory module"""
        self.logger.bind(tag=TAG).debug("Calling memory.init_memory...")
        self.memory.init_memory(
            role_id=self.device_id,
            llm=self.llm,
            summary_memory=self.config.get("summaryMemory", None),
            save_to_file=not self.read_config_from_api,
        )
        self.logger.bind(tag=TAG).debug("Memory init_memory completed")

        # Get memory summary configuration
        self.logger.bind(tag=TAG).debug("Getting memory configuration...")
        memory_config = self.config["Memory"]
        memory_type = self.config["Memory"][self.config["selected_module"]["Memory"]][
            "type"
        ]
        self.logger.bind(tag=TAG).debug(f"Memory type: {memory_type}")
        # If using nomen, return directly
        if memory_type == "nomem":
            return
        # Use mem_local_short mode
        elif memory_type == "mem_local_short":
            memory_llm_name = memory_config[self.config["selected_module"]["Memory"]][
                "llm"
            ]
            if memory_llm_name and memory_llm_name in self.config["LLM"]:
                # If dedicated LLM is configured, create independent LLM instance
                from core.utils import llm as llm_utils

                memory_llm_config = self.config["LLM"][memory_llm_name]
                memory_llm_type = memory_llm_config.get("type", memory_llm_name)
                memory_llm = llm_utils.create_instance(
                    memory_llm_type, memory_llm_config
                )
                self.logger.bind(tag=TAG).info(
                    f"Created dedicated LLM for memory summary: {memory_llm_name}, type: {memory_llm_type}"
                )
                self.memory.set_llm(memory_llm)
            else:
                # Otherwise use main LLM
                self.memory.set_llm(self.llm)
                self.logger.bind(tag=TAG).info("Using main LLM as intent recognition model")

    def _initialize_intent(self):
        self.logger.bind(tag=TAG).debug("Starting intent initialization...")
        if self.intent is None:
            self.logger.bind(tag=TAG).debug("Intent is None, skipping initialization")
            return
        self.logger.bind(tag=TAG).debug("Getting intent type from config...")
        self.intent_type = self.config["Intent"][
            self.config["selected_module"]["Intent"]
        ]["type"]
        self.logger.bind(tag=TAG).debug(f"Intent type: {self.intent_type}")
        if self.intent_type == "function_call" or self.intent_type == "intent_llm":
            self.logger.bind(tag=TAG).debug("Setting load_function_plugin = True")
            self.load_function_plugin = True
        """Initialize intent recognition module"""
        # Get intent recognition configuration
        self.logger.bind(tag=TAG).debug("Getting intent configuration...")
        intent_config = self.config["Intent"]
        intent_type = self.config["Intent"][self.config["selected_module"]["Intent"]][
            "type"
        ]
        self.logger.bind(tag=TAG).debug(f"Intent type from config: {intent_type}")

        # If using nointent, return directly
        if intent_type == "nointent":
            self.logger.bind(tag=TAG).debug("Intent type is nointent, returning early")
            return
        # Use intent_llm mode
        elif intent_type == "intent_llm":
            intent_llm_name = intent_config[self.config["selected_module"]["Intent"]][
                "llm"
            ]

            if intent_llm_name and intent_llm_name in self.config["LLM"]:
                # If dedicated LLM is configured, create independent LLM instance
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
                # Otherwise use main LLM
                self.intent.set_llm(self.llm)
                self.logger.bind(tag=TAG).info("Using main LLM as intent recognition model")

        """Load unified tool handler"""
        self.func_handler = UnifiedToolHandler(self)

        # Asynchronously initialize tool handler
        if hasattr(self, "loop") and self.loop:
            asyncio.run_coroutine_threadsafe(self.func_handler._initialize(), self.loop)

    def change_system_prompt(self, prompt):
        self.prompt = prompt
        # Update system prompt to context
        self.dialogue.update_system_message(self.prompt)

    def chat(self, query, depth=0):
        self.logger.bind(tag=TAG).info(f"LLM received user message: {query}")
        self.logger.bind(tag=TAG).debug(f"Chat method called with depth={depth}, intent_type={self.intent_type}")
        self.llm_finish_task = False
        self.logger.bind(tag=TAG).debug("Step 1: Set llm_finish_task = False")

        # Create new session ID and send FIRST request for top level
        if depth == 0:
            self.logger.bind(tag=TAG).debug("Step 2: Creating session ID...")
            self.sentence_id = str(uuid.uuid4().hex)
            self.logger.bind(tag=TAG).debug(f"Step 3: Session ID created: {self.sentence_id}")
            self.dialogue.put(Message(role="user", content=query))
            self.logger.bind(tag=TAG).debug("Step 4: Message added to dialogue")
            try:
                self.tts.tts_text_queue.put(
                    TTSMessageDTO(
                        sentence_id=self.sentence_id,
                        sentence_type=SentenceType.FIRST,
                        content_type=ContentType.ACTION,
                    ),
                    timeout=5.0  # 5 second timeout
                )
                self.logger.bind(tag=TAG).debug("Step 5: FIRST TTS message added to queue")
            except Exception as e:
                self.logger.bind(tag=TAG).error(f"Step 5 FAILED: TTS queue put failed: {e}")
                # Continue without TTS to prevent hanging

        # Define intent functions
        functions = None
        self.logger.bind(tag=TAG).debug("Step 6: Checking functions...")
        if self.intent_type == "function_call" and hasattr(self, "func_handler"):
            functions = self.func_handler.get_functions()
            self.logger.bind(tag=TAG).debug(f"Functions loaded: {len(functions) if functions else 0}")
        else:
            self.logger.bind(tag=TAG).debug(f"No functions - intent_type={self.intent_type}, has_func_handler={hasattr(self, 'func_handler')}")
        response_message = []
        self.logger.bind(tag=TAG).debug("Step 7: Functions check completed")

        try:
            # Use dialogue with memory
            memory_str = None
            self.logger.bind(tag=TAG).debug("Step 8: Checking memory...")
            if self.memory is not None:
                self.logger.bind(tag=TAG).debug("Step 9: Querying memory...")
                future = asyncio.run_coroutine_threadsafe(
                    self.memory.query_memory(query), self.loop
                )
                memory_str = future.result()
                self.logger.bind(tag=TAG).debug(f"Memory query completed, result length: {len(memory_str) if memory_str else 0}")
            else:
                self.logger.bind(tag=TAG).debug("No memory provider available")
            self.logger.bind(tag=TAG).debug("Step 10: Memory check completed")

            # Prepare dialogue data
            self.logger.bind(tag=TAG).debug("Step 11: Preparing dialogue data...")
            dialogue_data = self.dialogue.get_llm_dialogue_with_memory(
                memory_str, self.config.get("voiceprint", {})
            )
            self.logger.bind(tag=TAG).debug(f"Step 12: Dialogue data prepared with {len(dialogue_data)} messages")

            if self.intent_type == "function_call" and functions is not None:
                # Use streaming interface that supports functions
                self.logger.bind(tag=TAG).debug("Step 13: Calling LLM with functions...")
                llm_responses = self.llm.response_with_functions(
                    self.session_id,
                    dialogue_data,
                    functions=functions,
                )
            else:
                # Use regular streaming interface
                self.logger.bind(tag=TAG).debug("Step 14: Calling LLM without functions...")
                llm_responses = self.llm.response(
                    self.session_id,
                    dialogue_data,
                )
            self.logger.bind(tag=TAG).debug("Step 15: LLM call completed, starting to process responses...")
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"LLM processing error {query}: {e}")
            return None

        # Process streaming response
        tool_call_flag = False
        function_name = None
        function_id = None
        function_arguments = ""
        content_arguments = ""
        self.client_abort = False
        emotion_flag = True
        self.logger.bind(tag=TAG).debug("Starting to iterate over LLM responses...")
        response_count = 0
        for response in llm_responses:
            response_count += 1
            self.logger.bind(tag=TAG).debug(f"Processing response #{response_count}: {type(response)}")
            if self.client_abort:
                self.logger.bind(tag=TAG).debug(f"Client aborted, breaking out of loop")
                break
            if self.intent_type == "function_call" and functions is not None:
                self.logger.bind(tag=TAG).debug(f"Processing function call: {response}")
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
                    if tools_call[0].id is not None:
                        function_id = tools_call[0].id
                    if tools_call[0].function.name is not None:
                        function_name = tools_call[0].function.name
                    if tools_call[0].function.arguments is not None:
                        function_arguments += tools_call[0].function.arguments
            else:
                self.logger.bind(tag=TAG).debug(f"Processing response: {response}")
                content = response

            # Get emotion expression from LLM response, only get once at the beginning of each conversation round
            if emotion_flag and content is not None and content.strip():
                asyncio.run_coroutine_threadsafe(
                    textUtils.get_emotion(self, content),
                    self.loop,
                )
                emotion_flag = False

            if content is not None and len(content) > 0:
                self.logger.bind(tag=TAG).debug(f"Processing content: '{content[:50]}...' (length: {len(content)})")
                if not tool_call_flag:
                    response_message.append(content)
                    self.logger.bind(tag=TAG).debug("Adding content to TTS queue...")
                    try:
                        self.tts.tts_text_queue.put(
                            TTSMessageDTO(
                                sentence_id=self.sentence_id,
                                sentence_type=SentenceType.MIDDLE,
                                content_type=ContentType.TEXT,
                                content_detail=content,
                            ),
                            timeout=5.0  # 5 second timeout
                        )
                        self.logger.bind(tag=TAG).debug("Content added to TTS queue successfully")
                    except Exception as e:
                        self.logger.bind(tag=TAG).error(f"TTS queue put failed for content: {e}")
                        # Continue without TTS to prevent hanging
        # Process function call
        if tool_call_flag:
            bHasError = False
            if function_id is None:
                a = extract_json_from_string(content_arguments)
                if a is not None:
                    try:
                        content_arguments_json = json.loads(a)
                        function_name = content_arguments_json["name"]
                        function_arguments = json.dumps(
                            content_arguments_json["arguments"], ensure_ascii=False
                        )
                        function_id = str(uuid.uuid4().hex)
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
            if not bHasError:
                # If LLM needs to process first, add relevant processing log situation
                if len(response_message) > 0:
                    text_buff = "".join(response_message)
                    self.tts_MessageText = text_buff
                    self.dialogue.put(Message(role="assistant", content=text_buff))
                response_message.clear()
                self.logger.bind(tag=TAG).debug(
                    f"function_name={function_name}, function_id={function_id}, function_arguments={function_arguments}"
                )
                function_call_data = {
                    "name": function_name,
                    "id": function_id,
                    "arguments": function_arguments,
                }

                # Use unified tool handler to process all tool calls
                result = asyncio.run_coroutine_threadsafe(
                    self.func_handler.handle_llm_function_call(
                        self, function_call_data
                    ),
                    self.loop,
                ).result()
                self._handle_function_result(result, function_call_data, depth=depth)

        # Store dialogue content
        if len(response_message) > 0:
            text_buff = "".join(response_message)
            self.tts_MessageText = text_buff
            self.dialogue.put(Message(role="assistant", content=text_buff))
        if depth == 0:
            self.logger.bind(tag=TAG).debug("Adding LAST TTS message to queue...")
            try:
                self.tts.tts_text_queue.put(
                    TTSMessageDTO(
                        sentence_id=self.sentence_id,
                        sentence_type=SentenceType.LAST,
                        content_type=ContentType.ACTION,
                    ),
                    timeout=5.0  # 5 second timeout
                )
                self.logger.bind(tag=TAG).debug("LAST TTS message added to queue successfully")
            except Exception as e:
                self.logger.bind(tag=TAG).error(f"LAST TTS queue put failed: {e}")
                # Continue without TTS to prevent hanging
        self.llm_finish_task = True
        self.logger.bind(tag=TAG).debug(f"Chat method completed successfully. Total responses processed: {response_count}")
        # Use lambda for lazy evaluation, only execute get_llm_dialogue() at DEBUG level
        self.logger.bind(tag=TAG).debug(
            lambda: json.dumps(
                self.dialogue.get_llm_dialogue(), indent=4, ensure_ascii=False
            )
        )

        return True

    def _handle_function_result(self, result, function_call_data, depth):
        if result.action == Action.RESPONSE:  # Direct response to frontend
            text = result.response
            self.tts.tts_one_sentence(self, ContentType.TEXT, content_detail=text)
            self.dialogue.put(Message(role="assistant", content=text))
        elif result.action == Action.REQLLM:  # Call function then request LLM to generate response
            text = result.result
            if text is not None and len(text) > 0:
                function_id = function_call_data["id"]
                function_name = function_call_data["name"]
                function_arguments = function_call_data["arguments"]
                self.dialogue.put(
                    Message(
                        role="assistant",
                        tool_calls=[
                            {
                                "id": function_id,
                                "function": {
                                    "arguments": (
                                        "{}"
                                        if function_arguments == ""
                                        else function_arguments
                                    ),
                                    "name": function_name,
                                },
                                "type": "function",
                                "index": 0,
                            }
                        ],
                    )
                )

                self.dialogue.put(
                    Message(
                        role="tool",
                        tool_call_id=(
                            str(uuid.uuid4()) if function_id is None else function_id
                        ),
                        content=text,
                    )
                )
                self.chat(text, depth=depth + 1)
        elif result.action == Action.NOTFOUND or result.action == Action.ERROR:
            text = result.response if result.response else result.result
            self.tts.tts_one_sentence(self, ContentType.TEXT, content_detail=text)
            self.dialogue.put(Message(role="assistant", content=text))
        else:
            pass

    def _report_worker(self):
        """Chat record reporting worker thread"""
        while not self.stop_event.is_set():
            try:
                # Get data from queue, set timeout to periodically check stop event
                item = self.report_queue.get(timeout=1)
                if item is None:  # Detect poison pill object
                    break
                try:
                    # Check thread pool status
                    if self.executor is None:
                        continue
                    # Submit task to thread pool
                    self.executor.submit(self._process_report, *item)
                except Exception as e:
                    self.logger.bind(tag=TAG).error(f"Chat record reporting thread exception: {e}")
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.bind(tag=TAG).error(f"Chat record reporting worker thread exception: {e}")

        self.logger.bind(tag=TAG).info("Chat record reporting thread has exited")

    def _process_report(self, type, text, audio_data, report_time):
        """Process reporting task"""
        try:
            # Execute reporting (pass binary data)
            report(self, type, text, audio_data, report_time)
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Reporting processing exception: {e}")
        finally:
            # Mark task completion
            self.report_queue.task_done()

    def clearSpeakStatus(self):
        self.client_is_speaking = False
        self.logger.bind(tag=TAG).debug(f"Clear server speaking status")

    async def close(self, ws=None):
        """Resource cleanup method"""
        try:
            # Clean audio buffer
            if hasattr(self, "audio_buffer"):
                self.audio_buffer.clear()

            # Cancel timeout task
            if self.timeout_task and not self.timeout_task.done():
                self.timeout_task.cancel()
                try:
                    await self.timeout_task
                except asyncio.CancelledError:
                    pass
                self.timeout_task = None

            # Clean tool handler resources
            if hasattr(self, "func_handler") and self.func_handler:
                try:
                    await self.func_handler.cleanup()
                except Exception as cleanup_error:
                    self.logger.bind(tag=TAG).error(
                        f"Error cleaning tool handler: {cleanup_error}"
                    )

            # Trigger stop event
            if self.stop_event:
                self.stop_event.set()

            # Clear task queue
            self.clear_queues()

            # Close WebSocket connection
            try:
                if ws:
                    # Safely check WebSocket status and close
                    try:
                        if hasattr(ws, "closed") and not ws.closed:
                            await ws.close()
                        elif hasattr(ws, "state") and ws.state.name != "CLOSED":
                            await ws.close()
                        else:
                            # If no closed attribute, directly try to close
                            await ws.close()
                    except Exception:
                        # If close fails, ignore error
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
                            # If no closed attribute, directly try to close
                            await self.websocket.close()
                    except Exception:
                        # If close fails, ignore error
                        pass
            except Exception as ws_error:
                self.logger.bind(tag=TAG).error(f"Error closing WebSocket connection: {ws_error}")

            if self.tts:
                await self.tts.close()

            # Finally close thread pool (avoid blocking)
            if self.executor:
                try:
                    self.executor.shutdown(wait=False)
                except Exception as executor_error:
                    self.logger.bind(tag=TAG).error(
                        f"Error closing thread pool: {executor_error}"
                    )
                self.executor = None

            self.logger.bind(tag=TAG).info("Connection resources released")
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error closing connection: {e}")
        finally:
            # Ensure stop event is set
            if self.stop_event:
                self.stop_event.set()

    def clear_queues(self):
        """Clear all task queues"""
        if self.tts:
            self.logger.bind(tag=TAG).debug(
                f"Starting cleanup: TTS queue size={self.tts.tts_text_queue.qsize()}, audio queue size={self.tts.tts_audio_queue.qsize()}"
            )

            # Use non-blocking method to clear queues
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

            self.logger.bind(tag=TAG).debug(
                f"Cleanup completed: TTS queue size={self.tts.tts_text_queue.qsize()}, audio queue size={self.tts.tts_audio_queue.qsize()}"
            )

    def reset_vad_states(self):
        self.client_audio_buffer = bytearray()
        self.client_have_voice = False
        self.client_voice_stop = False
        self.logger.bind(tag=TAG).debug("VAD states reset.")

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
        """Check connection timeout"""
        try:
            while not self.stop_event.is_set():
                # Check if timeout (only when timestamp is initialized)
                if self.last_activity_time > 0.0:
                    current_time = time.time() * 1000
                    if (
                        current_time - self.last_activity_time
                        > self.timeout_seconds * 1000
                    ):
                        if not self.stop_event.is_set():
                            self.logger.bind(tag=TAG).info("Connection timeout, preparing to close")
                            # Set stop event to prevent duplicate processing
                            self.stop_event.set()
                            # Use try-except to wrap close operation, ensure it won't block due to exceptions
                            try:
                                await self.close(self.websocket)
                            except Exception as close_error:
                                self.logger.bind(tag=TAG).error(
                                    f"Error closing connection due to timeout: {close_error}"
                                )
                        break
                # Check every 10 seconds to avoid being too frequent
                await asyncio.sleep(10)
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Timeout check task error: {e}")
        finally:
            self.logger.bind(tag=TAG).info("Timeout check task exited")
