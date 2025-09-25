import os
import time
import base64
from typing import Optional, Tuple, List
from config.logger import setup_logging
from core.providers.asr.dto.dto import InterfaceType
from core.providers.asr.base import ASRProviderBase
from core.utils.util import check_model_key
from google import generativeai as genai
from google.generativeai import types
import requests

TAG = __name__
logger = setup_logging()


class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        super().__init__()
        self.interface_type = InterfaceType.NON_STREAM
        self.api_key = config.get("api_key")
        self.model_name = config.get("model_name")
        self.output_dir = config.get("output_dir")
        self.delete_audio_file = delete_audio_file
        self.http_proxy = config.get("http_proxy")
        self.https_proxy = config.get("https_proxy")
        
        logger.debug(
            f"Gemini ASR parameters initialized: model_name={self.model_name}, output_dir={self.output_dir}, delete_audio_file={self.delete_audio_file}, http_proxy={self.http_proxy}, https_proxy={self.https_proxy}"
        )
        
        model_key_msg = check_model_key("ASR", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
        
        # Configure proxy if provided
        if self.http_proxy or self.https_proxy:
            logger.bind(tag=TAG).info(f"Configuring Gemini ASR proxy settings: HTTP={self.http_proxy}, HTTPS={self.https_proxy}")
            if self.http_proxy:
                os.environ["HTTP_PROXY"] = self.http_proxy
            if self.https_proxy:
                os.environ["HTTPS_PROXY"] = self.https_proxy
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    async def speech_to_text(self, opus_data: List[bytes], session_id: str, audio_format="opus") -> Tuple[Optional[str], Optional[str]]:
        """Convert speech data to text using Gemini API"""
        logger.bind(tag=TAG).debug(f"Sending ASR request to Gemini with model: {self.model_name}, session_id: {session_id}, audio_format: {audio_format}")
        
        file_path = None
        try:
            start_time = time.time()
            
            # Decode audio data
            if audio_format == "pcm":
                pcm_data = opus_data
                logger.bind(tag=TAG).debug(f"Using PCM data directly, length: {len(opus_data)}")
            else:
                logger.bind(tag=TAG).debug(f"Decoding Opus data to PCM")
                pcm_data = self.decode_opus(opus_data)
                logger.bind(tag=TAG).debug(f"Decoded PCM data length: {len(pcm_data) if pcm_data else 0}")
            
            if not pcm_data:
                logger.bind(tag=TAG).warning("Decoded PCM data is empty, cannot perform recognition")
                return "", None
            
            # Save audio file for processing
            file_path = self.save_audio_to_file(pcm_data, session_id)
            logger.bind(tag=TAG).debug(f"Saved audio file: {file_path}")
            
            # Read the audio file and convert to base64
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                logger.bind(tag=TAG).debug(f"Encoded audio to base64, size: {len(audio_base64)} characters")
            
            # Create Gemini model instance
            model = genai.GenerativeModel(self.model_name)
            
            # Prepare the prompt for speech recognition
            prompt = "Please transcribe the following audio file. Return only the transcribed text without any additional commentary or formatting."
            
            # Create content with audio data
            content = [
                prompt,
                {
                    "mime_type": "audio/wav",
                    "data": audio_base64
                }
            ]
            
            logger.bind(tag=TAG).debug(f"Making Gemini ASR API request with model: {self.model_name}")
            
            # Generate content using Gemini
            response = model.generate_content(content)
            
            logger.bind(tag=TAG).debug(f"Received Gemini ASR response")
            
            # Extract text from response
            if response and response.text:
                text = response.text.strip()
                logger.bind(tag=TAG).debug(f"Successfully extracted text from Gemini ASR response: {text}")
                
                # Log processing time
                processing_time = time.time() - start_time
                logger.bind(tag=TAG).debug(f"Gemini ASR processing time: {processing_time:.3f}s")
                
                return text, file_path
            else:
                logger.bind(tag=TAG).warning("Gemini ASR response is empty or invalid")
                return "", file_path
                
        except Exception as e:
            logger.bind(tag=TAG).error(f"Gemini ASR request failed: {e}")
            return "", file_path
        finally:
            # File cleanup logic
            if self.delete_audio_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.bind(tag=TAG).debug(f"Deleted temporary audio file: {file_path}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"File deletion failed: {file_path} | Error: {e}")
