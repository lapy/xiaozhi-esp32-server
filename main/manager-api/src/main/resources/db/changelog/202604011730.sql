-- Restore non-Chinese-safe seed entries that exist on downstream origin/main
-- but were not yet ported into the append-only westernization stack.
-- Keep deleted Chinese-focused integrations deleted while preserving the
-- western/non-Chinese-safe provider surface in the latest table shape.

INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 901, 'twilio.sms.account_sid', '', 'string', 1, 'Twilio Account SID for SMS service', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'twilio.sms.account_sid');

INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 902, 'twilio.sms.auth_token', '', 'string', 1, 'Twilio Auth Token for SMS service', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'twilio.sms.auth_token');

INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 903, 'twilio.sms.phone_number', '', 'string', 1, 'Twilio phone number for sending SMS messages', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'twilio.sms.phone_number');

INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 904, 'twilio.sms.template_message', 'Your verification code is: %s', 'string', 1, 'Twilio SMS template message with %s placeholder for verification code', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'twilio.sms.template_message');

INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`)
SELECT src.`id`, src.`model_type`, src.`provider_code`, src.`name`, src.`fields`, src.`sort`, src.`creator`, src.`create_date`, src.`updater`, src.`update_date`
FROM (
    SELECT 'SYSTEM_ASR_GeminiASR' AS `id`, 'ASR' AS `model_type`, 'gemini' AS `provider_code`, 'Gemini Speech Recognition' AS `name`,
           '[{"key": "api_key", "type": "string", "label": "API Key"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}, {"key": "http_proxy", "type": "string", "label": "HTTP Proxy"}, {"key": "https_proxy", "type": "string", "label": "HTTPS Proxy"}]' AS `fields`,
           11 AS `sort`, 1 AS `creator`, '2025-09-27 00:00:00' AS `create_date`, 1 AS `updater`, '2025-09-27 00:00:00' AS `update_date`
    UNION ALL
    SELECT 'SYSTEM_ASR_GroqASR', 'ASR', 'openai', 'Groq Speech Recognition',
           '[{"key": "base_url", "type": "string", "label": "Base URL"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]',
           10, 1, '2025-09-25 15:16:45', 1, '2025-09-25 15:16:45'
    UNION ALL
    SELECT 'SYSTEM_ASR_WhisperASR', 'ASR', 'whisper', 'OpenAI Whisper Speech Recognition',
           '[{"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "device", "type": "string", "label": "Device (auto/cpu/cuda)"}, {"key": "language", "type": "string", "label": "Language (null for auto-detect)"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]',
           12, 1, '2025-09-27 00:00:00', 1, '2025-09-27 00:00:00'
    UNION ALL
    SELECT 'SYSTEM_PLUGIN_HA_GET_CALENDAR', 'Plugin', 'get_calendar', 'Standard Calendar Information Service',
           '[]',
           8, 1, '2025-09-29 11:42:00', 1, '2025-09-29 11:42:00'
    UNION ALL
    SELECT 'SYSTEM_PLUGIN_CHANGE_ROLE', 'Plugin', 'change_role', 'Role Switching Service',
           '[{"key": "available_roles", "type": "string", "label": "Available Roles", "default": "sassy_girlfriend,english_teacher,curious_kid", "description": "Comma-separated list of available roles for switching"}]',
           9, 1, '2025-09-29 11:42:00', 1, '2025-09-29 11:42:00'
    UNION ALL
    SELECT 'SYSTEM_TTS_elevenlabs', 'TTS', 'elevenlabs', 'ElevenLabs TTS',
           '[{"key": "api_key", "type": "string", "label": "API Key"}, {"key": "api_url", "type": "string", "label": "API URL"}, {"key": "voice_id", "type": "string", "label": "Voice ID"}, {"key": "model_id", "type": "string", "label": "Model ID"}, {"key": "stability", "type": "number", "label": "Stability"}, {"key": "similarity_boost", "type": "number", "label": "Similarity Boost"}, {"key": "style", "type": "number", "label": "Style"}, {"key": "use_speaker_boost", "type": "boolean", "label": "Use Speaker Boost"}, {"key": "optimize_streaming_latency", "type": "number", "label": "Optimize Streaming Latency"}, {"key": "output_format", "type": "string", "label": "Output Format"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]',
           15, 1, '2025-10-02 14:30:00', 1, '2025-10-02 14:30:00'
    UNION ALL
    SELECT 'SYSTEM_TTS_kokoro', 'TTS', 'kokoro', 'Kokoro TTS',
           '[{"key": "use_api", "type": "boolean", "label": "Use API Mode"}, {"key": "api_url", "type": "string", "label": "API URL"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "model", "type": "string", "label": "Model"}, {"key": "voice", "type": "string", "label": "Voice"}, {"key": "language", "type": "string", "label": "Language"}, {"key": "speed", "type": "number", "label": "Speech Speed"}, {"key": "response_format", "type": "string", "label": "Response Format"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]',
           17, 1, '2025-10-02 15:00:00', 1, '2025-10-02 15:00:00'
) AS src
WHERE NOT EXISTS (SELECT 1 FROM `ai_model_provider` existing WHERE existing.`id` = src.`id`);

INSERT INTO `ai_model_config` (`id`, `model_type`, `model_code`, `model_name`, `is_default`, `is_enabled`, `config_json`, `doc_link`, `remark`, `sort`, `creator`, `create_date`, `updater`, `update_date`)
SELECT src.`id`, src.`model_type`, src.`model_code`, src.`model_name`, src.`is_default`, src.`is_enabled`, src.`config_json`, src.`doc_link`, src.`remark`, src.`sort`, src.`creator`, src.`create_date`, src.`updater`, src.`update_date`
FROM (
    SELECT 'ASR_GeminiASR' AS `id`, 'ASR' AS `model_type`, 'GeminiASR' AS `model_code`, 'Gemini Speech Recognition' AS `model_name`,
           0 AS `is_default`, 0 AS `is_enabled`,
           '{"type": "gemini", "api_key": "", "model_name": "gemini-2.0-flash-exp", "output_dir": "tmp/", "http_proxy": "", "https_proxy": ""}' AS `config_json`,
           'https://aistudio.google.com/apikey' AS `doc_link`,
           'Gemini ASR configuration:\n1. Visit https://aistudio.google.com/apikey\n2. Create an API key\n3. Paste it into this configuration\n4. Choose a Gemini audio-capable model for speech-to-text tasks' AS `remark`,
           11 AS `sort`, NULL AS `creator`, NULL AS `create_date`, NULL AS `updater`, NULL AS `update_date`
    UNION ALL
    SELECT 'ASR_WhisperASR', 'ASR', 'WhisperASR', 'OpenAI Whisper Speech Recognition',
           1, 0,
           '{"type": "whisper", "model_name": "base", "device": "auto", "language": null, "output_dir": "tmp/"}',
           'https://github.com/openai/whisper',
           'Whisper ASR configuration:\n1. Runs locally after model download\n2. Supports multilingual speech recognition\n3. Choose a model based on your speed and accuracy needs\n4. Output files are written to tmp/',
           12, NULL, NULL, NULL, NULL
    UNION ALL
    SELECT 'LLM_OpenAILLM', 'LLM', 'OpenAILLM', 'OpenAI GPT',
           1, 1,
           '{"type": "openai", "api_key": "your_api_key", "model_name": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 500}',
           'https://platform.openai.com/api-keys',
           'OpenAI configuration:\n1. Visit https://platform.openai.com/api-keys\n2. Create an API key\n3. Paste it into this configuration',
           1, NULL, NULL, NULL, NULL
    UNION ALL
    SELECT 'TTS_ElevenLabsTTS', 'TTS', 'ElevenLabsTTS', 'ElevenLabs TTS',
           0, 1,
           '{"type": "elevenlabs", "api_key": "your_elevenlabs_api_key", "api_url": "https://api.elevenlabs.io/v1/text-to-speech", "voice_id": "21m00Tcm4TlvDq8ikWAM", "model_id": "eleven_turbo_v2_5", "stability": 0.5, "similarity_boost": 0.5, "style": 0.0, "use_speaker_boost": true, "optimize_streaming_latency": 0, "output_format": "mp3_44100_128", "output_dir": "tmp/"}',
           'https://elevenlabs.io/',
           'ElevenLabs TTS configuration:\n1. Visit https://elevenlabs.io/\n2. Create an API key\n3. Choose a voice and model\n4. Adjust stability, similarity boost, and style to fit your use case',
           15, NULL, NULL, NULL, NULL
    UNION ALL
    SELECT 'TTS_KokoroTTS', 'TTS', 'KokoroTTS', 'Kokoro TTS',
           0, 1,
           '{"type": "kokoro", "use_api": false, "api_url": "http://localhost:8000/api/v1/audio/speech", "api_key": "", "model": "model_fp32", "voice": "af_heart", "language": "en-us", "speed": 1.0, "response_format": "mp3", "output_dir": "tmp/"}',
           'https://pypi.org/project/kokoro-tts/',
           'Kokoro TTS configuration:\n1. Supports local package mode and API mode\n2. Uses English-first defaults downstream\n3. Choose a supported voice such as af_heart or af_sarah\n4. Adjust speed and response format as needed',
           17, NULL, NULL, NULL, NULL
    UNION ALL
    SELECT 'VLLM_GeminiVLLM', 'VLLM', 'GeminiVLLM', 'Google Gemini Vision AI',
           0, 1,
           '{"type": "gemini", "api_key": "your_api_key", "model_name": "gemini-1.5-pro"}',
           'https://makersuite.google.com/app/apikey',
           'Gemini Vision configuration:\n1. Visit https://makersuite.google.com/app/apikey\n2. Create an API key\n3. Paste it into this configuration',
           1, NULL, NULL, NULL, NULL
    UNION ALL
    SELECT 'VLLM_OpenAILLMVLLM', 'VLLM', 'OpenAILLMVLLM', 'OpenAI Vision Model',
           1, 1,
           '{"type": "openai", "api_key": "your_api_key", "model_name": "gpt-4o"}',
           'https://platform.openai.com/api-keys',
           'OpenAI Vision configuration:\n1. Visit https://platform.openai.com/api-keys\n2. Create an API key\n3. Paste it into this configuration',
           2, NULL, NULL, NULL, NULL
) AS src
WHERE NOT EXISTS (SELECT 1 FROM `ai_model_config` existing WHERE existing.`id` = src.`id`);

INSERT INTO `ai_tts_voice` (`id`, `tts_model_id`, `name`, `tts_voice`, `languages`, `voice_demo`, `remark`, `reference_audio`, `reference_text`, `sort`, `creator`, `create_date`, `updater`, `update_date`)
SELECT src.`id`, src.`tts_model_id`, src.`name`, src.`tts_voice`, src.`languages`, src.`voice_demo`, src.`remark`, src.`reference_audio`, src.`reference_text`, src.`sort`, src.`creator`, src.`create_date`, src.`updater`, src.`update_date`
FROM (
    SELECT 'TTS_EdgeTTS_EN004' AS `id`, 'TTS_EdgeTTS' AS `tts_model_id`, 'Jenny' AS `name`, 'en-US-JennyNeural' AS `tts_voice`, 'English (US)' AS `languages`, NULL AS `voice_demo`, NULL AS `remark`, NULL AS `reference_audio`, NULL AS `reference_text`, 4 AS `sort`, NULL AS `creator`, NULL AS `create_date`, NULL AS `updater`, NULL AS `update_date`
    UNION ALL SELECT 'TTS_EdgeTTS_EN005', 'TTS_EdgeTTS', 'Davis', 'en-US-DavisNeural', 'English (US)', NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_EdgeTTS_EN006', 'TTS_EdgeTTS', 'Emma', 'en-GB-EmmaNeural', 'English (UK)', NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_EdgeTTS_EN007', 'TTS_EdgeTTS', 'Ryan', 'en-GB-RyanNeural', 'English (UK)', NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_EdgeTTS_EN008', 'TTS_EdgeTTS', 'Libby', 'en-GB-LibbyNeural', 'English (UK)', NULL, NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_EdgeTTS_EN009', 'TTS_EdgeTTS', 'Natasha', 'en-AU-NatashaNeural', 'English (AU)', NULL, NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_EdgeTTS_EN010', 'TTS_EdgeTTS', 'William', 'en-AU-WilliamNeural', 'English (AU)', NULL, NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_OpenAITTS0002', 'TTS_OpenAITTS', 'Alloy', 'alloy', 'English (US)', NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_OpenAITTS0003', 'TTS_OpenAITTS', 'Echo', 'echo', 'English (US)', NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_OpenAITTS0004', 'TTS_OpenAITTS', 'Fable', 'fable', 'English (UK)', NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_OpenAITTS0005', 'TTS_OpenAITTS', 'Nova', 'nova', 'English (US)', NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_OpenAITTS0006', 'TTS_OpenAITTS', 'Shimmer', 'shimmer', 'English (US)', NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0001', 'TTS_ElevenLabsTTS', 'Rachel', '21m00Tcm4TlvDq8ikWAM', 'American English - Calm, Young Adult Female', NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0002', 'TTS_ElevenLabsTTS', 'Adam', 'pNInz6obpgDQGcFmaJgB', 'American English - Deep, Middle-aged Male', NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0003', 'TTS_ElevenLabsTTS', 'Antoni', 'ErXwobaYiN019PkySvjV', 'American English - Well-rounded, Middle-aged Male', NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0004', 'TTS_ElevenLabsTTS', 'Arnold', 'VR6AewLTigWG4xSOukaG', 'American English - Crisp, Middle-aged Male', NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0005', 'TTS_ElevenLabsTTS', 'Bella', 'EXAVITQu4vr4xnSDxMaL', 'American English - Soft, Young Adult Female', NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0006', 'TTS_ElevenLabsTTS', 'Domi', 'AZnzlk1XvdvUeBnXmlld', 'American English - Strong, Young Adult Female', NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0007', 'TTS_ElevenLabsTTS', 'Elli', 'MF3mGyEYCl7XYWbV9V6O', 'American English - Emotional, Young Adult Female', NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0008', 'TTS_ElevenLabsTTS', 'Josh', 'TxGEqnHWrfWFTfGW9XjX', 'American English - Deep, Young Adult Male', NULL, NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0009', 'TTS_ElevenLabsTTS', 'Sam', 'yoZ06aMxZJJ28mfd3POQ', 'American English - Raspy, Young Adult Male', NULL, NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0010', 'TTS_ElevenLabsTTS', 'Matilda', 'XrExE9yKIg1WjnnlVkGX', 'American English - Warm, Middle-aged Female', NULL, NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0011', 'TTS_ElevenLabsTTS', 'Matthew', 'Yko7PKHZNXotIFUBG7I9', 'British English - Clear, Middle-aged Male', NULL, NULL, NULL, NULL, 11, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0012', 'TTS_ElevenLabsTTS', 'James', 'ZQe5CqHNLWdS2F4s9BqK', 'Australian English - Calm, Young Adult Male', NULL, NULL, NULL, NULL, 12, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0013', 'TTS_ElevenLabsTTS', 'Hope', 'uYXf8XasLslADfZ2MB4u', 'American English - Friendly, Engaging Female', NULL, NULL, NULL, NULL, 13, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0014', 'TTS_ElevenLabsTTS', 'Daniel', 'onwK6e5U6N7xDrBOmXO', 'British English - Energetic, Enthusiastic Male', NULL, NULL, NULL, NULL, 14, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0015', 'TTS_ElevenLabsTTS', 'Lily', 'pFZP5JQG7iQjIQuC4Bku', 'British English - Warm, Pleasant Female', NULL, NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0016', 'TTS_ElevenLabsTTS', 'Freya', 'jsCqWAovK2LkecY7zXl4', 'American English - Confident, Professional Female', NULL, NULL, NULL, NULL, 16, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0017', 'TTS_ElevenLabsTTS', 'Charlie', 'IK2y5XjIqaOfvMWOhSXy', 'Australian English - Casual, Friendly Male', NULL, NULL, NULL, NULL, 17, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_ElevenLabs_0018', 'TTS_ElevenLabsTTS', 'Grace', 'oWAxZDx7w5VEj9dCyTzz', 'American English - Gentle, Soothing Female', NULL, NULL, NULL, NULL, 18, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0001', 'TTS_KokoroTTS', 'Alloy', 'af_alloy', 'American English - Versatile female voice', NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0002', 'TTS_KokoroTTS', 'Aoede', 'af_aoede', 'American English - Melodic female voice', NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0003', 'TTS_KokoroTTS', 'Bella', 'af_bella', 'American English - Soft, gentle female voice', NULL, NULL, NULL, NULL, 3, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0004', 'TTS_KokoroTTS', 'Heart', 'af_heart', 'American English - Warm, expressive female voice', NULL, NULL, NULL, NULL, 4, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0005', 'TTS_KokoroTTS', 'Jessica', 'af_jessica', 'American English - Professional female voice', NULL, NULL, NULL, NULL, 5, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0006', 'TTS_KokoroTTS', 'Kore', 'af_kore', 'American English - Dynamic female voice', NULL, NULL, NULL, NULL, 6, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0007', 'TTS_KokoroTTS', 'Nicole', 'af_nicole', 'American English - Clear female voice', NULL, NULL, NULL, NULL, 7, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0008', 'TTS_KokoroTTS', 'Nova', 'af_nova', 'American English - Bright female voice', NULL, NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0009', 'TTS_KokoroTTS', 'River', 'af_river', 'American English - Flowing female voice', NULL, NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0010', 'TTS_KokoroTTS', 'Sarah', 'af_sarah', 'American English - Professional female voice', NULL, NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0011', 'TTS_KokoroTTS', 'Sky', 'af_sky', 'American English - Light female voice', NULL, NULL, NULL, NULL, 11, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0012', 'TTS_KokoroTTS', 'Adam', 'am_adam', 'American English - Deep, confident male voice', NULL, NULL, NULL, NULL, 12, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0013', 'TTS_KokoroTTS', 'Echo', 'am_echo', 'American English - Resonant male voice', NULL, NULL, NULL, NULL, 13, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0014', 'TTS_KokoroTTS', 'Eric', 'am_eric', 'American English - Friendly male voice', NULL, NULL, NULL, NULL, 14, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0015', 'TTS_KokoroTTS', 'Fenrir', 'am_fenrir', 'American English - Strong male voice', NULL, NULL, NULL, NULL, 15, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0016', 'TTS_KokoroTTS', 'Liam', 'am_liam', 'American English - Smooth male voice', NULL, NULL, NULL, NULL, 16, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0017', 'TTS_KokoroTTS', 'Michael', 'am_michael', 'American English - Conversational male voice', NULL, NULL, NULL, NULL, 17, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0018', 'TTS_KokoroTTS', 'Onyx', 'am_onyx', 'American English - Rich male voice', NULL, NULL, NULL, NULL, 18, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0019', 'TTS_KokoroTTS', 'Puck', 'am_puck', 'American English - Playful male voice', NULL, NULL, NULL, NULL, 19, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0020', 'TTS_KokoroTTS', 'Alice', 'bf_alice', 'British English - Elegant female voice', NULL, NULL, NULL, NULL, 20, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0021', 'TTS_KokoroTTS', 'Emma', 'bf_emma', 'British English - Refined female voice', NULL, NULL, NULL, NULL, 21, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0022', 'TTS_KokoroTTS', 'Isabella', 'bf_isabella', 'British English - Sophisticated female voice', NULL, NULL, NULL, NULL, 22, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0023', 'TTS_KokoroTTS', 'Lily', 'bf_lily', 'British English - Gentle female voice', NULL, NULL, NULL, NULL, 23, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0024', 'TTS_KokoroTTS', 'Daniel', 'bm_daniel', 'British English - Distinguished male voice', NULL, NULL, NULL, NULL, 24, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0025', 'TTS_KokoroTTS', 'Fable', 'bm_fable', 'British English - Storytelling male voice', NULL, NULL, NULL, NULL, 25, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0026', 'TTS_KokoroTTS', 'George', 'bm_george', 'British English - Classic male voice', NULL, NULL, NULL, NULL, 26, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0027', 'TTS_KokoroTTS', 'Lewis', 'bm_lewis', 'British English - Modern male voice', NULL, NULL, NULL, NULL, 27, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0028', 'TTS_KokoroTTS', 'Alpha', 'jf_alpha', 'Japanese - Natural female voice', NULL, NULL, NULL, NULL, 28, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0029', 'TTS_KokoroTTS', 'Gongitsune', 'jf_gongitsune', 'Japanese - Expressive female voice', NULL, NULL, NULL, NULL, 29, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0030', 'TTS_KokoroTTS', 'Nezumi', 'jf_nezumi', 'Japanese - Sweet female voice', NULL, NULL, NULL, NULL, 30, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0031', 'TTS_KokoroTTS', 'Tebukuro', 'jf_tebukuro', 'Japanese - Gentle female voice', NULL, NULL, NULL, NULL, 31, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0032', 'TTS_KokoroTTS', 'Kumo', 'jm_kumo', 'Japanese - Strong male voice', NULL, NULL, NULL, NULL, 32, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0041', 'TTS_KokoroTTS', 'Siwis', 'ff_siwis', 'French - Elegant female voice', NULL, NULL, NULL, NULL, 41, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0042', 'TTS_KokoroTTS', 'Sara', 'if_sara', 'Italian - Melodic female voice', NULL, NULL, NULL, NULL, 42, NULL, NULL, NULL, NULL
    UNION ALL SELECT 'TTS_Kokoro_0043', 'TTS_KokoroTTS', 'Nicola', 'im_nicola', 'Italian - Expressive male voice', NULL, NULL, NULL, NULL, 43, NULL, NULL, NULL, NULL
) AS src
WHERE NOT EXISTS (SELECT 1 FROM `ai_tts_voice` existing WHERE existing.`id` = src.`id`);
