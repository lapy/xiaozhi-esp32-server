import json
import uuid
import asyncio
from core.utils.dialogue import Message
from core.providers.tts.dto.dto import ContentType
from core.handle.helloHandle import checkWakeupWords
from plugins_func.register import Action, ActionResponse
from core.handle.sendAudioHandle import send_stt_message
from core.utils.util import remove_punctuation_and_length
from core.providers.tts.dto.dto import TTSMessageDTO, SentenceType

TAG = __name__


async def handle_user_intent(conn, text):
    # Preprocess input text, handle possible JSON format
    try:
        if text.strip().startswith('{') and text.strip().endswith('}'):
            parsed_data = json.loads(text)
            if isinstance(parsed_data, dict) and "content" in parsed_data:
                text = parsed_data["content"]  # Extract content for intent analysis
                conn.current_speaker = parsed_data.get("speaker")  # Preserve speaker information
    except (json.JSONDecodeError, TypeError):
        pass

    # Check if there are explicit exit commands
    _, filtered_text = remove_punctuation_and_length(text)
    if await check_direct_exit(conn, filtered_text):
        return True

    # Check if it's a wake word
    if await checkWakeupWords(conn, filtered_text):
        return True

    if conn.intent_type == "function_call":
        # Use chat method that supports function calling, no longer perform intent analysis
        return False
    # Use LLM for intent analysis
    intent_result = await analyze_intent_with_llm(conn, text)
    if not intent_result:
        return False
    # Generate sentence_id at start of conversation
    conn.sentence_id = str(uuid.uuid4().hex)
    # Handle various intents
    return await process_intent_result(conn, intent_result, text)


async def check_direct_exit(conn, text):
    """Check if there are explicit exit commands"""
    _, text = remove_punctuation_and_length(text)
    cmd_exit = conn.cmd_exit
    for cmd in cmd_exit:
        if text == cmd:
            conn.logger.bind(tag=TAG).info(f"Recognized explicit exit command: {text}")
            await send_stt_message(conn, text)
            await conn.close()
            return True
    return False


async def analyze_intent_with_llm(conn, text):
    """Use LLM to analyze user intent"""
    if not hasattr(conn, "intent") or not conn.intent:
        conn.logger.bind(tag=TAG).warning("Intent recognition service not initialized")
        return None

    # Conversation history
    dialogue = conn.dialogue
    try:
        intent_result = await conn.intent.detect_intent(conn, dialogue.dialogue, text)
        return intent_result
    except Exception as e:
        conn.logger.bind(tag=TAG).error(f"Intent recognition failed: {str(e)}")

    return None


async def process_intent_result(conn, intent_result, original_text):
    """Process intent recognition result"""
    try:
        # Try to parse result as JSON
        intent_data = json.loads(intent_result)

        # Check if there's function_call
        if "function_call" in intent_data:
            # Got function_call directly from intent recognition
            conn.logger.bind(tag=TAG).debug(
                f"Detected function_call format intent result: {intent_data['function_call']['name']}"
            )
            function_name = intent_data["function_call"]["name"]
            if function_name == "continue_chat":
                return False

            if function_name == "result_for_context":
                await send_stt_message(conn, original_text)
                conn.client_abort = False
                
                def process_context_result():
                    conn.dialogue.put(Message(role="user", content=original_text))
                    
                    from core.utils.current_time import get_current_time_info

                    current_time, today_date, today_weekday, formatted_date = get_current_time_info()
                    
                    # Build basic prompt with context
                    context_prompt = f"""Current time: {current_time}
                                        Today's date: {today_date} ({today_weekday})

                                        Please answer the user's question based on the above information: {original_text}"""
                    
                    response = conn.intent.replyResult(context_prompt, original_text)
                    speak_txt(conn, response)
                
                conn.executor.submit(process_context_result)
                return True

            function_args = {}
            if "arguments" in intent_data["function_call"]:
                function_args = intent_data["function_call"]["arguments"]
                if function_args is None:
                    function_args = {}
            # Ensure parameters are in string format JSON
            if isinstance(function_args, dict):
                function_args = json.dumps(function_args)

            function_call_data = {
                "name": function_name,
                "id": str(uuid.uuid4().hex),
                "arguments": function_args,
            }

            await send_stt_message(conn, original_text)
            conn.client_abort = False

            # Use executor to execute function calls and process results
            def process_function_call():
                conn.dialogue.put(Message(role="user", content=original_text))

                # Use unified tool handler to process all tool calls
                try:
                    result = asyncio.run_coroutine_threadsafe(
                        conn.func_handler.handle_llm_function_call(
                            conn, function_call_data
                        ),
                        conn.loop,
                    ).result()
                except Exception as e:
                    conn.logger.bind(tag=TAG).error(f"Tool call failed: {e}")
                    result = ActionResponse(
                        action=Action.ERROR, result=str(e), response=str(e)
                    )

                if result:
                    if result.action == Action.RESPONSE:  # Direct response to frontend
                        text = result.response
                        if text is not None:
                            speak_txt(conn, text)
                    elif result.action == Action.REQLLM:  # Call function then request LLM to generate response
                        text = result.result
                        conn.dialogue.put(Message(role="tool", content=text))
                        llm_result = conn.intent.replyResult(text, original_text)
                        if llm_result is None:
                            llm_result = text
                        speak_txt(conn, llm_result)
                    elif (
                        result.action == Action.NOTFOUND
                        or result.action == Action.ERROR
                    ):
                        text = result.result
                        if text is not None:
                            speak_txt(conn, text)
                    elif function_name != "play_music":
                        # For backward compatibility with original code
                        # Get current latest text index
                        text = result.response
                        if text is None:
                            text = result.result
                        if text is not None:
                            speak_txt(conn, text)

            # Put function execution in thread pool
            conn.executor.submit(process_function_call)
            return True
        return False
    except json.JSONDecodeError as e:
        conn.logger.bind(tag=TAG).error(f"Error processing intent result: {e}")
        return False


def speak_txt(conn, text):
    conn.tts.tts_text_queue.put(
        TTSMessageDTO(
            sentence_id=conn.sentence_id,
            sentence_type=SentenceType.FIRST,
            content_type=ContentType.ACTION,
        )
    )
    conn.tts.tts_one_sentence(conn, ContentType.TEXT, content_detail=text)
    conn.tts.tts_text_queue.put(
        TTSMessageDTO(
            sentence_id=conn.sentence_id,
            sentence_type=SentenceType.LAST,
            content_type=ContentType.ACTION,
        )
    )
    conn.dialogue.put(Message(role="assistant", content=text))
