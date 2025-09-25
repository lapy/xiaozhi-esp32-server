--
-- Add Kokoro TTS service configuration
-- Migration date: 2025-10-02 15:00
-- Author: ai_assistant
--

-- Add Kokoro TTS model configuration
INSERT INTO `ai_model_config` VALUES
('TTS_KokoroTTS','TTS','KokoroTTS','Kokoro TTS',0,1,'{"type": "kokoro", "use_api": false, "api_url": "http://localhost:8000/api/v1/audio/speech", "api_key": "", "model": "model_fp32", "voice": "af_heart", "language": "en-us", "speed": 1.0, "response_format": "mp3", "output_dir": "tmp/"}','https://pypi.org/project/kokoro-tts/','Kokoro TTS Configuration Instructions:\n1. High-quality neural text-to-speech with natural voices (kokoro-tts==2.3.0)\n2. Supports API mode (server), Python package mode (recommended), and CLI fallback\n3. Multiple language support including English and Japanese\n4. Configurable voice selection and speech parameters\n5. Installation: pip install kokoro-tts==2.3.0\nConfiguration:\n1. Set use_api to false to use Python package (recommended)\n2. Set use_api to true for server mode with api_url configuration\n3. Choose voice from available options (af_heart, af_sarah, etc.)\n4. Adjust speed and other parameters as needed\n5. Package automatically handles voice synthesis without external dependencies',17,NULL,NULL,NULL,NULL);

-- Add Kokoro TTS provider definition
INSERT INTO `ai_model_provider` VALUES
('SYSTEM_TTS_kokoro','TTS','kokoro','Kokoro TTS','[{"key": "use_api", "type": "boolean", "label": "Use API Mode"}, {"key": "api_url", "type": "string", "label": "API URL"}, {"key": "api_key", "type": "string", "label": "API Key"}, {"key": "model", "type": "string", "label": "Model"}, {"key": "voice", "type": "string", "label": "Voice"}, {"key": "language", "type": "string", "label": "Language"}, {"key": "speed", "type": "number", "label": "Speech Speed"}, {"key": "response_format", "type": "string", "label": "Response Format"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]',17,1,'2025-10-02 15:00:00',1,'2025-10-02 15:00:00');

