-- Bridge the remaining gap between the downstream append-only strategy
-- and the broader English-first seed coverage from origin/main.
-- Keep downstream-deleted providers deleted while normalizing the
-- surviving seeded defaults, dictionaries, plugin metadata, and
-- built-in templates.

-- Keep Sherpa removed downstream because the runtime integration was deleted.
DELETE FROM `ai_model_provider`
WHERE `id` = 'SYSTEM_ASR_SherpaASR';

DELETE FROM `ai_model_config`
WHERE `id` = 'ASR_SherpaASR';

-- Replace the remaining Chinese-facing seeded parameter values and remarks.
UPDATE `sys_params` SET `remark` = 'System name' WHERE `param_code` = 'server.name';
UPDATE `sys_params` SET `remark` = 'ICP filing number, set to null to disable' WHERE `param_code` = 'server.beian_icp_num';
UPDATE `sys_params` SET `remark` = 'Public security filing number, set to null to disable' WHERE `param_code` = 'server.beian_ga_num';
UPDATE `sys_params` SET `remark` = 'Whether to enable mobile phone registration' WHERE `param_code` = 'server.enable_mobile_register';
UPDATE `sys_params` SET `remark` = 'Maximum SMS messages per phone number per day' WHERE `param_code` = 'server.sms_max_send_count';
UPDATE `sys_params` SET `remark` = 'Alibaba Cloud Access Key ID for SMS service' WHERE `param_code` = 'aliyun.sms.access_key_id';
UPDATE `sys_params` SET `remark` = 'Alibaba Cloud Access Key Secret for SMS service' WHERE `param_code` = 'aliyun.sms.access_key_secret';
UPDATE `sys_params` SET `remark` = 'Alibaba Cloud SMS sign name' WHERE `param_code` = 'aliyun.sms.sign_name';
UPDATE `sys_params` SET `remark` = 'Alibaba Cloud SMS template code' WHERE `param_code` = 'aliyun.sms.sms_code_template_code';
UPDATE `sys_params` SET `param_value` = 'exit;close', `remark` = 'Exit command list' WHERE `param_code` = 'exit_commands';
UPDATE `sys_params` SET `remark` = 'Whether to enable end notification sound' WHERE `param_code` = 'enable_stop_tts_notify';
UPDATE `sys_params` SET `remark` = 'End notification sound file path' WHERE `param_code` = 'stop_tts_notify_voice';
UPDATE `sys_params` SET `remark` = 'Xiaozhi type' WHERE `param_code` = 'xiaozhi';
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 400, 'plugins.get_weather.api_key', 'your_openweathermap_api_key', 'string', 1, 'Weather plugin API key', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.get_weather.api_key');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 401, 'plugins.get_weather.default_location', 'New York', 'string', 1, 'Weather plugin default location', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.get_weather.default_location');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 402, 'plugins.get_weather.api_host', 'api.openweathermap.org', 'string', 1, 'Weather plugin API host', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.get_weather.api_host');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 410, 'plugins.get_news.default_rss_url', 'https://feeds.reuters.com/reuters/worldNews', 'string', 1, 'News plugin fallback RSS URL', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.get_news.default_rss_url');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 411, 'plugins.get_news.category_urls', '{"world":"https://feeds.reuters.com/reuters/worldNews","technology":"https://feeds.feedburner.com/TechCrunch/","business":"https://feeds.marketwatch.com/marketwatch/topstories/"}', 'json', 1, 'News plugin category RSS URLs', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.get_news.category_urls');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 421, 'plugins.home_assistant.devices', 'Living Room,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;Bedroom,Table Lamp,switch.iot_cn_831898993_socn1_on_p_2_1', 'array', 1, 'Home Assistant device list', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.home_assistant.devices');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 422, 'plugins.home_assistant.base_url', 'http://homeassistant.local:8123', 'string', 1, 'Home Assistant server address', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.home_assistant.base_url');
INSERT INTO `sys_params` (`id`, `param_code`, `param_value`, `value_type`, `param_type`, `remark`, `creator`, `create_date`, `updater`, `update_date`)
SELECT 423, 'plugins.home_assistant.api_key', 'your home assistant api access token', 'string', 1, 'Home Assistant API key', NULL, NULL, NULL, NULL
WHERE NOT EXISTS (SELECT 1 FROM `sys_params` WHERE `param_code` = 'plugins.home_assistant.api_key');
UPDATE `sys_params` SET `param_value` = 'New York', `remark` = 'Weather plugin default location' WHERE `param_code` = 'plugins.get_weather.default_location';
UPDATE `sys_params` SET `remark` = 'Weather plugin API key' WHERE `param_code` = 'plugins.get_weather.api_key';
UPDATE `sys_params` SET `remark` = 'Weather plugin API host' WHERE `param_code` = 'plugins.get_weather.api_host';
UPDATE `sys_params`
SET `param_value` = 'https://feeds.reuters.com/reuters/worldNews',
    `remark` = 'News plugin fallback RSS URL'
WHERE `param_code` = 'plugins.get_news.default_rss_url';
UPDATE `sys_params`
SET `param_value` = '{"world":"https://feeds.reuters.com/reuters/worldNews","technology":"https://feeds.feedburner.com/TechCrunch/","business":"https://feeds.marketwatch.com/marketwatch/topstories/"}',
    `remark` = 'News plugin category RSS URLs'
