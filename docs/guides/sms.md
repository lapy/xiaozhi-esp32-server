# Twilio SMS Integration

This document describes how to configure and use Twilio SMS service for sending verification codes in the Xiaozhi system.

## Overview

Twilio SMS service has been implemented as a replacement for the previous Aliyun SMS service, providing Western-based SMS functionality for user verification.

## Configuration

### 1. Twilio Account Setup

1. Visit [Twilio Console](https://console.twilio.com/)
2. Create a new account or sign in to existing account
3. Navigate to the Console Dashboard
4. Get your Account SID and Auth Token from the Account Info section
5. Purchase a phone number for sending SMS messages

### 2. System Configuration

Configure the following parameters in the system configuration:

#### Required Parameters

- **twilio.sms.account_sid**: Your Twilio Account SID
- **twilio.sms.auth_token**: Your Twilio Auth Token  
- **twilio.sms.phone_number**: Your Twilio phone number (in E.164 format, e.g., +1234567890)
- **twilio.sms.template_message**: SMS message template (default: "Your verification code is: %s")

#### Optional Parameters

- **server.sms_max_send_count**: Maximum SMS messages per phone number per day (default: 10)
- **server.enable_mobile_register**: Enable mobile phone registration (default: false)

### 3. Configuration Examples

#### Basic Configuration
```
twilio.sms.account_sid=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
twilio.sms.auth_token=your_auth_token_here
twilio.sms.phone_number=+1234567890
twilio.sms.template_message=Your verification code is: %s
```

#### Custom Template
```
twilio.sms.template_message=Welcome to Xiaozhi! Your verification code is %s. This code will expire in 10 minutes.
```

## Features

### SMS Verification
- Send verification codes via SMS
- Rate limiting (configurable daily limit per phone number)
- 60-second cooldown between SMS sends
- Automatic retry mechanism on failure

### Error Handling
- Connection failure detection
- Invalid phone number handling
- Rate limit enforcement
- Comprehensive error logging

## API Usage

### Sending Verification Code

```java
@Autowired
private SmsService smsService;

// Send verification code
smsService.sendVerificationCodeSms("+1234567890", "123456");
```

### Rate Limiting

The system implements the following rate limiting:
- **Daily Limit**: Configurable via `server.sms_max_send_count` (default: 10 messages per day)
- **Cooldown**: 60 seconds between consecutive SMS sends to the same number
- **Redis Storage**: Rate limit data stored in Redis for persistence

## Security Considerations

1. **API Keys**: Store Twilio credentials securely in system configuration
2. **Rate Limiting**: Prevents SMS abuse and spam
3. **Phone Number Validation**: Ensures proper E.164 format
4. **Error Handling**: Prevents credential exposure in logs

## Troubleshooting

### Common Issues

1. **Invalid Phone Number Format**
   - Ensure phone numbers are in E.164 format (+1234567890)
   - Remove spaces, dashes, and parentheses

2. **Authentication Failures**
   - Verify Account SID and Auth Token are correct
   - Check if credentials have SMS permissions

3. **Rate Limiting**
   - Check daily send limits in Twilio console
   - Verify system rate limiting configuration

4. **Phone Number Issues**
   - Ensure Twilio phone number is verified
   - Check if phone number supports SMS in target region

### Error Codes

- `SMS_SEND_FAILED`: Failed to send SMS message
- `SMS_CONNECTION_FAILED`: Failed to connect to Twilio service
- `SMS_SEND_TOO_FREQUENTLY`: Rate limit exceeded (60-second cooldown)
- `TODAY_SMS_LIMIT_REACHED`: Daily limit exceeded

## Migration from Aliyun SMS

If migrating from the previous Aliyun SMS service:

1. Remove old Aliyun SMS configuration parameters
2. Add new Twilio SMS configuration parameters
3. Update phone number formats to E.164 standard
4. Test SMS functionality with new configuration

## Support

For Twilio-specific issues, refer to:
- [Twilio SMS Documentation](https://www.twilio.com/docs/sms)
- [Twilio Console](https://console.twilio.com/)
- [Twilio Support](https://support.twilio.com/)
