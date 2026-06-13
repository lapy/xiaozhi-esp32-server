# RAGFlow Chat Session API Reference

## Scope

This document covers the session lifecycle for chat assistants.

## Endpoints

### `create`

- Method: `POST`
- Path: `/api/v1/chats/<chat_id>/sessions`
- Purpose: Create a new chat session.

Common request fields:

- `name`
- `user_id`

### `list_session`

- Method: `GET`
- Path: `/api/v1/chats/<chat_id>/sessions`
- Purpose: List sessions under a chat assistant.

Common query fields:

- `page`
- `page_size`
- `orderby`
- `desc`
- `name`
- `id`
- `user_id`

### `update`

- Method: `PUT`
- Path: `/api/v1/chats/<chat_id>/sessions/<session_id>`
- Purpose: Rename or otherwise update session metadata.

Typical body field:

- `name`

### `delete`

- Method: `DELETE`
- Path: `/api/v1/chats/<chat_id>/sessions`
- Purpose: Delete selected sessions or, if supported upstream, all sessions
  under a chat assistant.

Common body field:

- `ids`

## Typical Returned Fields

- `id`
- `chat_id`
- `name`
- `user_id`
- `messages`
- `create_time`
- `update_time`

## Notes

- The prologue or starter message is usually injected automatically from the
  chat assistant definition.
- Session history is the foundation for subsequent chat completion calls.
