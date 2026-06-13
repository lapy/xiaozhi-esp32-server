package xiaozhi.modules.sys.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * Dictionary Data VO
 */
@Data
@Schema(description = "Dictionary Data VO")
public class SysDictDataVO implements Serializable {
    @Schema(description = "Primary Key")
    private Long id;

    @Schema(description = "Dictionary Type ID")
    private Long dictTypeId;

    @Schema(description = "Dictionary Label")
    private String dictLabel;

    @Schema(description = "Dictionary Value")
    private String dictValue;

    @Schema(description = "Remark")
    private String remark;

    @Schema(description = "Sort Order")
    private Integer sort;

    @Schema(description = "Creator")
    private Long creator;

    @Schema(description = "Creator Name")
    private String creatorName;

    @Schema(description = "Create Time")
    private Date createDate;

    @Schema(description = "Updater")
    private Long updater;

    @Schema(description = "Updater Name")
    private String updaterName;

    @Schema(description = "Update time")
    private Date updateDate;
}
