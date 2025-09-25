package xiaozhi.modules.agent.entity;

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
    @Schema(description = "Agent unique identifier")
    private String id;

    @Schema(description = "Owner user ID")
    private Long userId;

    @Schema(description = "Agent code")
    private String agentCode;

    @Schema(description = "Agent name")
    private String agentName;

    @Schema(description = "ASR model identifier")
    private String asrModelId;

    @Schema(description = "VAD model identifier")
    private String vadModelId;

    @Schema(description = "LLM model identifier")
    private String llmModelId;

    @Schema(description = "VLLM model identifier")
    private String vllmModelId;

    @Schema(description = "TTS model identifier")
    private String ttsModelId;

    @Schema(description = "Voice identifier")
    private String ttsVoiceId;

    @Schema(description = "Memory model identifier")
    private String memModelId;

    @Schema(description = "Intent model identifier")
    private String intentModelId;

    @Schema(description = "Chat history configuration (0=no record 1=text only 2=text and voice)")
    private Integer chatHistoryConf;

    @Schema(description = "Role setting parameters")
    private String systemPrompt;

    @Schema(description = "Summary memory", example = "Build a growing dynamic memory network that retains key information in limited space while intelligently maintaining information evolution trajectories\n" +
            "Based on conversation records, summarize important user information to provide more personalized service in future conversations", required = false)
    private String summaryMemory;

    @Schema(description = "Language code")
    private String langCode;

    @Schema(description = "Interaction language")
    private String language;

    @Schema(description = "Sort order")
    private Integer sort;

    @Schema(description = "Creator")
    private Long creator;

    @Schema(description = "Creation time")
    private Date createdAt;

    @Schema(description = "Updater")
    private Long updater;

    @Schema(description = "Update time")
    private Date updatedAt;
}