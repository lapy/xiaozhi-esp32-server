import os
import json
import time
from typing import Optional, Tuple, List
from .base import ASRProviderBase
from config.logger import setup_logging
from core.providers.asr.dto.dto import InterfaceType
import vosk

TAG = __name__
logger = setup_logging()

class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool = True):
        super().__init__()
        self.interface_type = InterfaceType.LOCAL
        self.model_path = config.get("model_path")
        self.output_dir = config.get("output_dir", "tmp/")
        self.delete_audio_file = delete_audio_file
        
        logger.debug(
            f"Vosk ASR parameters initialized: model_path={self.model_path}, output_dir={self.output_dir}, delete_audio_file={self.delete_audio_file}"
        )
        
        # Initialize VOSK model
        self.model = None
        self.recognizer = None
        self._load_model()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_model(self):
        """Load VOSK model"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"VOSK model path does not exist: {self.model_path}")
                
            logger.bind(tag=TAG).info(f"Loading VOSK model: {self.model_path}")
            self.model = vosk.Model(self.model_path)

            # Initialize VOSK recognizer (sample rate must be 16kHz)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

            logger.bind(tag=TAG).info("VOSK model loaded successfully")
        except Exception as e:
            logger.bind(tag=TAG).error(f"Failed to load VOSK model: {e}")
            raise

    async def speech_to_text(
        self, audio_data: List[bytes], session_id: str, audio_format: str = "opus"
    ) -> Tuple[Optional[str], Optional[str]]:
        """Convert speech data to text"""
        logger.bind(tag=TAG).debug(f"Sending Vosk ASR request with session_id: {session_id}, audio_format: {audio_format}")
        
        file_path = None
        try:
            # Check if model loaded successfully
            if not self.model:
                logger.bind(tag=TAG).error("VOSK model not loaded, cannot perform recognition")
                return "", None

            # Decode audio (if original format is Opus)
            if audio_format == "pcm":
                pcm_data = audio_data
                logger.bind(tag=TAG).debug(f"Using PCM data directly, length: {len(audio_data)}")
            else:
                logger.bind(tag=TAG).debug(f"Decoding Opus data to PCM")
                pcm_data = self.decode_opus(audio_data)
                logger.bind(tag=TAG).debug(f"Decoded PCM data length: {len(pcm_data) if pcm_data else 0}")
                
            if not pcm_data:
                logger.bind(tag=TAG).warning("Decoded PCM data is empty, cannot perform recognition")
                return "", None
                
            # Merge PCM data
            combined_pcm_data = b"".join(pcm_data)
            if len(combined_pcm_data) == 0:
                logger.bind(tag=TAG).warning("Merged PCM data is empty")
                return "", None

            logger.bind(tag=TAG).debug(f"Merged PCM data size: {len(combined_pcm_data)} bytes")

            # Determine whether to save as WAV file
            if not self.delete_audio_file:
                file_path = self.save_audio_to_file(pcm_data, session_id)
                logger.bind(tag=TAG).debug(f"Saved audio file: {file_path}")

            start_time = time.time()
            
            logger.bind(tag=TAG).debug(f"Starting Vosk speech recognition")
            
            # Perform recognition (VOSK recommends sending 2000 bytes of data each time)
            chunk_size = 2000
            text_result = ""
            chunk_count = 0
            
            for i in range(0, len(combined_pcm_data), chunk_size):
                chunk = combined_pcm_data[i:i+chunk_size]
                chunk_count += 1
                if self.recognizer.AcceptWaveform(chunk):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '')
                    if text:
                        text_result += text + " "
                        logger.bind(tag=TAG).debug(f"Vosk recognized text chunk {chunk_count}: {text}")
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            final_text = final_result.get('text', '')
            if final_text:
                text_result += final_text
                logger.bind(tag=TAG).debug(f"Vosk final result: {final_text}")
            
            logger.bind(tag=TAG).debug(
                f"VOSK speech recognition time: {time.time() - start_time:.3f}s | Processed {chunk_count} chunks | Result: {text_result.strip()}"
            )
            
            return text_result.strip(), file_path
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"VOSK speech recognition failed: {e}")
            return "", None
        finally:
            # File cleanup logic
            if self.delete_audio_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.bind(tag=TAG).debug(f"Deleted temporary audio file: {file_path}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"File deletion failed: {file_path} | Error: {e}")
