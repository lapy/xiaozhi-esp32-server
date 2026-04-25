# RAGFlow Chat API Reference

## Scope

This document covers the chat assistant management endpoints under `/api/v1/chats`.

## Endpoints

### `create`

- Method: `POST`
- Path: `/api/v1/chats`
- Purpose: Create a chat assistant.

Typical body fields:

- `name`
- `avatar`
- `description`
- `prompt_config`
- `dataset_ids`

### `list_chat`

- Method: `GET`
- Path: `/api/v1/chats`
- Purpose: List chat assistants with paging and filters.

Common query fields:

- `page`
- `page_size`
- `orderby`
- `desc`
- `id`
- `name`

### `update`

- Method: `PUT`
- Path: `/api/v1/chats/<chat_id>`
- Purpose: Update a chat assistant definition.

### `delete_chats`

- Method: `DELETE`
- Path: `/api/v1/chats`
- Purpose: Delete one or more chat assistants.
- Common body field: `ids`

## Typical Returned Fields

- `id`
- `name`
- `description`
- `avatar`
- `dataset_ids`
- `prompt_config`
- `llm_setting`
- `create_time`
- `update_time`

## Notes

- Chat assistants represent assistant-style conversational apps rather than
  graph-driven agents.
- Completion and session operations are documented separately.
