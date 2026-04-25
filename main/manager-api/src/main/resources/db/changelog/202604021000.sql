-- Restore a usable default VOSK model path for API-driven deployments.
-- docker-setup.sh uses config_from_api.yaml, so the final DB seed must not leave
-- ASR_VoskASR with an empty model_path.
UPDATE `ai_model_provider`
SET `fields` = '[{"key": "model_path", "type": "string", "label": "Model Path", "default": "models/vosk/vosk-model-en-us-0.22"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]'
WHERE `id` = 'SYSTEM_ASR_VoskASR';

UPDATE `ai_model_config`
SET `config_json` = JSON_SET(
    COALESCE(NULLIF(`config_json`, ''), '{}'),
    '$.type', 'vosk',
    '$.model_path', 'models/vosk/vosk-model-en-us-0.22',
    '$.output_dir', 'tmp/'
)
WHERE `id` = 'ASR_VoskASR';
