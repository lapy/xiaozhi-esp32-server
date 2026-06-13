package xiaozhi.modules.sms.service.imp;

import com.twilio.Twilio;
import com.twilio.rest.api.v2010.account.Message;
import com.twilio.type.PhoneNumber;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.modules.sms.service.SmsService;
import xiaozhi.modules.sys.service.SysParamsService;

@Service
@AllArgsConstructor
@Slf4j
public class TwilioSmsService implements SmsService {
    private final SysParamsService sysParamsService;
    private final RedisUtils redisUtils;

    @Override
    public void sendVerificationCodeSms(String phone, String verificationCode) {
        try {
            // Initialize Twilio client
            initializeTwilioClient();
            
            // Get Twilio configuration parameters
            String fromPhoneNumber = sysParamsService.getValue(Constant.SysMSMParam
                    .TWILIO_SMS_PHONE_NUMBER.getValue(), true);
            String templateMessage = sysParamsService.getValue(Constant.SysMSMParam
                    .TWILIO_SMS_TEMPLATE_MESSAGE.getValue(), true);
            
            // Format the SMS message with verification code
            String messageBody = String.format(templateMessage, verificationCode);
            
            // Send SMS using Twilio
            Message message = Message.creator(
                    new PhoneNumber(phone),      // To phone number
                    new PhoneNumber(fromPhoneNumber), // From phone number (Twilio number)
                    messageBody                  // Message body
            ).create();
            
            log.info("SMS sent successfully. Message SID: {}", message.getSid());
            
        } catch (Exception e) {
            // If sending failed, refund this sending count
            String todayCountKey = RedisKeys.getSMSTodayCountKey(phone);
            redisUtils.delete(todayCountKey);
            
            // Log error and throw exception
            log.error("Failed to send SMS via Twilio: {}", e.getMessage(), e);
            throw new RenException(ErrorCode.SMS_SEND_FAILED);
        }
    }

    /**
     * Initialize Twilio client with credentials
     */
    private void initializeTwilioClient() {
        try {
            String accountSid = sysParamsService.getValue(Constant.SysMSMParam
                    .TWILIO_SMS_ACCOUNT_SID.getValue(), true);
            String authToken = sysParamsService.getValue(Constant.SysMSMParam
                    .TWILIO_SMS_AUTH_TOKEN.getValue(), true);
            
            Twilio.init(accountSid, authToken);
            
        } catch (Exception e) {
            log.error("Failed to initialize Twilio client: {}", e.getMessage(), e);
            throw new RenException(ErrorCode.SMS_CONNECTION_FAILED);
        }
    }
}
