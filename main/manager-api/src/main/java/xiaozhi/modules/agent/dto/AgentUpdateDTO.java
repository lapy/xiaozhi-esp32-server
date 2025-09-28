package xiaozhi.modules.agent.dto;

import java.io.Serializable;
import java.util.HashMap;
import java.util.List;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Agent update DTO
 * Specifically for updating agents, id field is required to identify the agent to update
 * Other fields are optional, only update provided fields
 */
@Data
@Schema(description = "Agent update object")
public class AgentUpdateDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @Schema(description = "Agent code", example = "AGT_1234567890", nullable = true)
    private String agentCode;

    @Schema(description = "Agent name", example = "Customer Service Assistant", nullable = true)
    private String agentName;

    @Schema(description = "ASR model identifier", example = "asr_model_02", nullable = true)
    private String asrModelId;

    @Schema(description = "VAD model identifier", example = "vad_model_02", nullable = true)
    private String vadModelId;

    @Schema(description = "LLM model identifier", example = "llm_model_02", nullable = true)
    private String llmModelId;

    @Schema(description = "VLLM model identifier", example = "vllm_model_02", required = false)
    private String vllmModelId;

    @Schema(description = "TTS model identifier", example = "tts_model_02", required = false)
    private String ttsModelId;

    @Schema(description = "Voice identifier", example = "voice_02", nullable = true)
    private String ttsVoiceId;

    @Schema(description = "Memory model identifier", example = "mem_model_02", nullable = true)
    private String memModelId;

    @Schema(description = "Intent model identifier", example = "intent_model_02", nullable = true)
    private String intentModelId;

    @Schema(description = "Plugin function information", nullable = true)
    private List<FunctionInfo> functions;

    @Schema(description = "Role setting parameters", example = "You are a professional customer service assistant, responsible for answering user questions and providing help", nullable = true)
    private String systemPrompt;

    @Schema(description = "Summary memory", example = "Build a growing dynamic memory network that retains key information in limited space while intelligently maintaining information evolution trajectories\n"
            + "Based on conversation records, summarize important user information to provide more personalized service in future conversations", nullable = true)
    private String summaryMemory;

    @Schema(description = "Chat history configuration (0=no record 1=text only 2=text and voice)", example = "3", nullable = true)
    private Integer chatHistoryConf;

    @Schema(description = "Language code", example = "zh_CN", nullable = true)
    private String langCode;

    @Schema(description = "Interaction language", example = "English", nullable = true)
    private String language;

    @Schema(description = "Sort order", example = "1", nullable = true)
    private Integer sort;

    @Data
    @Schema(description = "Plugin function information")
    public static class FunctionInfo implements Serializable {
        @Schema(description = "Plugin ID", example = "plugin_01")
        private String pluginId;

        @Schema(description = "Function parameter information", nullable = true)
        private HashMap<String, Object> paramInfo;

        private static final long serialVersionUID = 1L;
    }
}