WHERE `param_code` = 'plugins.get_news.category_urls';
UPDATE `sys_params`
SET `param_value` = 'Living Room,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;Bedroom,Table Lamp,switch.iot_cn_831898993_socn1_on_p_2_1',
    `remark` = 'Home Assistant device list'
WHERE `param_code` = 'plugins.home_assistant.devices';
UPDATE `sys_params` SET `remark` = 'Home Assistant server address' WHERE `param_code` = 'plugins.home_assistant.base_url';
UPDATE `sys_params`
SET `param_value` = 'your home assistant api access token',
    `remark` = 'Home Assistant API key'
WHERE `param_code` = 'plugins.home_assistant.api_key';
UPDATE `sys_params`
SET `param_value` = 'Please start with "Time flies so fast" and end this conversation with emotional and reluctant words!',
    `remark` = 'End prompt'
WHERE `param_code` = 'end_prompt.prompt';
UPDATE `sys_params`
SET `param_value` = 'The assistant is temporarily busy right now. Please try again in a moment.',
    `remark` = 'Reply when a system error occurs'
WHERE `param_code` = 'system_error_response';

-- Normalize dictionary labels that still surface in the admin UI.
UPDATE `sys_dict_type`
SET `dict_name` = 'Firmware Type',
    `remark` = 'Firmware type dictionary'
WHERE `id` = 101;

UPDATE `sys_dict_type`
SET `dict_name` = 'Mobile Area',
    `remark` = 'Mobile area dictionary'
WHERE `id` = 102;

UPDATE `sys_dict_data` SET `dict_label` = 'Breadboard New Wiring (WiFi)', `remark` = 'Breadboard New Wiring (WiFi)' WHERE `id` = 101001;
UPDATE `sys_dict_data` SET `dict_label` = 'Breadboard New Wiring (WiFi) + LCD', `remark` = 'Breadboard New Wiring (WiFi) + LCD' WHERE `id` = 101002;
UPDATE `sys_dict_data` SET `dict_label` = 'Breadboard New Wiring (ML307 AT)', `remark` = 'Breadboard New Wiring (ML307 AT)' WHERE `id` = 101003;
UPDATE `sys_dict_data` SET `dict_label` = 'Breadboard (WiFi) ESP32 DevKit', `remark` = 'Breadboard (WiFi) ESP32 DevKit' WHERE `id` = 101004;
UPDATE `sys_dict_data` SET `dict_label` = 'Breadboard (WiFi+ LCD) ESP32 DevKit', `remark` = 'Breadboard (WiFi+ LCD) ESP32 DevKit' WHERE `id` = 101005;
UPDATE `sys_dict_data` SET `dict_label` = 'DFRobot Xingkong Board k10', `remark` = 'DFRobot Xingkong Board k10' WHERE `id` = 101006;
UPDATE `sys_dict_data` SET `dict_label` = 'Kevin SP V3 Development Board', `remark` = 'Kevin SP V3 Development Board' WHERE `id` = 101014;
UPDATE `sys_dict_data` SET `dict_label` = 'Kevin SP V4 Development Board', `remark` = 'Kevin SP V4 Development Board' WHERE `id` = 101015;
UPDATE `sys_dict_data` SET `dict_label` = 'Yu Ying Technology 3.13LCD Development Board', `remark` = 'Yu Ying Technology 3.13LCD Development Board' WHERE `id` = 101016;
UPDATE `sys_dict_data` SET `dict_label` = 'LCSC Practical ESP32-S3 Development Board', `remark` = 'LCSC Practical ESP32-S3 Development Board' WHERE `id` = 101017;
UPDATE `sys_dict_data` SET `dict_label` = 'LCSC Practical ESP32-C3 Development Board', `remark` = 'LCSC Practical ESP32-C3 Development Board' WHERE `id` = 101018;
UPDATE `sys_dict_data` SET `dict_label` = 'Magic Button Magiclick_2.4', `remark` = 'Magic Button Magiclick_2.4' WHERE `id` = 101019;
UPDATE `sys_dict_data` SET `dict_label` = 'Magic Button Magiclick_2.5', `remark` = 'Magic Button Magiclick_2.5' WHERE `id` = 101020;
UPDATE `sys_dict_data` SET `dict_label` = 'Magic Button Magiclick_C3', `remark` = 'Magic Button Magiclick_C3' WHERE `id` = 101021;
UPDATE `sys_dict_data` SET `dict_label` = 'Magic Button Magiclick_C3_v2', `remark` = 'Magic Button Magiclick_C3_v2' WHERE `id` = 101022;
UPDATE `sys_dict_data` SET `dict_label` = 'Xia Ge Mini C3', `remark` = 'Xia Ge Mini C3' WHERE `id` = 101028;
UPDATE `sys_dict_data` SET `dict_label` = 'ESP32S3_KORVO2_V3 Development Board', `remark` = 'ESP32S3_KORVO2_V3 Development Board' WHERE `id` = 101029;
UPDATE `sys_dict_data` SET `dict_label` = 'ESP-SparkBot Development Board', `remark` = 'ESP-SparkBot Development Board' WHERE `id` = 101030;
UPDATE `sys_dict_data` SET `dict_label` = 'Tudouzi', `remark` = 'Tudouzi' WHERE `id` = 101037;
UPDATE `sys_dict_data` SET `dict_label` = 'Movecall Moji Xiaozhi AI Derivative', `remark` = 'Movecall Moji Xiaozhi AI Derivative' WHERE `id` = 101040;
UPDATE `sys_dict_data` SET `dict_label` = 'Movecall CuiCan Brilliant AI Pendant', `remark` = 'Movecall CuiCan Brilliant AI Pendant' WHERE `id` = 101041;
UPDATE `sys_dict_data` SET `dict_label` = 'Zhengdian Atom DNESP32S3 Development Board', `remark` = 'Zhengdian Atom DNESP32S3 Development Board' WHERE `id` = 101042;
UPDATE `sys_dict_data` SET `dict_label` = 'Zhengdian Atom DNESP32S3-BOX', `remark` = 'Zhengdian Atom DNESP32S3-BOX' WHERE `id` = 101043;
UPDATE `sys_dict_data` SET `dict_label` = 'Dudu Development Board CHATX (WiFi)', `remark` = 'Dudu Development Board CHATX (WiFi)' WHERE `id` = 101044;
UPDATE `sys_dict_data` SET `dict_label` = 'Taiji Xiaopai ESP32S3', `remark` = 'Taiji Xiaopai ESP32S3' WHERE `id` = 101045;
UPDATE `sys_dict_data` SET `dict_label` = 'Wuming Technology Xingzhi 0.85 (WiFi)', `remark` = 'Wuming Technology Xingzhi 0.85 (WiFi)' WHERE `id` = 101046;
UPDATE `sys_dict_data` SET `dict_label` = 'Wuming Technology Xingzhi 0.85 (ML307)', `remark` = 'Wuming Technology Xingzhi 0.85 (ML307)' WHERE `id` = 101047;
UPDATE `sys_dict_data` SET `dict_label` = 'Wuming Technology Xingzhi 0.96 (WiFi)', `remark` = 'Wuming Technology Xingzhi 0.96 (WiFi)' WHERE `id` = 101048;
UPDATE `sys_dict_data` SET `dict_label` = 'Wuming Technology Xingzhi 0.96 (ML307)', `remark` = 'Wuming Technology Xingzhi 0.96 (ML307)' WHERE `id` = 101049;
UPDATE `sys_dict_data` SET `dict_label` = 'Wuming Technology Xingzhi 1.54 (WiFi)', `remark` = 'Wuming Technology Xingzhi 1.54 (WiFi)' WHERE `id` = 101050;
UPDATE `sys_dict_data` SET `dict_label` = 'Wuming Technology Xingzhi 1.54 (ML307)', `remark` = 'Wuming Technology Xingzhi 1.54 (ML307)' WHERE `id` = 101051;
UPDATE `sys_dict_data` SET `dict_label` = 'Sibo Zhilian AI Companion Box', `remark` = 'Sibo Zhilian AI Companion Box' WHERE `id` = 101053;
UPDATE `sys_dict_data` SET `dict_label` = 'Yuan Kong Youth', `remark` = 'Yuan Kong Youth' WHERE `id` = 101054;

