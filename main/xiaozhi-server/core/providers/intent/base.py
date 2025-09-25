from abc import ABC, abstractmethod
from typing import List, Dict
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class IntentProviderBase(ABC):
    def __init__(self, config):
        self.config = config

    def set_llm(self, llm):
        self.llm = llm
        # Get model name and type information
        model_name = getattr(llm, "model_name", str(llm.__class__.__name__))
        # Record more detailed logs
        logger.bind(tag=TAG).info(f"Intent recognition set LLM: {model_name}")

    @abstractmethod
    async def detect_intent(self, conn, dialogue_history: List[Dict], text: str) -> str:
        """
        Detect intent of user's last sentence
        Args:
            dialogue_history: Dialogue history list, each record contains role and content
        Returns:
            Returns identified intent in format:
            - "continue chat"
            - "end chat"
            - "play music song_name" or "play random music"
            - "query weather location_name" or "query weather [current location]"
        """
        pass
