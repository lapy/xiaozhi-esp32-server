-- Align seeded database defaults with the downstream westernization policy.
-- Keep upstream changelog history append-only while removing seeded
-- Chinese-facing defaults that can still surface in the admin UI.

-- Replace seeded Chinese EdgeTTS voices with a compact English-first set.
DELETE FROM `ai_tts_voice`
WHERE `tts_model_id` = 'TTS_EdgeTTS'
  AND (
    `tts_voice` LIKE 'zh-CN-%'
    OR `tts_voice` LIKE 'zh-HK-%'
  );

DELETE FROM `ai_tts_voice`
WHERE `id` IN (
  'TTS_EdgeTTS_EN001',
  'TTS_EdgeTTS_EN002',
  'TTS_EdgeTTS_EN003'
);

INSERT INTO `ai_tts_voice` VALUES
('TTS_EdgeTTS_EN001', 'TTS_EdgeTTS', 'Aria', 'en-US-AriaNeural', 'English (US)', NULL, 'Default downstream Edge voice', NULL, NULL, 1, NULL, NULL, NULL, NULL),
('TTS_EdgeTTS_EN002', 'TTS_EdgeTTS', 'Guy', 'en-US-GuyNeural', 'English (US)', NULL, 'Alternative downstream Edge voice', NULL, NULL, 2, NULL, NULL, NULL, NULL),
('TTS_EdgeTTS_EN003', 'TTS_EdgeTTS', 'Sonia', 'en-GB-SoniaNeural', 'English (UK)', NULL, 'Alternative downstream Edge voice', NULL, NULL, 3, NULL, NULL, NULL, NULL);

UPDATE `ai_model_config`
SET
  `model_name` = 'Edge TTS',
  `config_json` = JSON_SET(`config_json`, '$.voice', 'en-US-AriaNeural'),
  `remark` = 'Microsoft Edge TTS. Use a supported Edge voice such as en-US-AriaNeural and keep generated audio in tmp/.'
WHERE `id` = 'TTS_EdgeTTS';

-- Restore downstream English names for memory models after upstream relabeling.
UPDATE `ai_model_config`
SET
  `model_name` = 'Local short-term memory',
  `remark` = 'Summarizes short-term conversational memory locally.'
WHERE `id` = 'Memory_mem_local_short';

UPDATE `ai_model_provider`
SET `name` = 'Local short-term memory'
WHERE `id` = 'SYSTEM_Memory_mem_local_short';

UPDATE `ai_model_config`
SET
  `model_name` = 'Report-only memory',
  `remark` = 'Uploads chat records without generating memory summaries.'
WHERE `id` = 'Memory_mem_report_only';

UPDATE `ai_model_provider`
SET `name` = 'Report-only memory'
WHERE `id` = 'SYSTEM_Memory_mem_report_only';

-- Replace Chinese wakeword defaults with downstream English-first examples.
UPDATE `sys_params`
SET `param_value` = 'hello assistant;hey assistant;hey computer;jarvis;alexa'
WHERE `param_code` = 'wakeup_words';

-- Remove the original seeded Chinese agent templates from downstream defaults.
DELETE FROM `ai_agent_template`
WHERE `id` IN (
  '9406648b5cc5fde1b8aa335b6f8b4f76',
  '0ca32eb728c949e58b1000b2e401f90c',
  '6c7d8e9f0a1b2c3d4e5f6a7b8c9d0s24',
  'e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b1',
  'a45b6c7d8e9f0a1b2c3d4e5f6a7b8c92'
);