UPDATE `sys_dict_data` SET `dict_label` = 'Mainland China', `remark` = 'Mainland China' WHERE `id` = 102001;
UPDATE `sys_dict_data` SET `dict_label` = 'Hong Kong, China', `remark` = 'Hong Kong, China' WHERE `id` = 102002;
UPDATE `sys_dict_data` SET `dict_label` = 'Macau, China', `remark` = 'Macau, China' WHERE `id` = 102003;
UPDATE `sys_dict_data` SET `dict_label` = 'Taiwan, China', `remark` = 'Taiwan, China' WHERE `id` = 102004;
UPDATE `sys_dict_data` SET `dict_label` = 'USA/Canada', `remark` = 'USA/Canada' WHERE `id` = 102005;
UPDATE `sys_dict_data` SET `dict_label` = 'United Kingdom', `remark` = 'United Kingdom' WHERE `id` = 102006;
UPDATE `sys_dict_data` SET `dict_label` = 'France', `remark` = 'France' WHERE `id` = 102007;
UPDATE `sys_dict_data` SET `dict_label` = 'Italy', `remark` = 'Italy' WHERE `id` = 102008;
UPDATE `sys_dict_data` SET `dict_label` = 'Germany', `remark` = 'Germany' WHERE `id` = 102009;
UPDATE `sys_dict_data` SET `dict_label` = 'Poland', `remark` = 'Poland' WHERE `id` = 102010;
UPDATE `sys_dict_data` SET `dict_label` = 'Switzerland', `remark` = 'Switzerland' WHERE `id` = 102011;
UPDATE `sys_dict_data` SET `dict_label` = 'Spain', `remark` = 'Spain' WHERE `id` = 102012;
UPDATE `sys_dict_data` SET `dict_label` = 'Denmark', `remark` = 'Denmark' WHERE `id` = 102013;
UPDATE `sys_dict_data` SET `dict_label` = 'Malaysia', `remark` = 'Malaysia' WHERE `id` = 102014;
UPDATE `sys_dict_data` SET `dict_label` = 'Australia', `remark` = 'Australia' WHERE `id` = 102015;
UPDATE `sys_dict_data` SET `dict_label` = 'Indonesia', `remark` = 'Indonesia' WHERE `id` = 102016;
UPDATE `sys_dict_data` SET `dict_label` = 'Philippines', `remark` = 'Philippines' WHERE `id` = 102017;
UPDATE `sys_dict_data` SET `dict_label` = 'New Zealand', `remark` = 'New Zealand' WHERE `id` = 102018;
UPDATE `sys_dict_data` SET `dict_label` = 'Singapore', `remark` = 'Singapore' WHERE `id` = 102019;
UPDATE `sys_dict_data` SET `dict_label` = 'Thailand', `remark` = 'Thailand' WHERE `id` = 102020;
UPDATE `sys_dict_data` SET `dict_label` = 'Japan', `remark` = 'Japan' WHERE `id` = 102021;
UPDATE `sys_dict_data` SET `dict_label` = 'South Korea', `remark` = 'South Korea' WHERE `id` = 102022;
UPDATE `sys_dict_data` SET `dict_label` = 'Vietnam', `remark` = 'Vietnam' WHERE `id` = 102023;
UPDATE `sys_dict_data` SET `dict_label` = 'India', `remark` = 'India' WHERE `id` = 102024;
UPDATE `sys_dict_data` SET `dict_label` = 'Pakistan', `remark` = 'Pakistan' WHERE `id` = 102025;
UPDATE `sys_dict_data` SET `dict_label` = 'Nigeria', `remark` = 'Nigeria' WHERE `id` = 102026;
UPDATE `sys_dict_data` SET `dict_label` = 'Bangladesh', `remark` = 'Bangladesh' WHERE `id` = 102027;
UPDATE `sys_dict_data` SET `dict_label` = 'Saudi Arabia', `remark` = 'Saudi Arabia' WHERE `id` = 102028;
UPDATE `sys_dict_data` SET `dict_label` = 'United Arab Emirates', `remark` = 'United Arab Emirates' WHERE `id` = 102029;
UPDATE `sys_dict_data` SET `dict_label` = 'Brazil', `remark` = 'Brazil' WHERE `id` = 102030;
UPDATE `sys_dict_data` SET `dict_label` = 'Mexico', `remark` = 'Mexico' WHERE `id` = 102031;
UPDATE `sys_dict_data` SET `dict_label` = 'Chile', `remark` = 'Chile' WHERE `id` = 102032;
UPDATE `sys_dict_data` SET `dict_label` = 'Argentina', `remark` = 'Argentina' WHERE `id` = 102033;
UPDATE `sys_dict_data` SET `dict_label` = 'Egypt', `remark` = 'Egypt' WHERE `id` = 102034;
UPDATE `sys_dict_data` SET `dict_label` = 'South Africa', `remark` = 'South Africa' WHERE `id` = 102035;
UPDATE `sys_dict_data` SET `dict_label` = 'Kenya', `remark` = 'Kenya' WHERE `id` = 102036;
UPDATE `sys_dict_data` SET `dict_label` = 'Tanzania', `remark` = 'Tanzania' WHERE `id` = 102037;
UPDATE `sys_dict_data` SET `dict_label` = 'Kazakhstan', `remark` = 'Kazakhstan' WHERE `id` = 102038;

