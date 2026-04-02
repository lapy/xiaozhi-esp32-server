package xiaozhi.modules.security.controller;

import java.io.IOException;
import java.util.Calendar;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.page.TokenDTO;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.JsonUtils;
import xiaozhi.common.utils.Result;
import xiaozhi.common.utils.Sm2DecryptUtil;
import xiaozhi.common.validator.AssertUtils;
import xiaozhi.common.validator.ValidatorUtils;
import xiaozhi.modules.security.dto.LoginDTO;
import xiaozhi.modules.security.dto.SmsVerificationDTO;
import xiaozhi.modules.security.password.PasswordUtils;
import xiaozhi.modules.security.service.CaptchaService;
import xiaozhi.modules.security.service.SysUserTokenService;
import xiaozhi.modules.security.user.SecurityUser;
import xiaozhi.modules.sys.dto.PasswordDTO;
import xiaozhi.modules.sys.dto.RetrievePasswordDTO;
import xiaozhi.modules.sys.dto.SysUserDTO;
import xiaozhi.modules.sys.service.SysDictDataService;
import xiaozhi.modules.sys.service.SysParamsService;
import xiaozhi.modules.sys.service.SysUserService;
import xiaozhi.modules.sys.vo.SysDictDataItem;

/**
 * Login controller.
 */
@Slf4j
@AllArgsConstructor
@RestController
@RequestMapping("/user")
@Tag(name = "Login Management")
public class LoginController {
    private final SysUserService sysUserService;
    private final SysUserTokenService sysUserTokenService;
    private final CaptchaService captchaService;
    private final SysParamsService sysParamsService;
    private final SysDictDataService sysDictDataService;

    @GetMapping("/captcha")
    @Operation(summary = "Captcha")
    public void captcha(HttpServletResponse response, String uuid) throws IOException {
        // uuid is required.
        AssertUtils.isBlank(uuid, ErrorCode.IDENTIFIER_NOT_NULL);
        // Generate the captcha.
        captchaService.create(response, uuid);
    }

    @PostMapping("/smsVerification")
    @Operation(summary = "SMS Verification Code")
    public Result<Void> smsVerification(@RequestBody SmsVerificationDTO dto) {
        // Validate the image captcha first.
        boolean validate = captchaService.validate(dto.getCaptchaId(), dto.getCaptcha(), false);
        if (!validate) {
            throw new RenException(ErrorCode.SMS_CAPTCHA_ERROR);
        }

        Boolean isMobileRegister = sysParamsService
                .getValueObject(Constant.SysMSMParam.SERVER_ENABLE_MOBILE_REGISTER.getValue(), Boolean.class);
        if (!isMobileRegister) {
            throw new RenException(ErrorCode.MOBILE_REGISTER_DISABLED);
        }
        // Send the SMS verification code.
        captchaService.sendSMSValidateCode(dto.getPhone());
        return new Result<>();
    }

    @PostMapping("/login")
    @Operation(summary = "Login")
    public Result<TokenDTO> login(@RequestBody LoginDTO login) {
        String password = login.getPassword();

        // Decrypt the password and validate the captcha.
        String actualPassword = Sm2DecryptUtil.decryptAndValidateCaptcha(
                password, login.getCaptchaId(), captchaService, sysParamsService);

        login.setPassword(actualPassword);

        // Load the user by username.
        SysUserDTO userDTO = sysUserService.getByUsername(login.getUsername());
        // Ensure the user exists.
        if (userDTO == null) {
            throw new RenException(ErrorCode.ACCOUNT_PASSWORD_ERROR);
        }
        // Ensure the password matches.
        if (!PasswordUtils.matches(login.getPassword(), userDTO.getPassword())) {
            throw new RenException(ErrorCode.ACCOUNT_PASSWORD_ERROR);
        }
        return sysUserTokenService.createToken(userDTO.getId());
    }

    @PostMapping("/register")
    @Operation(summary = "Register")
    public Result<Void> register(@RequestBody LoginDTO login) {
        if (!sysUserService.getAllowUserRegister()) {
            throw new RenException(ErrorCode.USER_REGISTER_DISABLED);
        }

        String password = login.getPassword();

        // Decrypt the password and validate the captcha.
        String actualPassword = Sm2DecryptUtil.decryptAndValidateCaptcha(
                password, login.getCaptchaId(), captchaService, sysParamsService);

        login.setPassword(actualPassword);

        // Check whether mobile registration is enabled.
        Boolean isMobileRegister = sysParamsService
                .getValueObject(Constant.SysMSMParam.SERVER_ENABLE_MOBILE_REGISTER.getValue(), Boolean.class);
        boolean validate;
        if (isMobileRegister) {
            // Validate that the username is a phone number.
            boolean validPhone = ValidatorUtils.isValidPhone(login.getUsername());
            if (!validPhone) {
                throw new RenException(ErrorCode.USERNAME_NOT_PHONE);
            }
            // Validate the SMS verification code.
            validate = captchaService.validateSMSValidateCode(login.getUsername(), login.getMobileCaptcha(), false);
            if (!validate) {
                throw new RenException(ErrorCode.SMS_CODE_ERROR);
            }
        }

        // Load the user by username.
        SysUserDTO userDTO = sysUserService.getByUsername(login.getUsername());
        if (userDTO != null) {
            throw new RenException(ErrorCode.PHONE_ALREADY_REGISTERED);
        }
        userDTO = new SysUserDTO();
        userDTO.setUsername(login.getUsername());
        userDTO.setPassword(login.getPassword());
        sysUserService.save(userDTO);
        return new Result<>();
    }

