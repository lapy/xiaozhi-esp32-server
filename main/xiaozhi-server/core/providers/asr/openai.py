import time
import os
from config.logger import setup_logging
from typing import Optional, Tuple, List
from core.providers.asr.dto.dto import InterfaceType
from core.providers.asr.base import ASRProviderBase

import requests

TAG = __name__
logger = setup_logging()

class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        self.interface_type = InterfaceType.NON_STREAM
        self.api_key = config.get("api_key")
        self.api_url = config.get("base_url")
        self.model = config.get("model_name")        
        self.output_dir = config.get("output_dir")
        self.delete_audio_file = delete_audio_file

        logger.debug(
            f"ASR parameters initialized: model={self.model}, api_url={self.api_url}, output_dir={self.output_dir}, delete_audio_file={self.delete_audio_file}"
        )

        os.makedirs(self.output_dir, exist_ok=True)

    async def speech_to_text(self, opus_data: List[bytes], session_id: str, audio_format="opus") -> Tuple[Optional[str], Optional[str]]:
        logger.bind(tag=TAG).debug(f"Sending ASR request to OpenAI with model: {self.model}, session_id: {session_id}, audio_format: {audio_format}")
        
        file_path = None
        try:
            start_time = time.time()
            if audio_format == "pcm":
                pcm_data = opus_data
                logger.bind(tag=TAG).debug(f"Using PCM data directly, length: {len(opus_data)}")
            else:
                logger.bind(tag=TAG).debug(f"Decoding Opus data to PCM")
                pcm_data = self.decode_opus(opus_data)
                logger.bind(tag=TAG).debug(f"Decoded PCM data length: {len(pcm_data) if pcm_data else 0}")
                
            file_path = self.save_audio_to_file(pcm_data, session_id)

            logger.bind(tag=TAG).debug(
                f"Audio file save time: {time.time() - start_time:.3f}s | Path: {file_path}"
            )

            logger.bind(tag=TAG).info(f"file path: {file_path}")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            
            # Use data parameter to pass model name
            data = {
                "model": self.model
            }

            logger.bind(tag=TAG).debug(f"Making OpenAI ASR API request to: {self.api_url}")

            with open(file_path, "rb") as audio_file:  # Use with statement to ensure file is closed
                files = {
                    "file": audio_file
                }

                start_time = time.time()
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    headers=headers
                )
                logger.bind(tag=TAG).debug(
                    f"Speech recognition time: {time.time() - start_time:.3f}s | Status: {response.status_code} | Result: {response.text}"
                )

            if response.status_code == 200:
                text = response.json().get("text", "")
                logger.bind(tag=TAG).debug(f"Successfully extracted text from OpenAI ASR response: {text}")
                return text, file_path
            else:
                logger.bind(tag=TAG).error(f"OpenAI ASR API request failed: {response.status_code} - {response.text}")
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"Speech recognition failed: {e}")
            return "", None
        finally:
            # File cleanup logic
            if self.delete_audio_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.bind(tag=TAG).debug(f"Deleted temporary audio file: {file_path}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"File deletion failed: {file_path} | Error: {e}")
        