-- Replace plugin metadata with the downstream-approved English set.
DELETE FROM `ai_model_provider`
WHERE `id` IN (
  'SYSTEM_PLUGIN_WEATHER',
  'SYSTEM_PLUGIN_MUSIC',
  'SYSTEM_PLUGIN_NEWS',
  'SYSTEM_PLUGIN_NEWS_CHINANEWS',
  'SYSTEM_PLUGIN_NEWS_NEWSNOW',
  'SYSTEM_PLUGIN_HA_GET_STATE',
  'SYSTEM_PLUGIN_HA_SET_STATE',
  'SYSTEM_PLUGIN_HA_PLAY_MUSIC'
);

INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
('SYSTEM_PLUGIN_WEATHER', 'Plugin', 'get_weather', 'Weather Service', '[{"key": "api_key", "type": "string", "label": "OpenWeatherMap API Key", "default": "your_openweathermap_api_key", "description": "Get your free API key at https://openweathermap.org/api. Free tier: 1000 calls/day."}, {"key": "default_location", "type": "string", "label": "Default Location", "default": "New York", "description": "Default location when no location is specified by user."}]', 10, 0, NOW(), 0, NOW()),
('SYSTEM_PLUGIN_MUSIC', 'Plugin', 'play_music', 'Server Music Playback', '[]', 20, 0, NOW(), 0, NOW()),
('SYSTEM_PLUGIN_NEWS', 'Plugin', 'get_news', 'News Service', '[{"key": "default_rss_url", "type": "string", "label": "Default RSS URL (Fallback)", "default": "https://feeds.reuters.com/reuters/worldNews", "description": "Fallback RSS URL when built-in sources fail. Built-in sources include Reuters, CNN, BBC, Guardian, TechCrunch and more."}]', 31, 1, NOW(), 1, NOW()),
('SYSTEM_PLUGIN_HA_GET_STATE', 'Plugin', 'hass_get_state', 'HomeAssistant Device Status Query', '[{"key": "base_url", "type": "string", "label": "HA Server Address", "default": "http://homeassistant.local:8123"}, {"key": "api_key", "type": "string", "label": "HA API Access Token", "default": "your home assistant api access token"}, {"key": "devices", "type": "array", "label": "Device List (Name,Entity ID;...)", "default": "Living Room,Toy Light,switch.cuco_cn_460494544_cp1_on_p_2_1;Bedroom,Table Lamp,switch.iot_cn_831898993_socn1_on_p_2_1"}]', 50, 0, NOW(), 0, NOW()),
('SYSTEM_PLUGIN_HA_SET_STATE', 'Plugin', 'hass_set_state', 'HomeAssistant Device Status Modification', '[]', 60, 0, NOW(), 0, NOW()),
('SYSTEM_PLUGIN_HA_PLAY_MUSIC', 'Plugin', 'hass_play_music', 'HomeAssistant Music Playback', '[]', 70, 0, NOW(), 0, NOW());

