package xiaozhi.modules.model.dto;

import java.io.Serial;

import cn.hutool.json.JSONObject;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "Model provider payload")
public class ModelConfigBodyDTO {

    @Serial
    private static final long serialVersionUID = 1L;

    @Schema(description = "Model ID. Generated automatically when omitted")
    private String id;

    @Schema(description = "Model code, for example AliLLM or OpenAITTS")
    private String modelCode;

    @Schema(description = "Model name")
    private String modelName;

    @Schema(description = "Default flag (0 no, 1 yes)")
    private Integer isDefault;

    @Schema(description = "Enabled flag")
    private Integer isEnabled;

    @Schema(description = "Model configuration in JSON format")
    private JSONObject configJson;

    @Schema(description = "Official documentation link")
    private String docLink;

    @Schema(description = "Remarks")
    private String remark;

    @Schema(description = "Sort order")
    private Integer sort;
}
