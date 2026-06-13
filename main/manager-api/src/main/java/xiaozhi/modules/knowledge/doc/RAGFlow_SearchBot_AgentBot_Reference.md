# RAGFlow SearchBot and AgentBot Reference

## SearchBot Endpoints

### `ask_about_embedded`

- Method: `POST`
- Path: `/api/v1/searchbots/ask`
- Purpose: Run a retrieval-focused SearchBot query for embedded use cases.

Common request fields:

- `question`
- `kb_ids`
- `search_id`

### `mindmap`

- Method: `POST`
- Path: `/api/v1/searchbots/mindmap`
- Purpose: Return a mind-map structure for a query.

### `related_questions_embedded`

- Method: `POST`
- Path: `/api/v1/searchbots/related_questions`
- Purpose: Suggest related questions for an embedded search experience.

### `detail_share_embedded`

- Method: `GET`
- Path: `/api/v1/searchbots/detail`
- Purpose: Return SearchBot configuration details used by citation or sidebar
  displays.

### `retrieval_test_embedded`

- Method: `POST`
- Path: `/api/v1/searchbots/retrieval_test`
- Purpose: Return retrieval chunks directly for testing.

## AgentBot Endpoints

### `begin_inputs`

- Method: `GET`
- Path: `/api/v1/agentbots/<agent_id>/inputs`
- Purpose: Return the prologue and input schema required before an embedded
  agent run starts.

### `agent_bot_completions`

- Method: `POST`
- Path: `/api/v1/agentbots/<agent_id>/completions`
- Purpose: Execute an embedded agent interaction.

Common request fields:

- `question`
- `inputs`
- `stream`

## Notes

- SearchBot is retrieval-first.
- AgentBot is workflow-first.
- Both surfaces are common entry points for external embedded experiences, so
  examples should remain English-first and provider-neutral.
