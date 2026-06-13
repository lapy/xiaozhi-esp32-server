# RAGFlow Document API Reference

## Scope

This document summarizes document ingestion, chunk management, and retrieval
testing under a dataset.

## Core Document Endpoints

### `upload`

- Method: `POST`
- Path: `/api/v1/datasets/<dataset_id>/documents`
- Purpose: Upload one or more documents into a dataset.

### `list_docs`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/documents`
- Purpose: List documents and parsing status.

Common query fields:

- `page`
- `page_size`
- `orderby`
- `desc`
- `keywords`
- `run`
- `create_time_from`
- `create_time_to`

### `update_doc`

- Method: `PUT`
- Path: `/api/v1/datasets/<dataset_id>/documents/<document_id>`
- Purpose: Update parsing configuration or metadata for a document.

### `delete`

- Method: `DELETE`
- Path: `/api/v1/datasets/<dataset_id>/documents`
- Purpose: Delete one or more documents.

### `download`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/documents/<document_id>`
- Purpose: Download the original stored document.

## Parsing and Chunk Endpoints

### `parse`

- Method: `POST`
- Path: `/api/v1/datasets/<dataset_id>/chunks`
- Purpose: Start document parsing or chunk generation jobs.

### `stop_parsing`

- Method: `DELETE`
- Path: `/api/v1/datasets/<dataset_id>/chunks`
- Purpose: Cancel parsing jobs.

### `list_chunks`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks`
- Purpose: List generated chunks for a document.

### `add_chunk`

- Method: `POST`
- Path: `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks`
- Purpose: Add a manual chunk.

### `update_chunk`

- Method: `PUT`
- Path: `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks/<chunk_id>`
- Purpose: Update a specific chunk.

### `rm_chunk`

- Method: `DELETE`
- Path: `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks`
- Purpose: Remove selected chunks.

## Metadata and Retrieval

### `metadata_summary`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/metadata/summary`
- Purpose: Return metadata facets or summary statistics.

### `metadata_batch_update`

- Method: `POST`
- Path: `/api/v1/datasets/<dataset_id>/metadata/update`
- Purpose: Update metadata across multiple records.

### `retrieval_test`

- Method: `POST`
- Path: `/api/v1/retrieval`
- Purpose: Run retrieval only, without a final LLM answer.

## Typical Returned Fields

- `id`
- `dataset_id`
- `name`
- `type`
- `run`
- `parser_config`
- `token_count`
- `chunk_count`
- `create_time`
- `update_time`

## Notes

- Parsing configuration is a major source of upstream churn, so keep this
  document summary-based rather than exhaustive.
