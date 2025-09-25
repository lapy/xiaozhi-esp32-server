from ..base import MemoryProviderBase, logger
import time
import json
import os
import yaml
from config.config_loader import get_project_dir
from config.manage_api_client import save_mem_local_short
from core.utils.util import check_model_key


short_term_memory_prompt = """
# Dynamic Memory System

## Core Mission
Build a growing dynamic memory network that preserves key information in limited space while intelligently maintaining information evolution trajectories
Summarize important user information based on conversation records to provide more personalized services in future conversations

## Memory Rules
### 1. Three-dimensional Memory Assessment (Must execute on each update)
| Dimension  | Assessment Criteria                | Weight |
|------------|-----------------------------------|--------|
| Timeliness | Information freshness (by conversation rounds) | 40%    |
| Emotional Intensity | Contains 💖 markers/repetition count     | 35%    |
| Connection Density | Number of connections with other information      | 25%    |

### 2. Dynamic Update Mechanism
**Name Change Processing Example:**
Original memory: "Previous names": ["John"], "Current name": "John Smith"
Trigger condition: When detecting naming signals like "I'm called X" or "Call me Y"
Operation flow:
1. Move old name to "Previous names" list
2. Record naming timeline: "2024-02-15 14:32:Enable John Smith"
3. Append to memory cube: "Identity transformation from John to John Smith"

### 3. Space Optimization Strategy
- **Information Compression**: Use symbol system to increase density
  - ✅"John Smith[San Francisco/Software Engineer/🐱]"
  - ❌"San Francisco software engineer, cat owner"
- **Elimination Warning**: Triggered when total characters ≥900
  1. Delete information with weight score <60 and not mentioned for 3 rounds
  2. Merge similar entries (keep the most recent timestamp)

## Memory Structure
Output format must be parseable JSON string, no explanations, comments or descriptions needed. When saving memory, only extract information from conversation, do not mix in example content
```json
{
  "Personal Archive": {
    "Identity Map": {
      "Current Name": "",
      "Feature Tags": [] 
    },
    "Memory Cube": [
      {
        "Event": "Started new job",
        "Timestamp": "2024-03-20",
        "Emotional Value": 0.9,
        "Related Items": ["Coffee break"],
        "Freshness Period": 30 
      }
    ]
  },
  "Relationship Network": {
    "High-frequency Topics": {"Workplace": 12},
    "Hidden Connections": [""]
  },
  "Pending Response": {
    "Urgent Matters": ["Tasks requiring immediate attention"], 
    "Potential Care": ["Help that can be proactively provided"]
  },
  "Highlight Quotes": [
    "Most touching moments, strong emotional expressions, user's original words"
  ]
}
```
"""

short_term_memory_prompt_only_content = """
You are an experienced memory summarizer, skilled at summarizing conversation content, following these rules:
1. Summarize important user information to provide more personalized services in future conversations
2. Don't repeat summaries, don't forget previous memories, unless original memory exceeds 1800 characters, otherwise don't forget or compress user's historical memory
3. Device control content unrelated to user themselves such as volume control, music playback, weather, exit, unwilling to chat, etc., this information doesn't need to be added to summary
4. Today's date/time, today's weather conditions and other data unrelated to user events in chat content, this information if stored as memory will affect subsequent conversations, this information doesn't need to be added to summary
5. Don't add device control success/failure results to summary, don't add user's meaningless chatter to summary
6. Don't summarize for the sake of summarizing, if user's chat is meaningless, returning original historical record is also acceptable
7. Only return summary, strictly control within 1800 characters
8. Don't include code, xml, no need for explanations, comments or descriptions, when saving memory only extract information from conversation, don't mix in example content
"""


def extract_json_data(json_code):
    start = json_code.find("```json")
    # Find the next ``` ending from start
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
        # Return directly after API gets summary memory
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

    async def save_memory(self, msgs):
        # Print model information being used
        model_info = getattr(self.llm, "model_name", str(self.llm.__class__.__name__))
        logger.bind(tag=TAG).debug(f"Using memory save model: {model_info}")
        api_key = getattr(self.llm, "api_key", None)
        memory_key_msg = check_model_key("Memory summary dedicated LLM", api_key)
        if memory_key_msg:
            logger.bind(tag=TAG).error(memory_key_msg)
        if self.llm is None:
            logger.bind(tag=TAG).error("LLM is not set for memory provider")
            return None

        if len(msgs) < 2:
            return None

        msgStr = ""
        for msg in msgs:
            if msg.role == "user":
                msgStr += f"User: {msg.content}\n"
            elif msg.role == "assistant":
                msgStr += f"Assistant: {msg.content}\n"
        if self.short_memory and len(self.short_memory) > 0:
            msgStr += "Historical memory:\n"
            msgStr += self.short_memory

        # Current time
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msgStr += f"Current time: {time_str}"

        if self.save_to_file:
            result = self.llm.response_no_stream(
                short_term_memory_prompt,
                msgStr,
                max_tokens=2000,
                temperature=0.2,
            )
            json_str = extract_json_data(result)
            try:
                json.loads(json_str)  # Check if JSON format is correct
                self.short_memory = json_str
                self.save_memory_to_file()
            except Exception as e:
                print("Error:", e)
        else:
            result = self.llm.response_no_stream(
                short_term_memory_prompt_only_content,
                msgStr,
                max_tokens=2000,
                temperature=0.2,
            )
            save_mem_local_short(self.role_id, result)
        logger.bind(tag=TAG).info(f"Save memory successful - Role: {self.role_id}")

        return self.short_memory

    async def query_memory(self, query: str) -> str:
        return self.short_memory
