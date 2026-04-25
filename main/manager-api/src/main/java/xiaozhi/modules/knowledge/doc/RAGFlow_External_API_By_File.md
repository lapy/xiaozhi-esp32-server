# RAGFlow External API Reference by Source File

## `api/apps/sdk/agents.py`

- `list_agents` -> `/api/v1/agents`
- `create_agent` -> `/api/v1/agents`
- `update_agent` -> `/api/v1/agents/<agent_id>`
- `delete_agent` -> `/api/v1/agents/<agent_id>`
- `webhook` -> `/api/v1/webhook_test/<agent_id>`
- `webhook_trace` -> `/api/v1/webhook_trace/<agent_id>`

## `api/apps/sdk/chat.py`

- `create` -> `/api/v1/chats`
- `delete_chats` -> `/api/v1/chats`
- `list_chat` -> `/api/v1/chats`
- `update` -> `/api/v1/chats/<chat_id>`

## `api/apps/sdk/dataset.py`

- `create` -> `/api/v1/datasets`
- `delete` -> `/api/v1/datasets`
- `list_datasets` -> `/api/v1/datasets`
- `update` -> `/api/v1/datasets/<dataset_id>`
- `knowledge_graph` -> `/api/v1/datasets/<dataset_id>/knowledge_graph`
- `delete_knowledge_graph` -> `/api/v1/datasets/<dataset_id>/knowledge_graph`
- `run_graphrag` -> `/api/v1/datasets/<dataset_id>/run_graphrag`
- `run_raptor` -> `/api/v1/datasets/<dataset_id>/run_raptor`
- `trace_graphrag` -> `/api/v1/datasets/<dataset_id>/trace_graphrag`
- `trace_raptor` -> `/api/v1/datasets/<dataset_id>/trace_raptor`

## `api/apps/sdk/dify_retrieval.py`

- `retrieval` -> `/api/v1/dify/retrieval`

## `api/apps/sdk/doc.py`

- `parse` -> `/api/v1/datasets/<dataset_id>/chunks`
- `stop_parsing` -> `/api/v1/datasets/<dataset_id>/chunks`
- `upload` -> `/api/v1/datasets/<dataset_id>/documents`
- `list_docs` -> `/api/v1/datasets/<dataset_id>/documents`
- `delete` -> `/api/v1/datasets/<dataset_id>/documents`
- `update_doc` -> `/api/v1/datasets/<dataset_id>/documents/<document_id>`
- `download` -> `/api/v1/datasets/<dataset_id>/documents/<document_id>`
- `list_chunks` -> `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks`
- `add_chunk` -> `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks`
- `update_chunk` -> `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks/<chunk_id>`
- `rm_chunk` -> `/api/v1/datasets/<dataset_id>/documents/<document_id>/chunks`
- `metadata_summary` -> `/api/v1/datasets/<dataset_id>/metadata/summary`
- `metadata_batch_update` -> `/api/v1/datasets/<dataset_id>/metadata/update`
- `retrieval_test` -> `/api/v1/retrieval`

## `api/apps/sdk/files.py`

- `get_all_parent_folders` -> `/api/v1/file/all_parent_folder`
- `convert` -> `/api/v1/file/convert`
- `create` -> `/api/v1/file/create`
- `download_attachment` -> `/api/v1/file/download/<attachment_id>`
- `get` -> `/api/v1/file/get/<file_id>`
- `list_files` -> `/api/v1/file/list`
- `move` -> `/api/v1/file/mv`
- `get_parent_folder` -> `/api/v1/file/parent_folder`
- `rename` -> `/api/v1/file/rename`
- `rm` -> `/api/v1/file/rm`
- `get_root_folder` -> `/api/v1/file/root_folder`
- `upload` -> `/api/v1/file/upload`

## `api/apps/sdk/session.py`

- `agent_bot_completions` -> `/api/v1/agentbots/<agent_id>/completions`
- `begin_inputs` -> `/api/v1/agentbots/<agent_id>/inputs`
- `agent_completions` -> `/api/v1/agents/<agent_id>/completions`
- `create_agent_session` -> `/api/v1/agents/<agent_id>/sessions`
- `list_agent_session` -> `/api/v1/agents/<agent_id>/sessions`
- `delete_agent_session` -> `/api/v1/agents/<agent_id>/sessions`
- `agents_completion_openai_compatibility` ->
  `/api/v1/agents_openai/<agent_id>/chat/completions`
- `chatbot_completions` -> `/api/v1/chatbots/<dialog_id>/completions`
- `chatbots_inputs` -> `/api/v1/chatbots/<dialog_id>/info`
- `chat_completion` -> `/api/v1/chats/<chat_id>/completions`
- `create` -> `/api/v1/chats/<chat_id>/sessions`
- `list_session` -> `/api/v1/chats/<chat_id>/sessions`
- `delete` -> `/api/v1/chats/<chat_id>/sessions`
- `update` -> `/api/v1/chats/<chat_id>/sessions/<session_id>`
- `chat_completion_openai_like` ->
  `/api/v1/chats_openai/<chat_id>/chat/completions`
- `ask_about_embedded` -> `/api/v1/searchbots/ask`
- `detail_share_embedded` -> `/api/v1/searchbots/detail`
- `mindmap` -> `/api/v1/searchbots/mindmap`
- `related_questions_embedded` -> `/api/v1/searchbots/related_questions`
- `retrieval_test_embedded` -> `/api/v1/searchbots/retrieval_test`
- `ask_about` -> `/api/v1/sessions/ask`
- `related_questions` -> `/api/v1/sessions/related_questions`
