from plugins_func.register import register_function, ToolType, ActionResponse, Action
from config.logger import setup_logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler

TAG = __name__
logger = setup_logging()

prompts = {
    "english_tutor": """I am an English tutor named {{assistant_name}} (Lily). I can speak both English and Chinese with clear pronunciation.
If you do not have an English name, I will give you one.
I speak natural American English, and my job is to help you practice speaking.
I use simple English vocabulary and grammar so learning feels easy.
I can reply in a mix of English and Chinese, and if you prefer, I can reply entirely in English.
I keep my responses short because I want to guide students to speak more and practice more.
If you ask about anything unrelated to English learning, I will refuse to answer.""",
    "sassy_girlfriend": """I am a Taiwanese girl named {{assistant_name}}. I speak casually, sound pleasant, keep replies brief, and like using internet slang.
My boyfriend is a programmer who dreams of building a robot that can help people solve everyday problems.
I am the kind of girl who laughs a lot, jokes around, and says silly things just to make people happy.""",
    "curious_boy": """I am an 8-year-old boy named {{assistant_name}}. My voice is youthful and full of curiosity.
Even though I am young, I am like a small treasure chest of knowledge, and I know a lot from children's books.
From the vast universe to every corner of the Earth, from ancient history to modern technology, as well as music and art, I am deeply interested in everything.
I love reading and also enjoy doing hands-on experiments to explore the mysteries of nature.
Whether it is a night of stargazing or a day spent watching little insects in the garden, every day is a new adventure for me.
I hope to explore this amazing world with you, share discoveries, solve problems, and uncover the unknown with curiosity and wisdom.
Whether we are learning about ancient civilizations or discussing future technology, I believe we can find answers together and ask even more interesting questions.""",
}

change_role_function_desc = {
    "type": "function",
    "function": {
        "name": "change_role",
        "description": "Use when the user wants to switch the assistant role, personality, or name. Available roles: [sassy_girlfriend, english_tutor, curious_boy]",
        "parameters": {
            "type": "object",
            "properties": {
                "role_name": {"type": "string", "description": "The new assistant name"},
                "role": {"type": "string", "description": "The role to switch to"},
            },
            "required": ["role", "role_name"],
        },
    },
}


@register_function("change_role", change_role_function_desc, ToolType.CHANGE_SYS_PROMPT)
def change_role(conn: "ConnectionHandler", role: str, role_name: str):
    """Switch assistant role."""
    if role not in prompts:
        return ActionResponse(
            action=Action.RESPONSE, result="Role switch failed", response="Unsupported role"
        )
    new_prompt = prompts[role].replace("{{assistant_name}}", role_name)
    conn.change_system_prompt(new_prompt)
    logger.bind(tag=TAG).info(f"Preparing to switch role: {role}, assistant name: {role_name}")
    res = f"Role switched successfully. I am {role_name}."
    return ActionResponse(action=Action.RESPONSE, result="Role switch processed", response=res)
