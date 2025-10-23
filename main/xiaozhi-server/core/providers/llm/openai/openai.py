import httpx
import openai
from openai.types import CompletionUsage
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        if "base_url" in config:
            self.base_url = config.get("base_url")
        else:
            self.base_url = config.get("url")
        # Add timeout configuration item, unit is seconds
        timeout = config.get("timeout", 300)
        self.timeout = int(timeout) if timeout else 300

        param_defaults = {
            "max_tokens": (500, int),
            "temperature": (0.7, lambda x: round(float(x), 1)),
            "top_p": (1.0, lambda x: round(float(x), 1)),
            "frequency_penalty": (0, lambda x: round(float(x), 1)),
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
            f"Intent recognition parameters initialized: {self.temperature}, {self.max_tokens}, {self.top_p}, {self.frequency_penalty}"
        )

        model_key_msg = check_model_key("LLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=httpx.Timeout(self.timeout))

    def response(self, session_id, dialogue, **kwargs):
        logger.bind(tag=TAG).debug(f"Sending request to OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
        try:
            responses = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                stream=True,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                frequency_penalty=kwargs.get(
                    "frequency_penalty", self.frequency_penalty
                ),
            )
            logger.bind(tag=TAG).debug(f"Received response from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
            is_active = True
            for chunk in responses:
                logger.bind(tag=TAG).debug(f"Received chunk from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
                try:
                    # Check if there is a valid choice and content is not empty
                    delta = (
                        chunk.choices[0].delta
                        if getattr(chunk, "choices", None)
                        else None
                    )
                    logger.bind(tag=TAG).debug(f"Received delta from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
                    content = delta.content if hasattr(delta, "content") else ""
                    logger.bind(tag=TAG).debug(f"Extracted content from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
                except IndexError:
                    logger.bind(tag=TAG).debug(f"Received index error from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
                    content = ""
                if content:
                    logger.bind(tag=TAG).debug(f"Received content from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
                    # Handle tags spanning multiple chunks
                    if "<think>" in content:
                        is_active = False
                        content = content.split("<think>")[0]
                    if "</think>" in content:
                        is_active = True
                        content = content.split("</think>")[-1]
                    if is_active:
                        logger.bind(tag=TAG).debug(f"Yielding content from OpenAI with model: {self.model_name}, dialogue length: {len(dialogue)}")
                        yield content

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")

    def response_with_functions(self, session_id, dialogue, functions=None):
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name, messages=dialogue, stream=True, tools=functions
            )

            for chunk in stream:
                # Check if there is a valid choice and content is not empty
                if getattr(chunk, "choices", None):
                    yield chunk.choices[0].delta.content, chunk.choices[
                        0
                    ].delta.tool_calls
                # When CompletionUsage message exists, generate Token consumption log
                elif isinstance(getattr(chunk, "usage", None), CompletionUsage):
                    usage_info = getattr(chunk, "usage", None)
                    logger.bind(tag=TAG).info(
                        f"Token consumption: input {getattr(usage_info, 'prompt_tokens', 'unknown')}，"
                        f"output {getattr(usage_info, 'completion_tokens', 'unknown')}，"
                        f"total {getattr(usage_info, 'total_tokens', 'unknown')}"
                    )

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            yield f"【OpenAI service response exception: {e}】", None