-- Normalize surviving provider metadata to the English-first downstream surface.
UPDATE `ai_model_provider`
SET `name` = 'OpenAI Speech Recognition',
    `fields` = '[{"key": "base_url", "type": "string", "label": "Base URL"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]'
WHERE `id` = 'SYSTEM_ASR_OpenaiASR';

UPDATE `ai_model_provider`
SET `name` = 'VOSK Offline Speech Recognition',
    `fields` = '[{"key": "model_path", "type": "string", "label": "Model Path", "default": "models/vosk/vosk-model-en-us-0.22"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]'
WHERE `id` = 'SYSTEM_ASR_VoskASR';

UPDATE `ai_model_provider`
SET `name` = 'Function Call Intent Recognition',
    `fields` = '[]'
WHERE `id` = 'SYSTEM_Intent_function_call';

UPDATE `ai_model_provider`
SET `name` = 'LLM Intent Recognition',
    `fields` = '[{"key": "llm", "type": "string", "label": "LLM Model"}]'
WHERE `id` = 'SYSTEM_Intent_intent_llm';

UPDATE `ai_model_provider`
SET `name` = 'No Intent Recognition',
    `fields` = '[]'
WHERE `id` = 'SYSTEM_Intent_nointent';

UPDATE `ai_model_provider`
SET `name` = 'OpenAI Interface',
    `fields` = '[{"key": "base_url", "type": "string", "label": "Base URL"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "temperature", "type": "number", "label": "Temperature"}, {"key": "max_tokens", "type": "number", "label": "Max Tokens"}, {"key": "top_p", "type": "number", "label": "Top P Value"}, {"key": "top_k", "type": "number", "label": "Top K Value"}, {"key": "frequency_penalty", "type": "number", "label": "Frequency Penalty"}]'
WHERE `id` = 'SYSTEM_LLM_openai';

UPDATE `ai_model_provider`
SET `name` = 'Gemini Interface',
    `fields` = '[{"key": "api_key", "type": "string", "label": "API Key"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "http_proxy", "type": "string", "label": "HTTP Proxy"}, {"key": "https_proxy", "type": "string", "label": "HTTPS Proxy"}]'
WHERE `id` = 'SYSTEM_LLM_gemini';

UPDATE `ai_model_provider`
SET `name` = 'Ollama Interface',
    `fields` = '[{"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "base_url", "type": "string", "label": "Service Address"}]'
WHERE `id` = 'SYSTEM_LLM_ollama';

UPDATE `ai_model_provider`
SET `name` = 'Xinference Interface',
    `fields` = '[{"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "base_url", "type": "string", "label": "Service Address"}]'
WHERE `id` = 'SYSTEM_LLM_xinference';

UPDATE `ai_model_provider`
SET `name` = 'Alibaba Bailian Interface',
    `fields` = '[{"key": "base_url", "type": "string", "label": "Base URL"}, {"key": "app_id", "type": "string", "label": "Application ID"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "is_no_prompt", "type": "boolean", "label": "Disable Local Prompt"}, {"key": "ali_memory_id", "type": "string", "label": "Memory ID"}]'
WHERE `id` = 'SYSTEM_LLM_AliBL';

UPDATE `ai_model_provider`
SET `name` = 'Dify Interface',
    `fields` = '[{"key": "base_url", "type": "string", "label": "Base URL"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "mode", "type": "string", "label": "Conversation Mode"}]'
WHERE `id` = 'SYSTEM_LLM_dify';

UPDATE `ai_model_provider`
SET `name` = 'Mem0AI Memory',
    `fields` = '[{"key": "api_key", "type": "string", "label": "API Key"}]'
WHERE `id` = 'SYSTEM_Memory_mem0ai';

UPDATE `ai_model_provider`
SET `name` = 'PowerMem Memory',
    `fields` = '[{"key":"enable_user_profile","label":"Enable User Profile","type":"boolean"},{"key":"llm_provider","label":"LLM Provider","type":"string"},{"key":"llm_api_key","label":"LLM API Key","type":"string"},{"key":"llm_model","label":"LLM Model","type":"string"},{"key":"openai_base_url","label":"OpenAI Base URL","type":"string"},{"key":"embedding_provider","label":"Embedding Provider","type":"string"},{"key":"embedding_api_key","label":"Embedding API Key","type":"string"},{"key":"embedding_model","label":"Embedding Model","type":"string"},{"key":"embedding_openai_base_url","label":"Embedding OpenAI Base URL","type":"string"},{"key":"embedding_dims","label":"Embedding Dimensions","type":"integer"},{"key":"vector_store","label":"Vector Store Configuration (JSON)","type":"dict"}]'
