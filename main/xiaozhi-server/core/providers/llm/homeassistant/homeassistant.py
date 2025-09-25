import requests
from requests.exceptions import RequestException
from config.logger import setup_logging
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.agent_id = config.get("agent_id")  # Corresponds to agent_id
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", config.get("url"))  # Default use base_url
        self.api_url = f"{self.base_url}/api/conversation/process"  # Concatenate complete API URL

    def response(self, session_id, dialogue, **kwargs):
        try:
            # Home Assistant voice assistant has built-in intent, no need to use xiaozhi ai built-in, just pass user speech to home assistant

            # Extract the last content where role is 'user'
            input_text = None
            if isinstance(dialogue, list):  # Ensure dialogue is a list
                # Traverse in reverse order, find the last message where role is 'user'
                for message in reversed(dialogue):
                    if message.get("role") == "user":  # Found message where role is 'user'
                        input_text = message.get("content", "")
                        break  # Exit loop immediately after finding

            # Construct request data
            payload = {
                "text": input_text,
                "agent_id": self.agent_id,
                "conversation_id": session_id,  # Use session_id as conversation_id
            }
            # Set request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Make POST request
            response = requests.post(self.api_url, json=payload, headers=headers)

            # Check if request is successful
            response.raise_for_status()

            # Parse response data
            data = response.json()
            speech = (
                data.get("response", {})
                .get("speech", {})
                .get("plain", {})
                .get("speech", "")
            )

            # Return generated content
            if speech:
                yield speech
            else:
                logger.bind(tag=TAG).warning("No speech content in API response data")

        except RequestException as e:
            logger.bind(tag=TAG).error(f"HTTP request error: {e}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"Error occurred while generating response: {e}")

    def response_with_functions(self, session_id, dialogue, functions=None):
        logger.bind(tag=TAG).error(
            f"homeassistant does not support (function call), recommend using other intent recognition"
        )
