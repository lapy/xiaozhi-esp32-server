import uuid
import re
from typing import List, Dict
from datetime import datetime


class Message:
    def __init__(
            self,
            role: str,
            content: str = None,
            uniq_id: str = None,
            tool_calls=None,
            tool_call_id=None,
            is_temporary=False,
    ):
        self.uniq_id = uniq_id if uniq_id is not None else str(uuid.uuid4())
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
        self.tool_call_id = tool_call_id
        self.is_temporary = is_temporary  # Marks temporary messages such as tool reminders.


class Dialogue:
    def __init__(self):
        self.dialogue: List[Message] = []
        # Get current time
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def put(self, message: Message):
        self.dialogue.append(message)

    def getMessages(self, m, dialogue):
        if m.tool_calls is not None:
            dialogue.append({"role": m.role, "tool_calls": m.tool_calls})
        elif m.role == "tool":
            dialogue.append(
                {
                    "role": m.role,
                    "tool_call_id": (
                        str(uuid.uuid4()) if m.tool_call_id is None else m.tool_call_id
                    ),
                    "content": m.content,
                }
            )
        else:
            dialogue.append({"role": m.role, "content": m.content})

    def get_llm_dialogue(self) -> List[Dict[str, str]]:
        # Directly call get_llm_dialogue_with_memory, pass None as memory_str
        # This ensures speaker functionality works in all call paths
        return self.get_llm_dialogue_with_memory(None, None)

    def update_system_message(self, new_content: str):
        """Update or add system message"""
        # Find first system message
        system_msg = next((msg for msg in self.dialogue if msg.role == "system"), None)
        if system_msg:
            system_msg.content = new_content
        else:
            self.put(Message(role="system", content=new_content))

    def trim_history(self, max_turns: int = 10) -> int:
        """
        Trim dialogue history while preserving complete tool-call chains.

        Args:
            max_turns: Maximum number of turns to keep. One turn includes the
                user message plus related assistant/tool messages.

        Returns:
            int: Number of removed messages.
        """
        if len(self.dialogue) <= max_turns * 2 + 1:  # +1 for the system message
            return 0

        # Split system messages from conversation messages.
        system_messages = [msg for msg in self.dialogue if msg.role == "system"]
        conversation_messages = [msg for msg in self.dialogue if msg.role != "system"]

        if len(conversation_messages) <= max_turns * 2:
            return 0

        # Preserve complete tool-call chains when trimming.
        keep_messages = []
        i = len(conversation_messages) - 1
        turn_count = 0

        while i >= 0 and turn_count < max_turns:
            msg = conversation_messages[i]

            # Collect messages from newest to oldest.
            if msg.role == "user":
                # A user message marks the start of a turn.
                keep_messages.insert(0, msg)
                turn_count += 1
                i -= 1
            elif msg.role == "assistant":
                # Keep assistant messages.
                keep_messages.insert(0, msg)

                # If this assistant message triggered tools, keep the tool results too.
                if msg.tool_calls is not None:
                    i -= 1
                    # Keep walking backward through related tool messages.
                    while i >= 0 and conversation_messages[i].role == "tool":
                        keep_messages.insert(0, conversation_messages[i])
                        i -= 1
                else:
                    i -= 1
            elif msg.role == "tool":
                # Tool messages should normally be captured above, but keep them
                # here too for edge cases.
                keep_messages.insert(0, msg)
                i -= 1
            else:
                i -= 1

        removed_count = len(conversation_messages) - len(keep_messages)

        # Rebuild the dialogue list.
        self.dialogue = system_messages + keep_messages

        return removed_count

    def get_llm_dialogue_with_memory(
            self, memory_str: str = None, voiceprint_config: dict = None
    ) -> List[Dict[str, str]]:
        # Build conversation
        dialogue = []

        # Add system prompt and memory
        system_message = next(
            (msg for msg in self.dialogue if msg.role == "system"), None
        )

        if system_message:
            # Basic system prompt
            enhanced_system_prompt = system_message.content
            # Replace the time placeholder.
            enhanced_system_prompt = enhanced_system_prompt.replace(
                "{{current_time}}", datetime.now().strftime("%H:%M")
            )

            # Add speaker personalization details.
            try:
                speakers = voiceprint_config.get("speakers", [])
                if speakers:
                    enhanced_system_prompt += "\n\n<speakers_info>"
                    for speaker_str in speakers:
                        try:
                            parts = speaker_str.split(",", 2)
                            if len(parts) >= 2:
                                name = parts[1].strip()
                                # If the description is empty, use an empty string.
                                description = (
                                    parts[2].strip() if len(parts) >= 3 else ""
                                )
                                enhanced_system_prompt += f"\n- {name}: {description}"
                        except:
                            pass
                    enhanced_system_prompt += "\n\n</speakers_info>"
            except:
                # Ignore speaker-config errors so they do not affect other features.
                pass

            # Replace <memory> tags regardless of the content they currently hold.
            if memory_str is not None:
                enhanced_system_prompt = re.sub(
                    r"<memory>.*?</memory>",
                    f"<memory>\n{memory_str}\n</memory>",
                    enhanced_system_prompt,
                    flags=re.DOTALL,
                )
            dialogue.append({"role": "system", "content": enhanced_system_prompt})

        # Add the user and assistant dialogue.
        for m in self.dialogue:
            if m.role != "system":  # Skip original system messages.
                self.getMessages(m, dialogue)

        return dialogue
