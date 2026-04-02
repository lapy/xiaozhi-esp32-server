from config.logger import setup_logging
from openai import OpenAI
import json
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.base_url = config.get("base_url", "http://localhost:11434")
        # Initialize OpenAI client with Ollama base URL.
        # Ensure the base URL ends with /v1 for OpenAI-compatible API.
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url}/v1"

        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama",  # Ollama doesn't need an API key but OpenAI client requires one
        )

    def response(self, session_id, dialogue, **kwargs):
        responses = self.client.chat.completions.create(
            model=self.model_name, messages=dialogue, stream=True
        )
        is_active = True
        # Track tags across chunks
        buffer = ""

        for chunk in responses:
            try:
                delta = (
                    chunk.choices[0].delta
                    if getattr(chunk, "choices", None)
                    else None
                )
                content = delta.content if hasattr(delta, "content") else ""

                if content:
                    # Append content to buffer
                    buffer += content

                    # Strip tag segments in buffer
                    while "<think>" in buffer and "</think>" in buffer:
                        # Remove full <think></think> tags
                        pre = buffer.split("<think>", 1)[0]
                        post = buffer.split("</think>", 1)[1]
                        buffer = pre + post

                    # Handle start tag only
                    if "<think>" in buffer:
                        is_active = False
                        buffer = buffer.split("<think>", 1)[0]

                    # Handle end tag only
                    if "</think>" in buffer:
                        is_active = True
                        buffer = buffer.split("</think>", 1)[1]

                    # Emit buffered content when active
                    if is_active and buffer:
                        yield buffer
                        buffer = ""  # Clear buffer

            except Exception as e:
                logger.bind(tag=TAG).error(f"Error processing chunk: {e}")

    def response_with_functions(self, session_id, dialogue, functions=None):
        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=dialogue,
            stream=True,
            tools=functions,
        )

        is_active = True
        buffer = ""

        for chunk in stream:
            try:
                delta = (
                    chunk.choices[0].delta
                    if getattr(chunk, "choices", None)
                    else None
                )
                content = delta.content if hasattr(delta, "content") else None
                tool_calls = (
                    delta.tool_calls if hasattr(delta, "tool_calls") else None
                )

                # Pass through tool calls
                if tool_calls:
                    yield None, tool_calls
                    continue

                # Process text content
                if content:
                    # Append content to buffer
                    buffer += content

                    # Strip tag segments in buffer
                    while "<think>" in buffer and "</think>" in buffer:
                        # Remove full <think></think> tags
                        pre = buffer.split("<think>", 1)[0]
                        post = buffer.split("</think>", 1)[1]
                        buffer = pre + post

                    # Handle start tag only
                    if "<think>" in buffer:
                        is_active = False
                        buffer = buffer.split("<think>", 1)[0]

                    # Handle end tag only
                    if "</think>" in buffer:
                        is_active = True
                        buffer = buffer.split("</think>", 1)[1]

                    # Emit buffered content when active
                    if is_active and buffer:
                        yield buffer, None
                        buffer = ""  # Clear buffer
            except Exception as e:
                logger.bind(tag=TAG).error(f"Error processing function chunk: {e}")
                continue
