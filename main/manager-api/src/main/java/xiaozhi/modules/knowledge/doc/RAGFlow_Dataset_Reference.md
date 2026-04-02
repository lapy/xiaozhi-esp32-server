# RAGFlow Dataset API Reference

## Scope

Datasets are the top-level knowledge base objects in RAGFlow.

## Core Endpoints

### `create`

- Method: `POST`
- Path: `/api/v1/datasets`
- Purpose: Create a dataset.

Typical body fields:

- `name`
- `description`
- `embedding_model`
- `permission`

### `list_datasets`

- Method: `GET`
- Path: `/api/v1/datasets`
- Purpose: List datasets with filters and paging.

Common query fields:

- `page`
- `page_size`
- `orderby`
- `desc`
- `id`
- `name`

### `update`

- Method: `PUT`
- Path: `/api/v1/datasets/<dataset_id>`
- Purpose: Update dataset metadata and settings.

### `delete`

- Method: `DELETE`
- Path: `/api/v1/datasets`
- Purpose: Delete one or more datasets.

Common body field:

- `ids`

## Graph and Advanced Retrieval Endpoints

### `knowledge_graph`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/knowledge_graph`
- Purpose: Return knowledge graph data for a dataset.

### `delete_knowledge_graph`

- Method: `DELETE`
- Path: `/api/v1/datasets/<dataset_id>/knowledge_graph`
- Purpose: Remove graph artifacts for a dataset.

### `run_graphrag`

- Method: `POST`
- Path: `/api/v1/datasets/<dataset_id>/run_graphrag`
- Purpose: Start a GraphRAG job.

### `run_raptor`

- Method: `POST`
- Path: `/api/v1/datasets/<dataset_id>/run_raptor`
- Purpose: Start a Raptor job.

### `trace_graphrag`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/trace_graphrag`
- Purpose: Inspect GraphRAG execution state.

### `trace_raptor`

- Method: `GET`
- Path: `/api/v1/datasets/<dataset_id>/trace_raptor`
- Purpose: Inspect Raptor execution state.

## Typical Returned Fields

- `id`
- `name`
- `description`
- `document_count`
- `chunk_count`
- `embedding_model`
- `permission`
- `create_time`
- `update_time`

## Notes

- Dataset behavior is tightly connected to the document endpoints.
- Keep downstream examples provider-neutral and infrastructure-neutral.
