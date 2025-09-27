import requests
from core.utils.util import check_model_key
from core.providers.tts.base import TTSProviderBase
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class TTSProvider(TTSProviderBase):
    def __init__(self, config, delete_audio_file):
        super().__init__(config, delete_audio_file)
        self.api_key = config.get("api_key")
        self.api_url = config.get("api_url", "https://api.openai.com/v1/audio/speech")
        self.model = config.get("model", "tts-1")
        if config.get("private_voice"):
            self.voice = config.get("private_voice")
        else:
            self.voice = config.get("voice", "alloy")
        self.response_format = config.get("format", "wav")
        self.audio_file_type = config.get("format", "wav")

        # Handle empty string case
        speed = config.get("speed", "1.0")
        self.speed = float(speed) if speed else 1.0

        self.output_file = config.get("output_dir", "tmp/")
        
        logger.debug(
            f"TTS parameters initialized: model={self.model}, voice={self.voice}, format={self.response_format}, speed={self.speed}, api_url={self.api_url}"
        )
        
        model_key_msg = check_model_key("TTS", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)

    async def text_to_speak(self, text, output_file):
        logger.bind(tag=TAG).debug(f"Sending TTS request to OpenAI with model: {self.model}, voice: {self.voice}, text length: {len(text)}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "input": text,
            "voice": self.voice,
            "response_format": "wav",
            "speed": self.speed,
        }
        
        logger.bind(tag=TAG).debug(f"Making OpenAI TTS API request to: {self.api_url}")
        
        response = requests.post(self.api_url, json=data, headers=headers)
        
        logger.bind(tag=TAG).debug(f"Received OpenAI TTS response with status: {response.status_code}")
        
        if response.status_code == 200:
            if output_file:
                logger.bind(tag=TAG).debug(f"Writing TTS audio to file: {output_file}")
                with open(output_file, "wb") as audio_file:
                    audio_file.write(response.content)
                logger.bind(tag=TAG).debug(f"Successfully wrote TTS audio file: {output_file}")
            else:
                logger.bind(tag=TAG).debug(f"Returning TTS audio content directly, size: {len(response.content)} bytes")
                return response.content
        else:
            logger.bind(tag=TAG).error(f"OpenAI TTS request failed: {response.status_code} - {response.text}")
            raise Exception(
                f"OpenAI TTS request failed: {response.status_code} - {response.text}"
            )