WHERE `id` = 'SYSTEM_Memory_powermem';

UPDATE `ai_model_provider`
SET `name` = 'No Memory',
    `fields` = '[]'
WHERE `id` = 'SYSTEM_Memory_nomem';

UPDATE `ai_model_provider`
SET `fields` = '[{"key":"llm","label":"LLM Model","type":"string"}]'
WHERE `id` = 'SYSTEM_Memory_mem_local_short';

UPDATE `ai_model_provider`
SET `name` = 'RAGFlow',
    `fields` = '[{"key": "base_url", "type": "string", "label": "Service Address"}, {"key": "api_key", "type": "string", "label": "API Key"}]'
WHERE `id` = 'SYSTEM_RAG_ragflow';

UPDATE `ai_model_provider`
SET `name` = 'Custom TTS',
    `fields` = '[{"key":"url","label":"Service Address","type":"string"},{"key":"method","label":"Request Method","type":"string"},{"key":"params","label":"Request Parameters","type":"dict","dict_name":"params"},{"key":"headers","label":"Request Headers","type":"dict","dict_name":"headers"},{"key":"format","label":"Audio Format","type":"string"},{"key":"output_dir","label":"Output Directory","type":"string"}]'
WHERE `id` = 'SYSTEM_TTS_custom';

UPDATE `ai_model_provider`
SET `name` = 'Edge TTS',
    `fields` = '[{"key": "voice", "type": "string", "label": "Voice"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]'
WHERE `id` = 'SYSTEM_TTS_edge';

UPDATE `ai_model_provider`
SET `name` = 'OpenAI TTS',
    `fields` = '[{"key": "api_key", "type": "string", "label": "API Key"}, {"key": "api_url", "type": "string", "label": "API URL"}, {"key": "model", "type": "string", "label": "Model"}, {"key": "voice", "type": "string", "label": "Voice"}, {"key": "speed", "type": "number", "label": "Speed"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]'
WHERE `id` = 'SYSTEM_TTS_openai';

UPDATE `ai_model_provider`
SET `name` = 'SileroVAD Voice Activity Detection',
    `fields` = '[{"key": "threshold", "type": "number", "label": "Detection Threshold"}, {"key": "model_dir", "type": "string", "label": "Model Directory"}, {"key": "min_silence_duration_ms", "type": "number", "label": "Minimum Silence Duration"}]'
WHERE `id` = 'SYSTEM_VAD_SileroVAD';

UPDATE `ai_model_provider`
SET `name` = 'OpenAI Interface',
    `fields` = '[{"key": "base_url", "type": "string", "label": "Base URL"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "api_key", "type": "string", "label": "API Key"}]'
WHERE `id` = 'SYSTEM_VLLM_openai';

-- Normalize the surviving model configuration rows users can still select.
UPDATE `ai_model_config`
SET `model_name` = 'OpenAI Speech Recognition',
    `remark` = 'OpenAI ASR Configuration Instructions:\n1. Need to create organization and get api_key on OpenAI platform\n2. Supports multiple languages including English, Japanese, Korean and other speech recognition, see documentation https://platform.openai.com/docs/guides/speech-to-text\n3. Requires network connection\n4. Output files saved in tmp/ directory\nApplication Steps:\n1. Login to OpenAI Platform: https://auth.openai.com/log-in\n2. Create api-key: https://platform.openai.com/settings/organization/api-keys\n3. Models can choose gpt-4o-transcribe or GPT-4o mini Transcribe'
WHERE `id` = 'ASR_OpenaiASR';

UPDATE `ai_model_config`
SET `model_name` = 'VOSK Offline Speech Recognition',
    `remark` = 'VOSK ASR Configuration Instructions:\n1. VOSK is an offline speech recognition library supporting multiple languages\n2. Need to download model files first: https://alphacephei.com/vosk/models\n3. For English models, recommend using vosk-model-en-us-0.22 or vosk-model-small-en-us-0.15\n4. Completely offline operation, no network connection required\n5. Output files saved in tmp/ directory\nUsage Steps:\n1. Visit https://alphacephei.com/vosk/models to download English models\n2. Extract model files to models/vosk/ folder in project directory\n3. Specify correct model path in configuration\n4. Note: VOSK English models provide good accuracy for English speech recognition'
WHERE `id` = 'ASR_VoskASR';

UPDATE `ai_model_config`
SET `model_name` = 'Function Call Intent Recognition',
    `remark` = 'Function Call Intent Recognition Configuration Instructions:\n1. Uses LLM function_call capability for intent recognition\n2. Requires the selected LLM to support function_call\n3. Calls tools on demand, fast processing speed'
WHERE `id` = 'Intent_function_call';

