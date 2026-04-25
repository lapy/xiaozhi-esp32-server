-- Remove Chinese-only and downstream-deleted providers from the westernized build.
-- This keeps upstream migration history append-only while preserving downstream behavior.

DELETE FROM `ai_tts_voice`
WHERE `tts_model_id` IN (
    'TTS_HuoshanDoubleStreamTTS',
    'TTS_XunFeiStreamTTS',
    'TTS_MinimaxStreamTTS',
    'TTS_AliyunStreamTTS',
    'TTS_DoubaoTTS',
    'TTS_TencentTTS',
    'TTS_AliyunTTS',
    'TTS_CozeCnTTS',
    'TTS_FishSpeech',
    'TTS_VolcesAiGatewayTTS',
    'TTS_LinkeraiTTS'
)
OR `id` IN (
    'TTS_Kokoro_0033',
    'TTS_Kokoro_0034',
    'TTS_Kokoro_0035',
    'TTS_Kokoro_0036',
    'TTS_Kokoro_0037',
    'TTS_Kokoro_0038',
    'TTS_Kokoro_0039',
    'TTS_Kokoro_0040'
);

DELETE FROM `ai_model_provider`
WHERE `provider_code` IN (
    'aliyun',
    'aliyun_stream',
    'aliyunbl_stream',
    'alibl_stream',
    'baidu',
    'coze',
    'cozecn',
    'doubao',
    'doubao_stream',
    'fastgpt',
    'fishspeech',
    'fun_local',
    'fun_server',
    'gpt_sovits_v2',
    'gpt_sovits_v3',
    'huoshan_double_stream',
    'index_stream',
    'linkerai',
    'minimax_httpstream',
    'paddle_speech',
    'qwen3_asr_flash',
    'siliconflow',
    'tencent',
    'ttson',
    'xunfei_stream'
)
OR `id` IN (
    'SYSTEM_TTS_HSDSTTS',
    'SYSTEM_TTS_cozecn'
);

DELETE FROM `ai_model_config`
WHERE `id` IN (
    'LLM_AliAppLLM',
    'LLM_DoubaoLLM',
    'LLM_XunfeiSparkLLM',
    'ASR_AliyunASR',
    'ASR_AliyunBLStream',
    'ASR_AliyunStreamASR',
    'ASR_BaiduASR',
    'ASR_DoubaoASR',
    'ASR_DoubaoStreamASR',
    'ASR_Qwen3Flash',
    'ASR_TencentASR',
    'ASR_XunfeiStream',
    'TTS_AliyunStreamTTS',
    'TTS_AliyunTTS',
    'TTS_CozeCnTTS',
    'TTS_DoubaoTTS',
    'TTS_FishSpeech',
    'TTS_HuoshanDoubleStreamTTS',
    'TTS_LinkeraiTTS',
    'TTS_MinimaxStreamTTS',
    'TTS_TencentTTS',
    'TTS_VolcesAiGatewayTTS',
    'TTS_XunFeiStreamTTS'
)
OR JSON_UNQUOTE(JSON_EXTRACT(`config_json`, '$.type')) IN (
    'aliyun',
    'aliyun_stream',
    'aliyunbl_stream',
    'alibl_stream',
    'baidu',
    'coze',
    'cozecn',
    'doubao',
    'doubao_stream',
    'fastgpt',
    'fishspeech',
    'fun_local',
    'fun_server',
    'gpt_sovits_v2',
    'gpt_sovits_v3',
    'huoshan_double_stream',
    'index_stream',
    'linkerai',
    'minimax_httpstream',
    'paddle_speech',
    'qwen3_asr_flash',
    'siliconflow',
    'tencent',
    'ttson',
    'xunfei_stream'
);
