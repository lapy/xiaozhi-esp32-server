package xiaozhi.modules.model.dto;

import java.io.Serial;

import cn.hutool.json.JSONObject;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "Model provider/vendor")
public class ModelConfigBodyDTO {

    @Serial
    private static final long serialVersionUID = 1L;

    // @Schema(description = "Model type (Memory/ASR/VAD/LLM/TTS)")
    // private String modelType;
    //
    @Schema(description = "Model code (e.g. AliLLM, AliBLTTS)")
    private String modelCode;

    @Schema(description = "Model name")
    private String modelName;

    @Schema(description = "Is default configuration (0=No 1=Yes)")
    private Integer isDefault;

    @Schema(description = "Is enabled")
    private Integer isEnabled;

    @Schema(description = "Model configuration (JSON format)")
    private JSONObject configJson;

    @Schema(description = "Official documentation link")
    private String docLink;

    @Schema(description = "Remarks")
    private String remark;

    @Schema(description = "Sort order")
    private Integer sort;
}
