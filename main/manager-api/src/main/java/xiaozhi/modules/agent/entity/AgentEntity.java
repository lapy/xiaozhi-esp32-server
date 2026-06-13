package xiaozhi.modules.agent.entity;

import java.math.BigDecimal;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@TableName("ai_agent")
@Schema(description = "Agent information")
public class AgentEntity {

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "Unique agent ID")
    private String id;

    @Schema(description = "Owner user ID")
    private Long userId;

    @Schema(description = "Agent code")
    private String agentCode;

    @Schema(description = "Agent name")
    private String agentName;

    @Schema(description = "ASR model ID")
    private String asrModelId;

    @Schema(description = "VAD model ID")
    private String vadModelId;

    @Schema(description = "LLM model ID")
    private String llmModelId;

    @Schema(description = "Small model ID")
    private String slmModelId;

    @Schema(description = "VLLM model ID")
    private String vllmModelId;

    @Schema(description = "TTS model ID")
    private String ttsModelId;

    @Schema(description = "Voice ID")
    private String ttsVoiceId;

    @Schema(description = "Voice language")
    private String ttsLanguage;

    @Schema(description = "TTS volume")
    private Integer ttsVolume;

    @Schema(description = "TTS speed")
    private Integer ttsRate;

    @Schema(description = "TTS pitch")
    private Integer ttsPitch;

    @Schema(description = "Memory model ID")
    private String memModelId;

    @Schema(description = "Intent model ID")
    private String intentModelId;

    @Schema(description = "Chat-history mode (0 disabled, 1 text only, 2 text and audio)")
    private Integer chatHistoryConf;

    @Schema(description = "System prompt")
    private String systemPrompt;

    @Schema(description = "Summary memory", example = "Build a growing memory graph that preserves key information while tracking how it evolves over time.\n" +
            "Summarize the user's important details from the conversation so future interactions can be more personalized.", required = false)
    private String summaryMemory;

    @Schema(description = "Language code")
    private String langCode;

    @Schema(description = "Interaction language")
    private String language;

    @Schema(description = "Sort order")
    private Integer sort;

    @Schema(description = "Created by")
    private Long creator;

    @Schema(description = "Created at")
    private Date createdAt;

    @Schema(description = "Updated by")
    private Long updater;

    @Schema(description = "Updated at")
    private Date updatedAt;
}
