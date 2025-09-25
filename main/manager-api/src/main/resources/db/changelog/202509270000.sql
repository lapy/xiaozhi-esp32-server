--
-- Add ASR configurations (Gemini, Sherpa Sense Voice, Whisper)
-- Author: AI Assistant
-- Date: 2025-01-01
--

-- Add Gemini ASR to ai_model_config table
INSERT INTO `ai_model_config` VALUES (
'ASR_GeminiASR',
'ASR',
'GeminiASR',
'Gemini Speech Recognition',
0,
0,
'{"type": "gemini", "api_key": "", "model_name": "gemini-2.0-flash-exp", "output_dir": "tmp/", "http_proxy": "", "https_proxy": ""}',
'https://aistudio.google.com/apikey',
'Gemini ASR Configuration Instructions:
1. Gemini ASR uses Google''s Gemini API for speech-to-text conversion
2. Supports multiple languages and provides high accuracy
3. Requires network connection and API key
4. Uses Gemini''s multimodal models for audio processing
Usage Steps:
1. Visit https://aistudio.google.com/apikey to create API key
2. Set your API key in the configuration below
3. Choose appropriate Gemini model for ASR tasks
4. Note: Gemini ASR provides excellent accuracy for multilingual speech recognition
5. Optional: Configure proxy settings for restricted regions',
11,
NULL,
NULL,
NULL,
NULL
);

-- Add Sherpa Sense Voice ASR to ai_model_config table
INSERT INTO `ai_model_config` VALUES (
'ASR_SherpaSenseVoiceASR',
'ASR',
'SherpaSenseVoiceASR',
'Sherpa Sense Voice Speech Recognition',
0,
0,
'{"type": "sherpa_onnx_local", "model_dir": "models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17", "output_dir": "tmp/", "model_type": "sense_voice"}',
'https://github.com/k2-fsa/sherpa-onnx',
'Sherpa Sense Voice ASR Configuration Instructions:
1. Multilingual speech recognition model supporting Chinese, English, Japanese, Korean, Cantonese
2. Automatically downloads model files to models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17 directory at runtime
3. Local inference, no network connection required
4. Output files saved in tmp/ directory
5. Provides high accuracy for multilingual speech recognition',
2,
NULL,
NULL,
NULL,
NULL
);

-- Add Gemini ASR provider to ai_model_provider table
INSERT INTO `ai_model_provider` VALUES (
'SYSTEM_ASR_GeminiASR',
'ASR',
'gemini',
'Gemini Speech Recognition',
'[{"key": "api_key", "type": "string", "label": "API Key"}, {"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}, {"key": "http_proxy", "type": "string", "label": "HTTP Proxy"}, {"key": "https_proxy", "type": "string", "label": "HTTPS Proxy"}]',
11,
1,
'2025-01-01 00:00:00',
1,
'2025-01-01 00:00:00'
);

-- Add Sherpa Sense Voice ASR provider to ai_model_provider table
INSERT INTO `ai_model_provider` VALUES (
'SYSTEM_ASR_SherpaSenseVoiceASR',
'ASR',
'sherpa_onnx_local',
'Sherpa Sense Voice Speech Recognition',
'[{"key": "model_dir", "type": "string", "label": "Model Directory"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}, {"key": "model_type", "type": "string", "label": "Model Type"}]',
2,
1,
'2025-01-01 00:00:00',
1,
'2025-01-01 00:00:00'
);

-- Add Whisper ASR to ai_model_config table
INSERT INTO `ai_model_config` VALUES (
'ASR_WhisperASR',
'ASR',
'WhisperASR',
'OpenAI Whisper Speech Recognition',
0,
0,
'{"type": "whisper", "model_name": "base", "device": "auto", "language": null, "output_dir": "tmp/"}',
'https://github.com/openai/whisper',
'Whisper ASR Configuration Instructions:
1. Whisper is an offline speech recognition library, supports multiple languages
2. Models are downloaded automatically when first used, or manually via docker-setup.sh
3. Available models: tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large-v1, large-v2, large-v3
4. Completely offline operation, no network connection required after model download
5. Output files saved in tmp/ directory
Usage Steps:
1. Choose appropriate model based on your accuracy vs speed requirements
2. Models are automatically downloaded to models/whisper/ directory when first used
3. For manual download, run: /opt/xiaozhi-server/models/whisper/download_all_models.sh
4. Note: Whisper provides excellent accuracy for multilingual speech recognition
Performance Notes:
- tiny/tiny.en: Fastest, lowest accuracy (~39 MB)
- base/base.en: Good balance of speed and accuracy (~74 MB)
- small/small.en: Better accuracy, slower than base (~244 MB)
- medium/medium.en: High accuracy, significantly slower (~769 MB)
- large-v1/v2/v3: Highest accuracy, slowest processing (~1550 MB)',
12,
NULL,
NULL,
NULL,
NULL
);

-- Add Whisper ASR provider to ai_model_provider table
INSERT INTO `ai_model_provider` VALUES (
'SYSTEM_ASR_WhisperASR',
'ASR',
'whisper',
'OpenAI Whisper Speech Recognition',
'[{"key": "model_name", "type": "string", "label": "Model Name"}, {"key": "device", "type": "string", "label": "Device (auto/cpu/cuda)"}, {"key": "language", "type": "string", "label": "Language (null for auto-detect)"}, {"key": "output_dir", "type": "string", "label": "Output Directory"}]',
12,
1,
'2025-01-01 00:00:00',
1,
'2025-01-01 00:00:00'
);
