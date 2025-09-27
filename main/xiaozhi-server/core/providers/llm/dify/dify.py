import json
from config.logger import setup_logging
import requests
from core.providers.llm.base import LLMProviderBase
from core.providers.llm.system_prompt import get_system_prompt_for_function
from core.utils.util import check_model_key

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.mode = config.get("mode", "chat-messages")
        self.base_url = config.get("base_url", "https://api.dify.ai/v1").rstrip("/")
        self.session_conversation_map = {}  # Store mapping of session_id and conversation_id
        
        logger.debug(
            f"Intent recognition parameters initialized: mode={self.mode}, base_url={self.base_url}"
        )
        
        model_key_msg = check_model_key("DifyLLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)

    def response(self, session_id, dialogue, **kwargs):
        logger.bind(tag=TAG).debug(f"Sending request to Dify with mode: {self.mode}, dialogue length: {len(dialogue)}")
        try:
            # Get last user message
            last_msg = next(m for m in reversed(dialogue) if m["role"] == "user")
            conversation_id = self.session_conversation_map.get(session_id)

            logger.bind(tag=TAG).debug(f"Processing Dify request with conversation_id: {conversation_id}")

            # Make streaming request
            if self.mode == "chat-messages":
                request_json = {
                    "query": last_msg["content"],
                    "response_mode": "streaming",
                    "user": session_id,
                    "inputs": {},
                    "conversation_id": conversation_id,
                }
            elif self.mode == "workflows/run":
                request_json = {
                    "inputs": {"query": last_msg["content"]},
                    "response_mode": "streaming",
                    "user": session_id,
                }
            elif self.mode == "completion-messages":
                request_json = {
                    "inputs": {"query": last_msg["content"]},
                    "response_mode": "streaming",
                    "user": session_id,
                }

            logger.bind(tag=TAG).debug(f"Making Dify API request to: {self.base_url}/{self.mode}")
            
            with requests.post(
                f"{self.base_url}/{self.mode}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=request_json,
                stream=True,
            ) as r:
                logger.bind(tag=TAG).debug(f"Received Dify response with status: {r.status_code}")
                
                if self.mode == "chat-messages":
                    for line in r.iter_lines():
                        if line.startswith(b"data: "):
                            event = json.loads(line[6:])
                            logger.bind(tag=TAG).debug(f"Received Dify event: {event.get('event', 'unknown')}")
                            
                            # If conversation_id is not found, get this conversation_id
                            if not conversation_id:
                                conversation_id = event.get("conversation_id")
                                self.session_conversation_map[session_id] = (
                                    conversation_id  # Update mapping
                                )
                                logger.bind(tag=TAG).debug(f"Updated conversation_id: {conversation_id}")
                            
                            # Filter message_replace event, this event pushes all content once
                            if event.get("event") != "message_replace" and event.get(
                                "answer"
                            ):
                                logger.bind(tag=TAG).debug(f"Yielding Dify answer content")
                                yield event["answer"]
                elif self.mode == "workflows/run":
                    for line in r.iter_lines():
                        if line.startswith(b"data: "):
                            event = json.loads(line[6:])
                            logger.bind(tag=TAG).debug(f"Received Dify workflow event: {event.get('event', 'unknown')}")
                            
                            if event.get("event") == "workflow_finished":
                                if event["data"]["status"] == "succeeded":
                                    logger.bind(tag=TAG).debug(f"Yielding Dify workflow result")
                                    yield event["data"]["outputs"]["answer"]
                                else:
                                    logger.bind(tag=TAG).error(f"Dify workflow failed: {event['data']['status']}")
                                    yield "【Service response exception】"
                elif self.mode == "completion-messages":
                    for line in r.iter_lines():
                        if line.startswith(b"data: "):
                            event = json.loads(line[6:])
                            logger.bind(tag=TAG).debug(f"Received Dify completion event: {event.get('event', 'unknown')}")
                            
                            # Filter message_replace event, this event pushes all content once
                            if event.get("event") != "message_replace" and event.get(
                                "answer"
                            ):
                                logger.bind(tag=TAG).debug(f"Yielding Dify completion answer content")
                                yield event["answer"]

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")
            yield "【Service response exception】"

    def response_with_functions(self, session_id, dialogue, functions=None):
        logger.bind(tag=TAG).debug(f"Sending function request to Dify with mode: {self.mode}, dialogue length: {len(dialogue)}")
        
        if len(dialogue) == 2 and functions is not None and len(functions) > 0:
            # First call to LLM, get last user message, append tool prompt
            last_msg = dialogue[-1]["content"]
            function_str = json.dumps(functions, ensure_ascii=False)
            modify_msg = get_system_prompt_for_function(function_str) + last_msg
            dialogue[-1]["content"] = modify_msg
            logger.bind(tag=TAG).debug(f"Modified dialogue with function prompt for Dify")

        # If the last one is role="tool", append to user
        if len(dialogue) > 1 and dialogue[-1]["role"] == "tool":
            assistant_msg = "\ntool call result: " + dialogue[-1]["content"] + "\n\n"
            while len(dialogue) > 1:
                if dialogue[-1]["role"] == "user":
                    dialogue[-1]["content"] = assistant_msg + dialogue[-1]["content"]
                    logger.bind(tag=TAG).debug(f"Appended tool result to user message for Dify")
                    break
                dialogue.pop()

        for token in self.response(session_id, dialogue):
            yield token, None
