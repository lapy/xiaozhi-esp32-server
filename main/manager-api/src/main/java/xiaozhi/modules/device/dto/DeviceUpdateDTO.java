package xiaozhi.modules.device.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.io.Serializable;

/**
 * Device update DTO
 */
@Data
public class DeviceUpdateDTO implements Serializable {
    /**
    * Auto update status
    */
    @Max(1)
    @Min(0)
    private Integer autoUpdate;

    /**
    * Device alias
    */
    @Size(max = 64)
    private String alias;

    private static final long serialVersionUID = 1L;
}
