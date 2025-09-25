package xiaozhi.modules.device.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * Device binding DTO
 * 
 * @author zjy
 * @since 2025-3-28
 */
@Data
@AllArgsConstructor
@Schema(description = "Device connection header information")
public class DeviceBindDTO {

    @Schema(description = "MAC address")
    private String macAddress;

    @Schema(description = "Associated user ID")
    private Long userId;

    @Schema(description = "Agent ID")
    private String agentId;

}