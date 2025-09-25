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

        logger.debug(
            f"Intent recognition parameters initialized: agent_id={self.agent_id}, base_url={self.base_url}, api_url={self.api_url}"
        )

    def response(self, session_id, dialogue, **kwargs):
        logger.bind(tag=TAG).debug(f"Sending request to Home Assistant with agent_id: {self.agent_id}, dialogue length: {len(dialogue)}")
        try:
            # Home Assistant voice assistant has built-in intent, no need to use xiaozhi ai built-in, just pass user speech to home assistant

            # Extract the last content where role is 'user'
            input_text = None
            if isinstance(dialogue, list):  # Ensure dialogue is a list
                # Traverse in reverse order, find the last message where role is 'user'
                for message in reversed(dialogue):
                    if message.get("role") == "user":  # Found message where role is 'user'
                        input_text = message.get("content", "")
                        logger.bind(tag=TAG).debug(f"Extracted user input from Home Assistant dialogue: {input_text[:50]}...")
                        break  # Exit loop immediately after finding

            # Construct request data
            payload = {
                "text": input_text,
                "agent_id": self.agent_id,
                "conversation_id": session_id,  # Use session_id as conversation_id
            }
            logger.bind(tag=TAG).debug(f"Constructed Home Assistant payload with conversation_id: {session_id}")
            
            # Set request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            logger.bind(tag=TAG).debug(f"Making Home Assistant API request to: {self.api_url}")
            
            # Make POST request
            response = requests.post(self.api_url, json=payload, headers=headers)

            logger.bind(tag=TAG).debug(f"Received Home Assistant response with status: {response.status_code}")

            # Check if request is successful
            response.raise_for_status()

            # Parse response data
            data = response.json()
            logger.bind(tag=TAG).debug(f"Parsed Home Assistant response data")
            
            speech = (
                data.get("response", {})
                .get("speech", {})
                .get("plain", {})
                .get("speech", "")
            )

            # Return generated content
            if speech:
                logger.bind(tag=TAG).debug(f"Yielding Home Assistant speech content: {speech[:50]}...")
                yield speech
            else:
                logger.bind(tag=TAG).warning("No speech content in Home Assistant API response data")

        except RequestException as e:
            logger.bind(tag=TAG).error(f"HTTP request error: {e}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"Error occurred while generating response: {e}")

    def response_with_functions(self, session_id, dialogue, functions=None):
        logger.bind(tag=TAG).debug(f"Sending function request to Home Assistant with agent_id: {self.agent_id}, dialogue length: {len(dialogue)}")
        logger.bind(tag=TAG).error(
            f"Home Assistant does not support function call, recommend using other intent recognition"
        )
