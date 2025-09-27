import openai
import json
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.vllm.base import VLLMProviderBase

TAG = __name__
logger = setup_logging()


class VLLMProvider(VLLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        if "base_url" in config:
            self.base_url = config.get("base_url")
        else:
            self.base_url = config.get("url")

        param_defaults = {
            "max_tokens": (500, int),
            "temperature": (0.7, lambda x: round(float(x), 1)),
            "top_p": (1.0, lambda x: round(float(x), 1)),
        }

        for param, (default, converter) in param_defaults.items():
            value = config.get(param)
            try:
                setattr(
                    self,
                    param,
                    converter(value) if value not in (None, "") else default,
                )
            except (ValueError, TypeError):
                setattr(self, param, default)

        logger.debug(
            f"VLLM parameters initialized: model_name={self.model_name}, base_url={self.base_url}, max_tokens={self.max_tokens}, temperature={self.temperature}, top_p={self.top_p}"
        )

        model_key_msg = check_model_key("VLLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def response(self, question, base64_image):
        logger.bind(tag=TAG).debug(f"Sending VLLM vision request with model: {self.model_name}, question length: {len(question)}, image size: {len(base64_image) if base64_image else 0}")
        
        question = question + "(Please reply in English)"
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]

            logger.bind(tag=TAG).debug(f"Making VLLM API request to: {self.base_url}")

            response = self.client.chat.completions.create(
                model=self.model_name, messages=messages, stream=False
            )

            logger.bind(tag=TAG).debug(f"Received VLLM response with model: {self.model_name}")
            
            result = response.choices[0].message.content
            logger.bind(tag=TAG).debug(f"Extracted VLLM response content: {result[:100]}..." if len(result) > 100 else f"Extracted VLLM response content: {result}")
            
            return result

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in VLLM response generation: {e}")
            raise
