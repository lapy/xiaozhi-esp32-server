package xiaozhi.modules.model.support;

import cn.hutool.json.JSONObject;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import xiaozhi.modules.model.entity.ModelConfigEntity;

class ProviderPolicyTest {

    @Test
    void allowsWesternRoleConfigDefaults() {
        Assertions.assertTrue(ProviderPolicy.isAllowedModelConfig(model("LLM_OpenAILLM", "OpenAILLM", "OpenAI GPT", openAiConfig())));
        Assertions.assertTrue(ProviderPolicy.isAllowedModelConfig(model("TTS_EdgeTTS", "EdgeTTS", "Edge TTS", edgeConfig())));
        Assertions.assertTrue(ProviderPolicy.isAllowedModelConfig(model("VAD_SileroVAD", "SileroVAD", "Voice Activity Detection", sileroConfig())));
        Assertions.assertTrue(ProviderPolicy.isAllowedModelConfig(model("ASR_VoskASR", "VoskASR", "VOSK Offline Speech Recognition", voskConfig())));
    }

    @Test
    void blocksChineseProviderSeeds() {
        Assertions.assertFalse(ProviderPolicy.isAllowedModelConfig(model("LLM_DoubaoLLM", "DoubaoLLM", "Doubao", openAiConfig())));
        Assertions.assertFalse(ProviderPolicy.isAllowedModelConfig(model("ASR_FunASR", "FunASR", "FunASR", voskConfig())));
        Assertions.assertFalse(ProviderPolicy.isAllowedModelConfig(model("LLM_DeepSeekLLM", "DeepSeekLLM", "DeepSeek", deepSeekConfig())));
    }

    private static ModelConfigEntity model(String id, String modelCode, String modelName, JSONObject configJson) {
        ModelConfigEntity entity = new ModelConfigEntity();
        entity.setId(id);
        entity.setModelCode(modelCode);
        entity.setModelName(modelName);
        entity.setConfigJson(configJson);
        return entity;
    }

    private static JSONObject openAiConfig() {
        JSONObject config = new JSONObject();
        config.set("type", "openai");
        config.set("model_name", "gpt-4o-mini");
        return config;
    }

    private static JSONObject edgeConfig() {
        JSONObject config = new JSONObject();
        config.set("voice", "en-US-AriaNeural");
        return config;
    }

    private static JSONObject sileroConfig() {
        JSONObject config = new JSONObject();
        config.set("type", "silero");
        return config;
    }

    private static JSONObject voskConfig() {
        JSONObject config = new JSONObject();
        config.set("type", "vosk");
        return config;
    }

    private static JSONObject deepSeekConfig() {
        JSONObject config = new JSONObject();
        config.set("type", "openai");
        config.set("model_name", "deepseek-chat");
        config.set("base_url", "https://api.deepseek.com");
        return config;
    }
}
