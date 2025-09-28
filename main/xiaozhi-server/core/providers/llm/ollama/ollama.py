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
        # Initialize OpenAI client with Ollama base URL
        # Add v1 if not present
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url}/v1"

        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama",  # Ollama doesn't need an API key but OpenAI client requires one
        )

        # Check if it's a specific model that needs special handling
        self.needs_special_handling = self.model_name and self.model_name.lower().startswith("qwen3")

        logger.debug(
            f"Intent recognition parameters initialized: model_name={self.model_name}, base_url={self.base_url}, needs_special_handling={self.needs_special_handling}"
        )

    def response(self, session_id, dialogue, **kwargs):
        logger.bind(tag=TAG).debug(f"Sending request to Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
        try:
            # If it's a specific model, add /no_think instruction to user's last message
            if self.needs_special_handling:
                # Copy dialogue list to avoid modifying original dialogue
                dialogue_copy = dialogue.copy()

                # Find the last user message
                for i in range(len(dialogue_copy) - 1, -1, -1):
                    if dialogue_copy[i]["role"] == "user":
                        # Add /no_think instruction before user message
                        dialogue_copy[i]["content"] = (
                            "/no_think " + dialogue_copy[i]["content"]
                        )
                        logger.bind(tag=TAG).debug(f"Added /no_think instruction for specific model")
                        break

                # Use modified dialogue
                dialogue = dialogue_copy

            responses = self.client.chat.completions.create(
                model=self.model_name, messages=dialogue, stream=True
            )
            logger.bind(tag=TAG).debug(f"Received response from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
            is_active = True
            # Used to handle cross-chunk tags
            buffer = ""

            for chunk in responses:
                logger.bind(tag=TAG).debug(f"Received chunk from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                try:
                    delta = (
                        chunk.choices[0].delta
                        if getattr(chunk, "choices", None)
                        else None
                    )
                    logger.bind(tag=TAG).debug(f"Received delta from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                    content = delta.content if hasattr(delta, "content") else ""
                    logger.bind(tag=TAG).debug(f"Extracted content from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")

                    if content:
                        # Add content to buffer
                        buffer += content

                        # Process tags in buffer
                        while "<think>" in buffer and "</think>" in buffer:
                            # Find complete <think></think> tags and remove them
                            pre = buffer.split("<think>", 1)[0]
                            post = buffer.split("</think>", 1)[1]
                            buffer = pre + post

                        # Handle case with only start tag
                        if "<think>" in buffer:
                            is_active = False
                            buffer = buffer.split("<think>", 1)[0]

                        # Handle case with only end tag
                        if "</think>" in buffer:
                            is_active = True
                            buffer = buffer.split("</think>", 1)[1]

                        # If currently active and buffer has content, output
                        if is_active and buffer:
                            logger.bind(tag=TAG).debug(f"Yielding content from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                            yield buffer
                            buffer = ""  # Clear buffer

                except Exception as e:
                    logger.bind(tag=TAG).error(f"Error processing chunk: {e}")

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in Ollama response generation: {e}")
            yield "【Ollama service response exception】"

    def response_with_functions(self, session_id, dialogue, functions=None):
        logger.bind(tag=TAG).debug(f"Sending function request to Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
        try:
            # If it's a specific model, add /no_think instruction to user's last message
            if self.needs_special_handling:
                # Copy dialogue list to avoid modifying original dialogue
                dialogue_copy = dialogue.copy()

                # Find the last user message
                for i in range(len(dialogue_copy) - 1, -1, -1):
                    if dialogue_copy[i]["role"] == "user":
                        # Add /no_think instruction before user message
                        dialogue_copy[i]["content"] = (
                            "/no_think " + dialogue_copy[i]["content"]
                        )
                        logger.bind(tag=TAG).debug(f"Added /no_think instruction for specific model")
                        break

                # Use modified dialogue
                dialogue = dialogue_copy

            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                stream=True,
                tools=functions,
            )

            logger.bind(tag=TAG).debug(f"Received function response from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
            is_active = True
            buffer = ""

            for chunk in stream:
                logger.bind(tag=TAG).debug(f"Received function chunk from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                try:
                    delta = (
                        chunk.choices[0].delta
                        if getattr(chunk, "choices", None)
                        else None
                    )
                    logger.bind(tag=TAG).debug(f"Received function delta from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                    content = delta.content if hasattr(delta, "content") else None
                    tool_calls = (
                        delta.tool_calls if hasattr(delta, "tool_calls") else None
                    )

                    # If it's a tool call, pass directly
                    if tool_calls:
                        logger.bind(tag=TAG).debug(f"Received tool call from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                        yield None, tool_calls
                        continue

                    # Process text content
                    if content:
                        logger.bind(tag=TAG).debug(f"Received function text content from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                        # Add content to buffer
                        buffer += content

                        # Process tags in buffer
                        while "<think>" in buffer and "</think>" in buffer:
                            # Find complete <think></think> tags and remove them
                            pre = buffer.split("<think>", 1)[0]
                            post = buffer.split("</think>", 1)[1]
                            buffer = pre + post

                        # Handle case with only start tag
                        if "<think>" in buffer:
                            is_active = False
                            buffer = buffer.split("<think>", 1)[0]

                        # Handle case with only end tag
                        if "</think>" in buffer:
                            is_active = True
                            buffer = buffer.split("</think>", 1)[1]

                        # If currently active and buffer has content, output
                        if is_active and buffer:
                            logger.bind(tag=TAG).debug(f"Yielding function content from Ollama with model: {self.model_name}, dialogue length: {len(dialogue)}")
                            yield buffer, None
                            buffer = ""  # Clear buffer
                except Exception as e:
                    logger.bind(tag=TAG).error(f"Error processing function chunk: {e}")
                    continue

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in Ollama function call: {e}")
            yield f"【Ollama service response exception: {str(e)}】", None
