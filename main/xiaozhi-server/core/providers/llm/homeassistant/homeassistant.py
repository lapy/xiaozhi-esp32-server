import requests
from requests.exceptions import RequestException
from config.logger import setup_logging
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.agent_id = config.get("agent_id")  # Home Assistant agent ID.
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", config.get("url"))  # Prefer base_url when available.
        self.api_url = f"{self.base_url}/api/conversation/process"  # Full conversation API URL.

    def response(self, session_id, dialogue, **kwargs):
        # Home Assistant already provides its own intent handling, so just pass
        # the latest user utterance through.

        # Extract the most recent user message content.
        input_text = None
        if isinstance(dialogue, list):  # Make sure dialogue is a list.
            # Walk backward to find the latest user message.
            for message in reversed(dialogue):
                if message.get("role") == "user":
                    input_text = message.get("content", "")
                    break

        # Build the request payload.
        payload = {
            "text": input_text,
            "agent_id": self.agent_id,
            "conversation_id": session_id,  # Use session_id as conversation_id.
        }
        # Build request headers.
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Send the POST request.
        response = requests.post(self.api_url, json=payload, headers=headers)

        # Raise for HTTP failures.
        response.raise_for_status()

        # Parse the response payload.
        data = response.json()
        speech = (
            data.get("response", {})
            .get("speech", {})
            .get("plain", {})
            .get("speech", "")
        )

        # Yield the generated speech content.
        if speech:
            yield speech
        else:
            logger.bind(tag=TAG).warning(
                "API response did not include speech content"
            )

    def response_with_functions(self, session_id, dialogue, functions=None):
        logger.bind(tag=TAG).error(
            "Home Assistant does not support function calling; use a different intent provider"
        )
