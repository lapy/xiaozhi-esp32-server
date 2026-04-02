package xiaozhi.modules.security.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Login form DTO.
 */
@Data
@Schema(description = "Login form")
public class LoginDTO implements Serializable {

    @Schema(description = "Phone number or username")
    @NotBlank(message = "{sysuser.username.require}")
    private String username;

    @Schema(description = "Password")
    @NotBlank(message = "{sysuser.password.require}")
    private String password;

    @Schema(description = "Mobile verification code")
    private String mobileCaptcha;

    @Schema(description = "Captcha identifier")
    @NotBlank(message = "{sysuser.uuid.require}")
    private String captchaId;

}
