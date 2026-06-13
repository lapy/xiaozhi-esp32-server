# RAGFlow Session Extras Reference

## `detail_share_embedded`

- Method: `GET`
- Path: `/api/v1/searchbots/detail`
- Purpose: Return SearchBot details that help the frontend display citation or
  source context.

Common query field:

- `search_id`

## `retrieval_test_embedded`

- Method: `POST`
- Path: `/api/v1/searchbots/retrieval_test`
- Purpose: Run retrieval-only testing for a SearchBot configuration.

Common request fields:

- `kb_id`
- `question`
- `page`
- `size`
- `doc_ids`
- `similarity_threshold`
- `top_k`
- `highlight`

## `ask_about`

- Method: `POST`
- Path: `/api/v1/sessions/ask`
- Purpose: Run an internal session question directly against selected datasets.

Common request fields:

- `question`
- `dataset_ids`

## `related_questions`

- Method: `POST`
- Path: `/api/v1/sessions/related_questions`
- Purpose: Generate related-question suggestions in internal or testing
  scenarios.

Common request fields:

- `question`
- `dataset_ids`
- `industry`

## Notes

- These endpoints are useful for internal testing, preview tools, and source
  explanation flows.
- Keep downstream references concise; this file is meant to reduce integration
  friction, not mirror every upstream response field verbatim.
