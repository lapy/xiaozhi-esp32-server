package xiaozhi.modules.timbre.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Timbre pagination parameters DTO
 * 
 * @author zjy
 * @since 2025-3-21
 */
@Data
@Schema(description = "Timbre pagination parameters")
public class TimbrePageDTO {

    @Schema(description = "Corresponding TTS Model Primary Key")
    @NotBlank(message = "{timbre.ttsModelId.require}")
    private String ttsModelId;

    @Schema(description = "Timbre Name")
    private String name;

    @Schema(description = "Page Number")
    private String page;

    @Schema(description = "Display Column Count")
    private String limit;
}
