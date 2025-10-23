package xiaozhi.modules.model.dto;

import java.io.Serializable;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import xiaozhi.common.validator.group.UpdateGroup;

@Data
@Schema(description = "Model provider/vendor")
public class ModelProviderDTO implements Serializable {
    @Schema(description = "Primary key")
    @NotBlank(message = "ID cannot be empty", groups = UpdateGroup.class)
    private String id;

    @Schema(description = "Model type (Memory/ASR/VAD/LLM/TTS)")
    @NotBlank(message = "Model type cannot be empty")
    private String modelType;

    @Schema(description = "Provider type")
    @NotBlank(message = "Provider code cannot be empty")
    private String providerCode;

    @Schema(description = "Provider name")
    @NotBlank(message = "Name cannot be empty")
    private String name;

    @Schema(description = "Provider field list (JSON format)")
    @TableField(typeHandler = JacksonTypeHandler.class)
    @NotBlank(message = "Fields (JSON format) cannot be empty")
    private String fields;

    @Schema(description = "Sort order")
    @NotNull(message = "Sort cannot be empty")
    private Integer sort;

    @Schema(description = "Updater")
    @TableField(fill = FieldFill.UPDATE)
    private Long updater;

    @Schema(description = "Update time")
    @TableField(fill = FieldFill.UPDATE)
    private Date updateDate;

    @Schema(description = "Creator")
    @TableField(fill = FieldFill.INSERT)
    private Long creator;

    @Schema(description = "Creation time")
    @TableField(fill = FieldFill.INSERT)
    private Date createDate;
}
