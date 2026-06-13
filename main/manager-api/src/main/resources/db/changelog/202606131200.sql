-- Westernize upstream web search and device calling plugin seeds added after the prior cleanup queue.
UPDATE `ai_model_provider`
SET `name` = 'Web Search',
    `fields` = '[{"key": "provider", "type": "string", "label": "Search provider: metaso / tavily", "default": "metaso", "editing": false, "selected": false}, {"key": "description", "type": "string", "label": "Tool description", "default": "Web search tool. Use when the user explicitly asks for current information from the internet.", "editing": false, "selected": false}, {"key": "max_results", "type": "string", "label": "Result count", "default": "5", "editing": false, "selected": false}, {"key": "api_key", "type": "string", "label": "API key", "default": "mk-XXXX", "editing": false, "selected": false}]'
WHERE `id` = 'SYSTEM_PLUGIN_WEB_SEARCH';

UPDATE `ai_model_provider`
SET `name` = 'Device Calling'
WHERE `id` = 'SYSTEM_PLUGIN_CALL_DEVICE';

-- Remove upstream Chinese-only provider seeds reintroduced after the earlier westernization queue.
DELETE FROM `ai_tts_voice` WHERE `tts_model_id` IN ('ASR_DoubaoStreamASRV2', 'TTS_HSDSTTS_V2');
DELETE FROM `ai_model_config` WHERE `id` IN ('ASR_DoubaoStreamASRV2', 'TTS_HSDSTTS_V2');
DELETE FROM `ai_model_provider` WHERE `id` IN ('SYSTEM_ASR_DoubaoStreamASRV2', 'SYSTEM_TTS_HSDSTTS_V2');
