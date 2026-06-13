package xiaozhi.modules.voiceclone.dto;

import java.util.Date;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Voice-clone response DTO.
 * Used by the frontend to display voice-clone details including model and user names.
 */
@Data
@Schema(description = "Voice-clone response DTO")
public class VoiceCloneResponseDTO {

    @Schema(description = "Unique ID")
    private String id;

    @Schema(description = "Voice name")
    private String name;

    @Schema(description = "Model ID")
    private String modelId;

    @Schema(description = "Model name")
    private String modelName;

    @Schema(description = "Voice ID")
    private String voiceId;

    @Schema(description = "Language")
    private String languages;

    @Schema(description = "User ID linked to the user table")
    private Long userId;

    @Schema(description = "User name")
    private String userName;

    @Schema(description = "Training status: 0 pending, 1 running, 2 success, 3 failed")
    private Integer trainStatus;

    @Schema(description = "Training error reason")
    private String trainError;

    @Schema(description = "Created at")
    private Date createDate;

    @Schema(description = "Whether audio data exists")
    private Boolean hasVoice;
}
