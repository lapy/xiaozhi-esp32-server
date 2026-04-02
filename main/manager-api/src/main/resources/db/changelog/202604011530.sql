-- Finalize downstream westernization of seeded model configuration rows.
-- Remove Chinese-focused defaults that should not ship downstream and
-- relocalize the surviving generic/international integrations.

DELETE FROM `ai_model_config`
WHERE `id` IN (
  'ASR_FunASR',
  'ASR_FunASRServer',
  'LLM_AliLLM',
  'LLM_ChatGLMLLM',
  'LLM_CozeLLM',
  'LLM_FastgptLLM',
  'LLM_VolcesAiGatewayLLM',
  'TTS_ACGNTTS',
  'TTS_AliBLStreamTTS',
  'TTS_CosyVoiceSiliconflow',
  'TTS_GPT_SOVITS_V2',
  'TTS_GPT_SOVITS_V3',
  'TTS_GizwitsTTS',
  'TTS_IndexStreamTTS',
  'TTS_PaddleSpeechTTS',
  'TTS_TTS302AI',
  'VLLM_ChatGLMVLLM',
  'VLLM_QwenVLVLLM'
);

DELETE FROM `ai_tts_voice`
WHERE `tts_model_id` IN (
  'TTS_ACGNTTS',
  'TTS_AliBLStreamTTS',
  'TTS_CosyVoiceSiliconflow',
  'TTS_GPT_SOVITS_V2',
  'TTS_GPT_SOVITS_V3',
  'TTS_GizwitsTTS',
  'TTS_IndexStreamTTS',
  'TTS_PaddleSpeechTTS',
  'TTS_TTS302AI'
);

UPDATE `ai_model_config`
SET `model_name` = 'Groq Speech Recognition',
    `remark` = 'Groq ASR configuration:\n1. Visit https://console.groq.com/keys\n2. Create an API key\n3. Recommended models: whisper-large-v3-turbo or whisper-large-v3'
WHERE `id` = 'ASR_GroqASR';

UPDATE `ai_model_config`
SET `model_name` = 'DeepSeek',
    `config_json` = '{"type": "openai", "model_name": "deepseek-chat", "base_url": "https://api.deepseek.com", "api_key": "your_api_key"}',
    `remark` = 'DeepSeek configuration:\n1. Visit https://platform.deepseek.com/\n2. Create an API key\n3. Paste it into this configuration'
WHERE `id` = 'LLM_DeepSeekLLM';

UPDATE `ai_model_config`
SET `model_name` = 'Dify',
    `config_json` = '{"type": "dify", "base_url": "https://api.dify.ai/v1", "api_key": "your_api_key", "mode": "chat-messages"}',
    `remark` = 'Dify configuration:\n1. Visit https://cloud.dify.ai/\n2. Create an API key\n3. Choose a conversation mode such as chat-messages or workflows/run\n4. Configure the assistant behavior in Dify itself'
WHERE `id` = 'LLM_DifyLLM';

UPDATE `ai_model_config`
SET `model_name` = 'Google Gemini',
    `config_json` = '{"type": "gemini", "api_key": "your_api_key", "model_name": "gemini-2.0-flash", "http_proxy": "", "https_proxy": ""}',
    `remark` = 'Gemini configuration:\n1. Visit https://aistudio.google.com/apikey\n2. Create an API key\n3. Paste it into this configuration'
WHERE `id` = 'LLM_GeminiLLM';

UPDATE `ai_model_config`
SET `remark` = 'LM Studio configuration:\n1. Install LM Studio locally\n2. Download a compatible model\n3. Keep the local API server running at http://localhost:1234/v1'
WHERE `id` = 'LLM_LMStudioLLM';

UPDATE `ai_model_config`
SET `model_name` = 'Xinference Small Model',
    `remark` = 'Xinference small-model configuration:\n1. Run Xinference locally\n2. Load a compact local model\n3. Keep the service available at http://localhost:9997'
WHERE `id` = 'LLM_XinferenceSmallLLM';

UPDATE `ai_model_config`
SET `config_json` = '{"type": "mem0ai", "api_key": "your_api_key"}',
    `remark` = 'Mem0AI memory configuration:\n1. Visit https://app.mem0.ai/dashboard/api-keys\n2. Create an API key\n3. Paste it into this configuration'
WHERE `id` = 'Memory_mem0ai';

UPDATE `ai_model_config`
SET `model_name` = 'PowerMem Memory',
    `config_json` = '{"type": "powermem", "enable_user_profile": true, "llm_provider": "openai", "llm_api_key": "your_llm_api_key", "llm_model": "gpt-4.1-mini", "openai_base_url": "https://api.openai.com/v1", "embedding_provider": "openai", "embedding_api_key": "your_embedding_api_key", "embedding_model": "text-embedding-3-small", "embedding_openai_base_url": "https://api.openai.com/v1", "embedding_dims": "", "vector_store": {"provider": "sqlite", "config": {}}}',
    `remark` = 'PowerMem memory configuration using OpenAI-compatible defaults and a local SQLite vector store.'
WHERE `id` = 'Memory_powermem';

UPDATE `ai_model_config`
SET `config_json` = '{"type": "ragflow", "base_url": "http://localhost", "api_key": "your_rag_api_key"}',
    `remark` = 'See the downstream RAGFlow guide in docs/ragflow-integration.md. After deployment, copy the API key and server address from RAGFlow into this configuration.'
WHERE `id` = 'RAG_RAGFlow';

UPDATE `ai_model_config`
SET `model_name` = 'Custom TTS',
    `remark` = 'Custom TTS configuration:\n1. Point this model at your own TTS endpoint\n2. Set request parameters and headers as needed\n3. Choose the output audio format that your endpoint returns'
WHERE `id` = 'TTS_CustomTTS';

UPDATE `ai_model_config`
SET `model_name` = 'OpenAI TTS',
    `config_json` = '{"type": "openai", "api_key": "your_api_key", "api_url": "https://api.openai.com/v1/audio/speech", "model": "tts-1", "voice": "onyx", "speed": 1, "output_dir": "tmp/"}',
    `remark` = 'OpenAI TTS configuration:\n1. Visit https://platform.openai.com/api-keys\n2. Create an API key\n3. Paste it into this configuration'
WHERE `id` = 'TTS_OpenAITTS';

UPDATE `ai_tts_voice`
SET `name` = 'Default Voice',
    `languages` = 'Custom',
    `voice_demo` = NULL,
    `remark` = 'Placeholder voice for downstream custom TTS integrations.'
WHERE `id` = 'TTS_CustomTTS0000';

UPDATE `ai_tts_voice`
SET `name` = 'Onyx',
    `languages` = 'English (US)',
    `voice_demo` = NULL,
    `remark` = 'Default OpenAI voice.'
WHERE `id` = 'TTS_OpenAITTS0001';
