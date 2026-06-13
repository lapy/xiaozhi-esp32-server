# RAGFlow Agent and Dify Compatibility Reference

## Dify-Compatible Retrieval

### `retrieval`

- Method: `POST`
- Path: `/api/v1/dify/retrieval`
- Purpose: Accept a Dify-style retrieval payload and return matching records.

Common request fields:

- `knowledge_id`
- `query`
- `use_kg`
- `retrieval_setting`
- `metadata_condition`

Common response fields:

- `records[].content`
- `records[].score`
- `records[].title`
- `records[].metadata`

## Agent Sessions

### `create_agent_session`

- Method: `POST`
- Path: `/api/v1/agents/<agent_id>/sessions`
- Purpose: Create a new agent session container.
- Optional query field: `user_id`

### `list_agent_session`

- Method: `GET`
- Path: `/api/v1/agents/<agent_id>/sessions`
- Purpose: List sessions for a specific agent.
- Common query fields: `page`, `page_size`, `orderby`, `desc`, `id`, `user_id`,
  `dsl`

### `delete_agent_session`

- Method: `DELETE`
- Path: `/api/v1/agents/<agent_id>/sessions`
- Purpose: Delete one or more sessions.
- Common body field: `ids`

## Agent Completions

### `agent_completions`

- Method: `POST`
- Path: `/api/v1/agents/<agent_id>/completions`
- Purpose: Run an agent session and stream or return a response.

Common request fields:

- `session_id`
- `question`
- `stream`
- `quote`

### `agents_completion_openai_compatibility`

- Method: `POST`
- Path: `/api/v1/agents_openai/<agent_id>/chat/completions`
- Purpose: Offer an OpenAI-style chat completion surface for an agent-backed
  workflow.

## Notes

- The downstream branch should prefer neutral examples and avoid locale-specific
  assumptions.
- If upstream expands the payload schema, update this summary rather than
  restoring a large translated document.
