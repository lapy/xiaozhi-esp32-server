-- Ensure role-config dropdowns have selectable western models after westernization.
-- Re-enable core defaults when they exist but were left disabled, and turn on
-- VAD/ASR menu flags so the role-config page shows those selectors.

UPDATE `ai_model_config`
SET `is_enabled` = 1
WHERE `id` IN (
    'LLM_OpenAILLM',
    'TTS_EdgeTTS',
    'VAD_SileroVAD',
    'ASR_VoskASR',
    'ASR_GroqASR',
    'ASR_OpenaiASR',
    'Intent_function_call',
    'Memory_nomem',
    'VLLM_OpenAILLMVLLM'
)
  AND `is_enabled` = 0;

UPDATE `ai_model_config`
SET `config_json` = JSON_SET(CAST(`config_json` AS JSON), '$.llm', 'LLM_OpenAILLM')
WHERE `id` = 'Memory_mem_local_short'
  AND JSON_UNQUOTE(JSON_EXTRACT(CAST(`config_json` AS JSON), '$.llm')) = 'LLM_ChatGLMLLM';

UPDATE `sys_params`
SET `param_value` = CAST(
    JSON_SET(
        CAST(`param_value` AS JSON),
        '$.features.vad.enabled', TRUE,
        '$.features.asr.enabled', TRUE
    ) AS CHAR
)
WHERE `param_code` = 'system-web.menu';
