package xiaozhi.modules.sms.service;

/**
 * SMS service method definition interface
 *
 * @author zjy
 * @since 2025-05-12
 */
public interface SmsService {

    /**
     * Send verification code SMS
     * @param phone Phone number
     * @param VerificationCode Verification code
     */
    void sendVerificationCodeSms(String phone, String VerificationCode) ;
}
