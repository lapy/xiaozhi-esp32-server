package xiaozhi.modules.sys.vo;

import java.util.Date;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Admin paginated user display VO
 * @ zjy
 * 
 * @since 2025-3-25
 */
@Data
public class AdminPageUserVO {

    @Schema(description = "Device Count")
    private String deviceCount;

    @Schema(description = "Mobile Number")
    private String mobile;

    @Schema(description = "Status")
    private Integer status;

    @Schema(description = "User ID")
    private String userid;

    @Schema(description = "Registration Time")
    private Date createDate;
}
