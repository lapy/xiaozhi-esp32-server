package xiaozhi.modules.security.dto;

import java.io.Serializable;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * Login form
 */
@Data
@Schema(description = "Login form")
public class LoginDTO implements Serializable {

    @Schema(description = "Mobile number")
    @NotBlank(message = "{sysuser.username.require}")
    private String username;

    @Schema(description = "Password")
    @NotBlank(message = "{sysuser.password.require}")
    private String password;

    @Schema(description = "Verification code")
    @NotBlank(message = "{sysuser.captcha.require}")
    private String captcha;

    @Schema(description = "Mobile verification code")
    private String mobileCaptcha;

    @Schema(description = "Unique identifier")
    @NotBlank(message = "{sysuser.uuid.require}")
    private String captchaId;

}