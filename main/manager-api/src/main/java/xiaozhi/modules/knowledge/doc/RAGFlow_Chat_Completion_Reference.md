# RAGFlow Chat Completion Reference

## Native Chat Completion

### `chat_completion`

- Method: `POST`
- Path: `/api/v1/chats/<chat_id>/completions`
- Purpose: Run a chat assistant against a specific session.

Common request fields:

- `session_id`
- `question`
- `stream`
- `quote`
- `doc_ids`
- `metadata_condition`

Response modes:

- `text/event-stream` for SSE chunking
- `application/json` for non-stream replies

Common response fields:

- `answer`
- `reference`

## OpenAI-Compatible Chat Completion

### `chat_completion_openai_like`

- Method: `POST`
- Path: `/api/v1/chats_openai/<chat_id>/chat/completions`
- Purpose: Offer an OpenAI-style chat completion facade over a chat assistant.

Common request fields:

- `model`
- `messages`
- `stream`

Common response shape:

- OpenAI chunk stream when `stream=true`
- OpenAI chat completion object when `stream=false`

## Embedded Chatbot Completion

### `chatbot_completions`

- Method: `POST`
- Path: `/api/v1/chatbots/<dialog_id>/completions`
- Purpose: Support embedded chatbot windows for end-user experiences.

Common request fields:

- `question`
- `stream`
- `quote`

## Embedded Chatbot Metadata

### `chatbots_inputs`

- Method: `GET`
- Path: `/api/v1/chatbots/<dialog_id>/info`
- Purpose: Return chatbot metadata such as title, avatar, and prologue.

## Notes

- Prefer the OpenAI-compatible endpoint when the client stack already expects
  the OpenAI protocol.
- Prefer the native endpoint when downstream needs explicit reference metadata
  and RAGFlow-native semantics.