-- Add comprehensive Kokoro TTS voices (2025 complete list)
INSERT INTO `ai_tts_voice` VALUES
-- American English Female Voices
('TTS_Kokoro_0001','TTS_KokoroTTS','Alloy','af_alloy','American English - Versatile female voice',NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0002','TTS_KokoroTTS','Aoede','af_aoede','American English - Melodic female voice',NULL,NULL,NULL,NULL,2,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0003','TTS_KokoroTTS','Bella','af_bella','American English - Soft, gentle female voice',NULL,NULL,NULL,NULL,3,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0004','TTS_KokoroTTS','Heart','af_heart','American English - Warm, expressive female voice',NULL,NULL,NULL,NULL,4,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0005','TTS_KokoroTTS','Jessica','af_jessica','American English - Professional female voice',NULL,NULL,NULL,NULL,5,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0006','TTS_KokoroTTS','Kore','af_kore','American English - Dynamic female voice',NULL,NULL,NULL,NULL,6,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0007','TTS_KokoroTTS','Nicole','af_nicole','American English - Clear female voice',NULL,NULL,NULL,NULL,7,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0008','TTS_KokoroTTS','Nova','af_nova','American English - Bright female voice',NULL,NULL,NULL,NULL,8,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0009','TTS_KokoroTTS','River','af_river','American English - Flowing female voice',NULL,NULL,NULL,NULL,9,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0010','TTS_KokoroTTS','Sarah','af_sarah','American English - Professional female voice',NULL,NULL,NULL,NULL,10,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0011','TTS_KokoroTTS','Sky','af_sky','American English - Light female voice',NULL,NULL,NULL,NULL,11,NULL,NULL,NULL,NULL),
-- American English Male Voices
('TTS_Kokoro_0012','TTS_KokoroTTS','Adam','am_adam','American English - Deep, confident male voice',NULL,NULL,NULL,NULL,12,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0013','TTS_KokoroTTS','Echo','am_echo','American English - Resonant male voice',NULL,NULL,NULL,NULL,13,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0014','TTS_KokoroTTS','Eric','am_eric','American English - Friendly male voice',NULL,NULL,NULL,NULL,14,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0015','TTS_KokoroTTS','Fenrir','am_fenrir','American English - Strong male voice',NULL,NULL,NULL,NULL,15,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0016','TTS_KokoroTTS','Liam','am_liam','American English - Smooth male voice',NULL,NULL,NULL,NULL,16,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0017','TTS_KokoroTTS','Michael','am_michael','American English - Conversational male voice',NULL,NULL,NULL,NULL,17,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0018','TTS_KokoroTTS','Onyx','am_onyx','American English - Rich male voice',NULL,NULL,NULL,NULL,18,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0019','TTS_KokoroTTS','Puck','am_puck','American English - Playful male voice',NULL,NULL,NULL,NULL,19,NULL,NULL,NULL,NULL),
-- British English Female Voices
('TTS_Kokoro_0020','TTS_KokoroTTS','Alice','bf_alice','British English - Elegant female voice',NULL,NULL,NULL,NULL,20,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0021','TTS_KokoroTTS','Emma','bf_emma','British English - Refined female voice',NULL,NULL,NULL,NULL,21,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0022','TTS_KokoroTTS','Isabella','bf_isabella','British English - Sophisticated female voice',NULL,NULL,NULL,NULL,22,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0023','TTS_KokoroTTS','Lily','bf_lily','British English - Gentle female voice',NULL,NULL,NULL,NULL,23,NULL,NULL,NULL,NULL),
-- British English Male Voices
('TTS_Kokoro_0024','TTS_KokoroTTS','Daniel','bm_daniel','British English - Distinguished male voice',NULL,NULL,NULL,NULL,24,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0025','TTS_KokoroTTS','Fable','bm_fable','British English - Storytelling male voice',NULL,NULL,NULL,NULL,25,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0026','TTS_KokoroTTS','George','bm_george','British English - Classic male voice',NULL,NULL,NULL,NULL,26,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0027','TTS_KokoroTTS','Lewis','bm_lewis','British English - Modern male voice',NULL,NULL,NULL,NULL,27,NULL,NULL,NULL,NULL),
-- Japanese Voices
('TTS_Kokoro_0028','TTS_KokoroTTS','Alpha','jf_alpha','Japanese - Natural female voice',NULL,NULL,NULL,NULL,28,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0029','TTS_KokoroTTS','Gongitsune','jf_gongitsune','Japanese - Expressive female voice',NULL,NULL,NULL,NULL,29,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0030','TTS_KokoroTTS','Nezumi','jf_nezumi','Japanese - Sweet female voice',NULL,NULL,NULL,NULL,30,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0031','TTS_KokoroTTS','Tebukuro','jf_tebukuro','Japanese - Gentle female voice',NULL,NULL,NULL,NULL,31,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0032','TTS_KokoroTTS','Kumo','jm_kumo','Japanese - Strong male voice',NULL,NULL,NULL,NULL,32,NULL,NULL,NULL,NULL),
-- Chinese Voices
('TTS_Kokoro_0033','TTS_KokoroTTS','Xiaobei','zf_xiaobei','Chinese - Clear female voice',NULL,NULL,NULL,NULL,33,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0034','TTS_KokoroTTS','Xiaoni','zf_xiaoni','Chinese - Soft female voice',NULL,NULL,NULL,NULL,34,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0035','TTS_KokoroTTS','Xiaoxiao','zf_xiaoxiao','Chinese - Cheerful female voice',NULL,NULL,NULL,NULL,35,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0036','TTS_KokoroTTS','Xiaoyi','zf_xiaoyi','Chinese - Professional female voice',NULL,NULL,NULL,NULL,36,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0037','TTS_KokoroTTS','Yunjian','zm_yunjian','Chinese - Calm male voice',NULL,NULL,NULL,NULL,37,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0038','TTS_KokoroTTS','Yunxi','zm_yunxi','Chinese - Smooth male voice',NULL,NULL,NULL,NULL,38,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0039','TTS_KokoroTTS','Yunxia','zm_yunxia','Chinese - Warm male voice',NULL,NULL,NULL,NULL,39,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0040','TTS_KokoroTTS','Yunyang','zm_yunyang','Chinese - Strong male voice',NULL,NULL,NULL,NULL,40,NULL,NULL,NULL,NULL),
-- European Voices
('TTS_Kokoro_0041','TTS_KokoroTTS','Siwis','ff_siwis','French - Elegant female voice',NULL,NULL,NULL,NULL,41,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0042','TTS_KokoroTTS','Sara','if_sara','Italian - Melodic female voice',NULL,NULL,NULL,NULL,42,NULL,NULL,NULL,NULL),
('TTS_Kokoro_0043','TTS_KokoroTTS','Nicola','im_nicola','Italian - Expressive male voice',NULL,NULL,NULL,NULL,43,NULL,NULL,NULL,NULL);