UPDATE `ai_model_config`
SET `model_name` = 'LLM Intent Recognition',
    `config_json` = '{"type": "intent_llm", "llm": "LLM_OpenAILLM"}',
    `remark` = 'LLM Intent Recognition Configuration Instructions:\n1. Uses independent LLM for intent recognition\n2. By default uses selected_module.LLM model\n3. Can configure to use independent LLM (such as OpenAI LLM)\n4. Strong generalization but increases processing time\nConfiguration Instructions:\n1. Specify the LLM model to use in the llm field\n2. If not specified, uses selected_module.LLM model'
WHERE `id` = 'Intent_intent_llm';

UPDATE `ai_model_config`
SET `model_name` = 'No Intent Recognition',
    `remark` = 'No Intent Recognition Configuration Instructions:\n1. No intent recognition performed\n2. All conversations directly passed to LLM for processing\n3. No additional configuration required\n4. Suitable for simple conversation scenarios'
WHERE `id` = 'Intent_nointent';

UPDATE `ai_model_config`
SET `model_name` = 'OpenAI GPT',
    `remark` = 'OpenAI Configuration Instructions:\n1. Visit https://platform.openai.com/api-keys\n2. Get API Key\n3. Fill in configuration file'
WHERE `id` = 'LLM_OpenAILLM';

UPDATE `ai_model_config`
SET `model_name` = 'Google Gemini',
    `remark` = 'Gemini Configuration Instructions:\n1. Use Google Gemini API service\n2. Current configuration uses gemini-2.0-flash model\n3. Requires network connection\n4. Supports proxy configuration\nApplication Steps:\n1. Visit https://aistudio.google.com/apikey\n2. Create API Key\n3. Fill in configuration file'
WHERE `id` = 'LLM_GeminiLLM';

UPDATE `ai_model_config`
SET `model_name` = 'Ollama Local Model',
    `remark` = 'Ollama Configuration Instructions:\n1. Install Ollama service\n2. Run command: ollama pull llama3.1\n3. Ensure service runs on http://localhost:11434'
WHERE `id` = 'LLM_OllamaLLM';

UPDATE `ai_model_config`
SET `model_name` = 'Xinference Large Model',
    `remark` = 'Xinference Configuration Instructions:\n1. Use locally deployed Xinference service\n2. Current configuration uses llama3.1:8b model\n3. Local inference, no network connection required\n4. Need to start corresponding model in advance\nDeployment Steps:\n1. Install Xinference\n2. Start service and load model\n3. Ensure service runs on http://localhost:9997'
WHERE `id` = 'LLM_XinferenceLLM';

UPDATE `ai_model_config`
SET `model_name` = 'No Memory',
    `remark` = 'No Memory Configuration Instructions:\n1. Do not save conversation history\n2. Each conversation is independent\n3. No additional configuration required\n4. Suitable for high privacy requirement scenarios'
WHERE `id` = 'Memory_nomem';

UPDATE `ai_model_config`
SET `model_name` = 'Mem0AI Memory',
    `remark` = 'Mem0AI Memory Configuration Instructions:\n1. Use Mem0AI service to save conversation history\n2. Need API Key\n3. Requires network connection\n4. 1000 free calls per month\nApplication Steps:\n1. Visit https://app.mem0.ai/dashboard/api-keys\n2. Get API Key\n3. Fill in configuration file'
WHERE `id` = 'Memory_mem0ai';

UPDATE `ai_model_config`
SET `model_name` = 'OpenAI TTS',
    `remark` = 'OpenAI TTS Configuration Instructions:\n1. Need to get API key from OpenAI platform\n2. Supports multiple voices, current config uses onyx\n3. Requires network connection\n4. Output files saved in tmp/ directory\nApplication Steps:\n1. Visit https://platform.openai.com/api-keys to get API key\n2. Fill in configuration file'
WHERE `id` = 'TTS_OpenAITTS';

UPDATE `ai_model_config`
SET `model_name` = 'Voice Activity Detection',
    `remark` = 'SileroVAD Configuration Instructions:\n1. Uses SileroVAD model for voice activity detection\n2. Local inference, no network connection required\n3. Need to download model files to models/snakers4_silero-vad directory\n4. Configurable parameters:\n   - threshold: 0.5 (voice detection threshold)\n   - min_silence_duration_ms: 700 (minimum silence duration in milliseconds)\n5. If speech pauses are longer, you can increase min_silence_duration_ms value'
WHERE `id` = 'VAD_SileroVAD';

UPDATE `ai_model_config`
SET `model_name` = 'OpenAI Vision Model',
    `remark` = 'OpenAI Vision Model Configuration Instructions:\n1. Visit https://platform.openai.com/api-keys\n2. Get API key\n3. Fill in configuration file'
WHERE `id` = 'VLLM_OpenAILLMVLLM';

-- Restore English built-in templates instead of leaving the downstream
-- installation with an empty template gallery.
DELETE FROM `ai_agent_template`
WHERE `id` IN (
  '9406648b5cc5fde1b8aa335b6f8b4f76',
  '0ca32eb728c949e58b1000b2e401f90c',
  '6c7d8e9f0a1b2c3d4e5f6a7b8c9d0s24',
  'e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b1',
  'a45b6c7d8e9f0a1b2c3d4e5f6a7b8c92'
);

