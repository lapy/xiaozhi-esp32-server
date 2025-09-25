# Alibaba Cloud SMS Integration Guide

Login to Alibaba Cloud console and enter the "SMS Service" page: https://dysms.console.aliyun.com/overview

## Step 1: Add Signature
![Step](images/alisms/sms-01.png)
![Step](images/alisms/sms-02.png)

After the above steps, you will get a signature. Please write it to the control console parameter: `aliyun.sms.sign_name`

## Step 2: Add Template
![Step](images/alisms/sms-11.png)

After the above steps, you will get a template code. Please write it to the control console parameter: `aliyun.sms.sms_code_template_code`

Note: The signature needs to wait for 7 working days, and can only be sent successfully after the carrier reports successfully.

Note: The signature needs to wait for 7 working days, and can only be sent successfully after the carrier reports successfully.

Note: The signature needs to wait for 7 working days, and can only be sent successfully after the carrier reports successfully.

You can continue with the following operations after the report is successful.

## Step 3: Create SMS Account and Enable Permissions

Login to Alibaba Cloud console and enter the "Access Control" page: https://ram.console.aliyun.com/overview?activeTab=overview

![Step](images/alisms/sms-21.png)
![Step](images/alisms/sms-22.png)
![Step](images/alisms/sms-23.png)
![Step](images/alisms/sms-24.png)
![Step](images/alisms/sms-25.png)

After the above steps, you will get access_key_id and access_key_secret. Please write them to the control console parameters: `aliyun.sms.access_key_id`, `aliyun.sms.access_key_secret`
## Step 4: Enable Mobile Registration Function

1. Normally, after filling in all the above information, you will have this effect. If not, you may have missed some steps.

![Step](images/alisms/sms-31.png)

2. Enable non-admin users to register by setting the parameter `server.allow_user_register` to `true`

3. Enable mobile registration function by setting the parameter `server.enable_mobile_register` to `true`
![Step](images/alisms/sms-32.png)