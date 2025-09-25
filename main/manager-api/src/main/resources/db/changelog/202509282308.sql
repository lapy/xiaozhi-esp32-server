--
-- Update default providers: WhisperASR for STT, LMStudioLLM for LLM, EdgeTTS for TTS
-- Migration date: 2025-09-28 23:08
-- Note: WhisperASR is already defined in 202509270000.sql
-- Also removes Chinese AI providers
--

-- Remove Chinese AI providers from ai_model_config
DELETE FROM `ai_model_config` WHERE `id` IN ('ASR_SherpaSenseVoiceASR');
DELETE FROM `ai_model_provider` WHERE `id` IN ('SYSTEM_ASR_SherpaSenseVoiceASR');

-- Update default configurations: Set WhisperASR as default ASR
UPDATE `ai_model_config` SET `is_default` = 0 WHERE `model_type` = 'ASR';
UPDATE `ai_model_config` SET `is_default` = 1 WHERE `id` = 'ASR_WhisperASR';

-- Update default configurations: Set LMStudioLLM as default LLM
UPDATE `ai_model_config` SET `is_default` = 0 WHERE `model_type` = 'LLM';
UPDATE `ai_model_config` SET `is_default` = 1 WHERE `id` = 'LLM_LMStudioLLM';

-- Update default configurations: Ensure EdgeTTS remains default TTS
UPDATE `ai_model_config` SET `is_default` = 0 WHERE `model_type` = 'TTS';
UPDATE `ai_model_config` SET `is_default` = 1 WHERE `id` = 'TTS_EdgeTTS';

-- Update agent templates to use new default providers
UPDATE `ai_agent_template` SET `asr_model_id` = 'ASR_WhisperASR' WHERE `asr_model_id` = 'ASR_VoskASR';
UPDATE `ai_agent_template` SET `llm_model_id` = 'LLM_LMStudioLLM' WHERE `llm_model_id` = 'LLM_OpenAILLM';
-- TTS is already EdgeTTS, so no change needed
