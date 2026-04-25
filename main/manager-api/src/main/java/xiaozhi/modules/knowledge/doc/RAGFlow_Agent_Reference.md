# RAGFlow Agent API Reference

## Scope

This document summarizes the external Agent management surface under
`/api/v1/agents`.

## Endpoints

### `list_agents`

- Method: `GET`
- Path: `/api/v1/agents`
- Purpose: List tenant-visible agents with optional filtering by `id` or
  `title`.
- Common query fields: `page`, `page_size`, `orderby`, `desc`, `id`, `title`

### `create_agent`

- Method: `POST`
- Path: `/api/v1/agents`
- Purpose: Create a new agent definition.
- Typical body fields: `title`, `dsl`, `description`, `avatar`

### `update_agent`

- Method: `PUT`
- Path: `/api/v1/agents/<agent_id>`
- Purpose: Update an existing agent.
- Typical body fields: `title`, `dsl`, `description`, `avatar`

### `delete_agent`

- Method: `DELETE`
- Path: `/api/v1/agents/<agent_id>`
- Purpose: Permanently delete an agent.

### `webhook`

- Method: `POST` or configured method
- Path: `/api/v1/webhook_test/<agent_id>`
- Purpose: Exercise a webhook-enabled agent flow from an external trigger.

### `webhook_trace`

- Method: `POST` or configured method
- Path: `/api/v1/webhook_trace/<agent_id>`
- Purpose: Inspect webhook execution traces for debugging.

## Returned Data

Typical agent records include:

- `id`
- `title`
- `description`
- `dsl`
- `user_id`
- `avatar`
- `canvas_category`
- `create_time`
- `update_time`

## Notes

- Agents are orchestration-oriented and usually contain graph-style DSL.
- The downstream branch should keep provider-neutral examples and
  English-first descriptions.