    @GetMapping("/info")
    @Operation(summary = "Get User Info")
    public Result<UserDetail> info() {
        UserDetail user = SecurityUser.getUser();
        Result<UserDetail> result = new Result<>();
        result.setData(user);
        return result;
    }

    @PutMapping("/change-password")
    @Operation(summary = "Change Password")
    public Result<?> changePassword(@RequestBody PasswordDTO passwordDTO) {
        // Validate required fields.
        ValidatorUtils.validateEntity(passwordDTO);
        Long userId = SecurityUser.getUserId();
        sysUserTokenService.changePassword(userId, passwordDTO);
        return new Result<>();
    }

    @PutMapping("/retrieve-password")
    @Operation(summary = "Retrieve Password")
    public Result<?> retrievePassword(@RequestBody RetrievePasswordDTO dto) {
        // Check whether mobile registration is enabled.
        Boolean isMobileRegister = sysParamsService
                .getValueObject(Constant.SysMSMParam.SERVER_ENABLE_MOBILE_REGISTER.getValue(), Boolean.class);
        if (!isMobileRegister) {
            throw new RenException(ErrorCode.RETRIEVE_PASSWORD_DISABLED);
        }
        // Validate required fields.
        ValidatorUtils.validateEntity(dto);
        // Validate that the phone number format is supported.
        boolean validPhone = ValidatorUtils.isValidPhone(dto.getPhone());
        if (!validPhone) {
            throw new RenException(ErrorCode.PHONE_FORMAT_ERROR);
        }

        // Load the user by username.
        SysUserDTO userDTO = sysUserService.getByUsername(dto.getPhone());
        if (userDTO == null) {
            throw new RenException(ErrorCode.PHONE_NOT_REGISTERED);
        }
        // Validate the SMS verification code.
        boolean validate = captchaService.validateSMSValidateCode(dto.getPhone(), dto.getCode(), false);
        // Stop if validation fails.
        if (!validate) {
            throw new RenException(ErrorCode.SMS_CODE_ERROR);
        }

        String password = dto.getPassword();

        // Decrypt the password and validate the captcha.
        String actualPassword = Sm2DecryptUtil.decryptAndValidateCaptcha(
                password, dto.getCaptchaId(), captchaService, sysParamsService);

        dto.setPassword(actualPassword);

        sysUserService.changePasswordDirectly(userDTO.getId(), dto.getPassword());
        return new Result<>();
    }

    @GetMapping("/pub-config")
    @Operation(summary = "Public Config")
    public Result<Map<String, Object>> pubConfig() {
        Map<String, Object> config = new HashMap<>();
        config.put("enableMobileRegister", sysParamsService
                .getValueObject(Constant.SysMSMParam.SERVER_ENABLE_MOBILE_REGISTER.getValue(), Boolean.class));
        config.put("version", Constant.VERSION);
        config.put("year", "©" + Calendar.getInstance().get(Calendar.YEAR));
        config.put("allowUserRegister", sysUserService.getAllowUserRegister());
        List<SysDictDataItem> list = sysDictDataService.getDictDataByType(Constant.DictType.MOBILE_AREA.getValue());
        config.put("mobileAreaList", list);
        config.put("beianIcpNum", sysParamsService.getValue(Constant.SysBaseParam.BEIAN_ICP_NUM.getValue(), true));
        config.put("beianGaNum", sysParamsService.getValue(Constant.SysBaseParam.BEIAN_GA_NUM.getValue(), true));
        config.put("name", sysParamsService.getValue(Constant.SysBaseParam.SERVER_NAME.getValue(), true));

        // SM2 public key
        String publicKey = sysParamsService.getValue(Constant.SM2_PUBLIC_KEY, true);
        if (StringUtils.isBlank(publicKey)) {
            throw new RenException(ErrorCode.SM2_KEY_NOT_CONFIGURED);
        }
        config.put("sm2PublicKey", publicKey);

        // Load the system-web.menu parameter.
        String menuConfig = sysParamsService.getValue("system-web.menu", true);
        if (StringUtils.isNotBlank(menuConfig)) {
            config.put("systemWebMenu", JsonUtils.parseObject(menuConfig, Object.class));
        }

        return new Result<Map<String, Object>>().ok(config);
    }
}
