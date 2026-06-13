# RAGFlow API Classification

## Overview

RAGFlow exposes two broad API families:

- External APIs under `/api/v1`, authenticated with API keys.
- Internal console APIs under `/v1/<app_name>`, authenticated with user
  sessions or cookies.

## External API Families

| Family | Example paths | Purpose |
|---|---|---|
| Agents | `/api/v1/agents`, `/api/v1/agents/<agent_id>/sessions` | Agent lifecycle, session management, completions |
| Chats | `/api/v1/chats`, `/api/v1/chats/<chat_id>/completions` | Chat assistant lifecycle and inference |
| Datasets | `/api/v1/datasets`, `/api/v1/datasets/<dataset_id>/documents` | Knowledge base and document management |
| Files | `/api/v1/file/upload`, `/api/v1/file/list` | File storage and logical folder operations |
| SearchBot | `/api/v1/searchbots/ask`, `/api/v1/searchbots/mindmap` | Embedded search experiences |
| Session utilities | `/api/v1/sessions/ask`, `/api/v1/sessions/related_questions` | Testing and debugging helpers |
| Dify compatibility | `/api/v1/dify/retrieval` | Dify-style retrieval payloads |
| OpenAI compatibility | `/api/v1/chats_openai/...`, `/api/v1/agents_openai/...` | OpenAI-style request and stream formats |

## Internal API Families

| Family | Example paths | Purpose |
|---|---|---|
| User | `/v1/user/login`, `/v1/user/info` | Authentication and profile operations |
| API token | `/v1/api/new_token` | Console token generation |
| Conversation | `/v1/conversation/set`, `/v1/conversation/completion` | Internal chat testing |
| Knowledge base | `/v1/kb/list`, `/v1/kb/create` | Console KB management |
| Document | `/v1/document/upload`, `/v1/document/parse` | Console-side document operations |

## Practical Guidance

- Prefer the external APIs for system-to-system integrations.
- Prefer OpenAI-compatible endpoints when the client already speaks the OpenAI
  chat protocol.
- Prefer SearchBot endpoints for embedded retrieval-centric experiences.
- Treat the internal `/v1` endpoints as console-oriented and subject to more UI
  coupling.