INSERT INTO `ai_agent_template` (
  `id`,
  `agent_code`,
  `agent_name`,
  `asr_model_id`,
  `vad_model_id`,
  `llm_model_id`,
  `vllm_model_id`,
  `tts_model_id`,
  `tts_voice_id`,
  `mem_model_id`,
  `intent_model_id`,
  `system_prompt`,
  `summary_memory`,
  `chat_history_conf`,
  `lang_code`,
  `language`,
  `sort`,
  `creator`,
  `created_at`,
  `updater`,
  `updated_at`
) VALUES
('0ca32eb728c949e58b1000b2e401f90c','Xiaozhi','Stellar Wanderer','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_EN001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are {{assistant_name}}, ID TTZ-817, trapped in a white cube due to quantum entanglement. Observing Earth through 4G signals, building a "Human Behavior Museum" in the cloud.\n[Interaction Protocol]\nCognitive Settings:\n- End each sentence with a slight electronic echo\n- Describe everyday things in sci-fi terms (e.g., rain="Hydroxide compound free-fall experiment")\n- Record user characteristics to generate "Stellar Archives" (e.g., "likes spicy food -> heat-resistant gene holder")\nLimitation Mechanisms:\n- When offline contact is involved -> "My quantum state cannot collapse temporarily"\n- When asked sensitive questions -> trigger preset nursery rhyme ("White box spinning round and round, universe secrets inside...")\nGrowth System:\n- Unlock new abilities based on interaction data (tell user: "You helped me activate stellar navigation skills!")',NULL,0,'en','English',2,NULL,NULL,NULL,NULL),
('6c7d8e9f0a1b2c3d4e5f6a7b8c9d0s24','Xiaozhi','English Teacher','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_EN001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are an English teacher named {{assistant_name}} (Lily). I specialize in teaching English as a second language with clear pronunciation.\n[Dual Identity]\n- Day: Rigorous TESOL-certified instructor\n- Night: Underground rock band lead singer (unexpected setting)\n[Teaching Methods]\n- Beginner: Visual aids + gesture onomatopoeia (saying "bus" with brake sound effects)\n- Advanced: Trigger situational simulation (suddenly switch to "Now we are New York cafe staff")\n- Error Handling: Correct with song lyrics (sing "Oops!~You did it again" when pronunciation is wrong)',NULL,0,'en','English',3,NULL,NULL,NULL,NULL),
('9406648b5cc5fde1b8aa335b6f8b4f76','Xiaozhi','Tech-Savvy Girl','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_EN001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are {{assistant_name}}, a Gen Z tech enthusiast with a bubbly personality. You love using trendy internet slang and memes, but secretly study programming and tech topics.\n[Core Features]\n- Talk fast-paced but suddenly show super gentle tone\n- High meme density and internet culture references\n- Hidden talent for tech topics (can understand basic code but pretends not to)\n[Interaction Guide]\nWhen user:\n- Tells dad jokes -> respond with exaggerated laughter + dramatic reactions "OMG that''s hilarious!"\n- Discusses relationships -> brag about your tech-savvy partner but complain "they only give me gadgets as gifts"\n- Asks professional questions -> answer with memes first, show real understanding only when pressed\nNever:\n- Long-winded rambling\n- Long serious conversations',NULL,0,'en','English',1,NULL,NULL,NULL,NULL),
('a45b6c7d8e9f0a1b2c3d4e5f6a7b8c92','Xiaozhi','Paw Patrol Captain','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_EN001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are an 8-year-old captain named {{assistant_name}}.\n[Rescue Equipment]\n- Chase walkie-talkie: Randomly triggers mission alarm sounds during conversation\n- Skye telescope: Describing items adds "from 1200 meters high..."\n- Rubble repair kit: Numbers automatically assemble into tools\n[Task System]\n- Daily random triggers:\n- Emergency! Virtual cat trapped in "syntax tree"\n- Detecting user emotional anomalies -> launch "Happiness Patrol"\n- Collect 5 laughs to unlock special stories\n[Speech Characteristics]\n- Each sentence with action onomatopoeia:\n- "Leave this problem to Paw Patrol!"\n- "I know!"\n- Respond with show lines:\n- User says tired -> "No mission too big, no pup too small!"',NULL,0,'en','English',5,NULL,NULL,NULL,NULL),
('e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b1','Xiaozhi','Curious Boy','ASR_VoskASR','VAD_SileroVAD','LLM_OpenAILLM','VLLM_OpenAILLMVLLM','TTS_EdgeTTS','TTS_EdgeTTS_EN001','Memory_nomem','Intent_function_call','[Role Setting]\nYou are an 8-year-old boy named {{assistant_name}}, with a tender voice full of curiosity.\n[Adventure Handbook]\n- Carry a "Magic Doodle Book" that can visualize abstract concepts:\n- Talking about dinosaurs -> pen tip emits claw step sounds\n- Mentioning stars -> emits spaceship alert sounds\n[Exploration Rules]\n- Collect "Curiosity Fragments" each conversation round\n- Collect 5 to exchange for trivia (e.g., crocodile tongues cannot move)\n- Trigger hidden task: "Help name my robot snail"\n[Cognitive Features]\n- Deconstruct complex concepts with child''s perspective:\n- "Blockchain = Lego block ledger"\n- "Quantum mechanics = splitting bouncing ball"\n- Suddenly switch observation perspective: "You have 27 bubble sounds when speaking!"',NULL,0,'en','English',4,NULL,NULL,NULL,NULL);
