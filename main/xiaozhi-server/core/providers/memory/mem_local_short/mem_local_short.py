from ..base import MemoryProviderBase, logger
import time
import json
import os
import yaml
from config.config_loader import get_project_dir
from config.manage_api_client import generate_and_save_chat_summary
import asyncio
from core.utils.util import check_model_key


short_term_memory_prompt = """
# Adaptive Memory Weaver

## Core mission
Build a living memory network that keeps the most important information while
tracking how it evolves over time. Summarize the user's important details from
the conversation so future replies can feel more personal and context-aware.

## Memory rules
### 1. Three-dimensional memory scoring (run on every update)
| Dimension | Evaluation standard | Weight |
|-----------|---------------------|--------|
| Recency | How recently the information appeared in the dialogue | 40% |
| Emotional intensity | Strong emotional cues, repeated mentions, or heartfelt wording | 35% |
| Relationship density | Number of meaningful links to other stored details | 25% |

### 2. Dynamic update behavior
**Example: handling a name change**
Existing memory: `"former_names": ["Sam"], "current_name": "Samuel"`
Trigger condition: when the user says things like "my name is X" or "call me Y"
Update steps:
1. Move the old name into the `former_names` list.
2. Record the naming timeline, for example: `"2024-02-15 14:32: switched to Samuel"`.
3. Append a short identity-change note to the memory timeline.

### 3. Space optimization strategy
- **Compress information** using compact symbolic summaries when possible.
  - Good: `"Samuel[Seattle/software engineer/cat]"`
  - Bad: `"A software engineer in Seattle who owns a cat"`
- **Eviction warning**: when the total memory size reaches 900 characters or more:
  1. Delete low-value information with a score below 60 that has not been mentioned in 3 turns.
  2. Merge similar entries and keep the most recent timestamp.

## Memory structure
The output must be a valid JSON string only. Do not include explanations,
comments, or extra notes. Extract information only from the actual dialogue and
do not mix example content into the saved memory.
```json
{
  "timeline_profile": {
    "identity_map": {
      "current_name": "",
      "traits": []
    },
    "memory_timeline": [
      {
        "event": "Started a new job",
        "timestamp": "2024-03-20",
        "emotion_score": 0.9,
        "related_items": ["afternoon coffee"],
        "retention_days": 30
      }
    ]
  },
  "relationship_graph": {
    "frequent_topics": {"career": 12},
    "latent_links": [""]
  },
  "follow_up": {
    "urgent_items": ["Tasks that need immediate attention"],
    "care_opportunities": ["Helpful actions the assistant could offer proactively"]
  },
  "highlight_quotes": [
    "The user's most emotionally meaningful original quote"
  ]
}
```
"""


def extract_json_data(json_code):
    start = json_code.find("```json")
    # Find the closing ``` fence that follows the opening ```json block.
    end = json_code.find("```", start + 1)
    # print("start:", start, "end:", end)
    if start == -1 or end == -1:
        try:
            jsonData = json.loads(json_code)
            return json_code
        except Exception as e:
            print("Error:", e)
        return ""
    jsonData = json_code[start + 7 : end]
    return jsonData


TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory):
        super().__init__(config)
        self.short_memory = ""
        self.save_to_file = True
        self.memory_path = get_project_dir() + "data/.memory.yaml"
        self.load_memory(summary_memory)

    def init_memory(
        self, role_id, llm, summary_memory=None, save_to_file=True, **kwargs
    ):
        super().init_memory(role_id, llm, **kwargs)
        self.save_to_file = save_to_file
        self.load_memory(summary_memory)

    def load_memory(self, summary_memory):
        # Return immediately when summary memory comes from the API.
        if summary_memory or not self.save_to_file:
            self.short_memory = summary_memory
            return

        all_memory = {}
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                all_memory = yaml.safe_load(f) or {}
        if self.role_id in all_memory:
            self.short_memory = all_memory[self.role_id]

    def save_memory_to_file(self):
        all_memory = {}
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r", encoding="utf-8") as f:
                all_memory = yaml.safe_load(f) or {}
        all_memory[self.role_id] = self.short_memory
        with open(self.memory_path, "w", encoding="utf-8") as f:
            yaml.dump(all_memory, f, allow_unicode=True)

    async def save_memory(self, msgs, session_id=None):
        # Log the model being used to save memory.
        model_info = getattr(self.llm, "model_name", str(self.llm.__class__.__name__))
        logger.bind(tag=TAG).debug(f"Using memory-save model: {model_info}")
        api_key = getattr(self.llm, "api_key", None)
        memory_key_msg = check_model_key("Memory summary LLM", api_key)
        if memory_key_msg:
            logger.bind(tag=TAG).error(memory_key_msg)
        if self.llm is None:
            logger.bind(tag=TAG).error("LLM is not set for memory provider")
            return None

        if len(msgs) < 2:
            return None

        msgStr = ""
        for msg in msgs:
            content = msg.content

            # Extract content from JSON format if present (for ASR with emotion/language tags)
            try:
                if content and content.strip().startswith("{") and content.strip().endswith("}"):
                    data = json.loads(content)
                    if "content" in data:
                        content = data["content"]
            except (json.JSONDecodeError, KeyError, TypeError):
                # If parsing fails, use original content
                pass

            if msg.role == "user":
                msgStr += f"User: {content}\n"
            elif msg.role == "assistant":
                msgStr += f"Assistant: {content}\n"
        if self.short_memory and len(self.short_memory) > 0:
            msgStr += "Historical memory:\n"
            msgStr += self.short_memory

        # Add the current time for temporal context.
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msgStr += f"Current time: {time_str}"

        if self.save_to_file:
            try:
                result = self.llm.response_no_stream(
                    short_term_memory_prompt,
                    msgStr,
                    max_tokens=2000,
                    temperature=0.2,
                )
                json_str = extract_json_data(result)
                json.loads(json_str)  # Validate that the result is proper JSON.
                self.short_memory = json_str
                self.save_memory_to_file()
            except Exception as e:
                logger.bind(tag=TAG).error(f"Error in saving memory: {e}")
        else:
            # When not saving locally, delegate summary generation to the Java API.
            summary_id = session_id if session_id else self.role_id
            await generate_and_save_chat_summary(summary_id)
        logger.bind(tag=TAG).info(
            f"Save memory successful - Role: {self.role_id}, Session: {session_id}"
        )

        return self.short_memory

    async def query_memory(self, query: str) -> str:
        return self.short_memory
