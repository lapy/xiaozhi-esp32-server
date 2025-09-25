package xiaozhi.common.exception;

/**
 * Error codes, consisting of 5 digits: the first 2 digits are the module code, and the last 3 digits are the business code.
 * <p>
 * Example: 10001 (10 represents the System module, 001 represents the business code)
 * </p>
 * Copyright (c) Renren Open Source. All rights reserved.
 * Website: https://www.renren.io
 */
public interface ErrorCode {
    int INTERNAL_SERVER_ERROR = 500;
    int UNAUTHORIZED = 401;
    int FORBIDDEN = 403;

    int NOT_NULL = 10001;
    int DB_RECORD_EXISTS = 10002;
    int PARAMS_GET_ERROR = 10003;
    int ACCOUNT_PASSWORD_ERROR = 10004;
    int ACCOUNT_DISABLE = 10005;
    int IDENTIFIER_NOT_NULL = 10006;
    int CAPTCHA_ERROR = 10007;
    int PHONE_NOT_NULL = 10008;
    int PASSWORD_ERROR = 10009;

    int SUPERIOR_DEPT_ERROR = 10011;
    int SUPERIOR_MENU_ERROR = 10012;
    int DATA_SCOPE_PARAMS_ERROR = 10013;
    int DEPT_SUB_DELETE_ERROR = 10014;
    int DEPT_USER_DELETE_ERROR = 10015;

    int UPLOAD_FILE_EMPTY = 10019;
    int TOKEN_NOT_EMPTY = 10020;
    int TOKEN_INVALID = 10021;
    int ACCOUNT_LOCK = 10022;

    int OSS_UPLOAD_FILE_ERROR = 10024;

    int REDIS_ERROR = 10027;
    int JOB_ERROR = 10028;
    int INVALID_SYMBOL = 10029;
    int PASSWORD_LENGTH_ERROR = 10030;
    int PASSWORD_WEAK_ERROR = 10031;
    int DEL_MYSELF_ERROR = 10032;
    int DEVICE_CAPTCHA_ERROR = 10033;

    // Parameter validation related error codes
    int PARAM_VALUE_NULL = 10034;
    int PARAM_TYPE_NULL = 10035;
    int PARAM_TYPE_INVALID = 10036;
    int PARAM_NUMBER_INVALID = 10037;
    int PARAM_BOOLEAN_INVALID = 10038;
    int PARAM_ARRAY_INVALID = 10039;
    int PARAM_JSON_INVALID = 10040;

    int OTA_DEVICE_NOT_FOUND = 10041;
    int OTA_DEVICE_NEED_BIND = 10042;
    
    // Newly added error codes
    int DELETE_DATA_FAILED = 10043;
    int USER_NOT_LOGIN = 10044;
    int WEB_SOCKET_CONNECT_FAILED = 10045;
    int VOICE_PRINT_SAVE_ERROR = 10046;
    int TODAY_SMS_LIMIT_REACHED = 10047;
    int OLD_PASSWORD_ERROR = 10048;
    int INVALID_LLM_TYPE = 10049;
    int TOKEN_GENERATE_ERROR = 10050;
    int RESOURCE_NOT_FOUND = 10051;
    
    // Newly added error codes
    int DEFAULT_AGENT_NOT_FOUND = 10052;
    int AGENT_NOT_FOUND = 10053;
    int VOICEPRINT_API_NOT_CONFIGURED = 10054;
    int SMS_SEND_FAILED = 10055;
    int SMS_CONNECTION_FAILED = 10056;
    int AGENT_VOICEPRINT_CREATE_FAILED = 10057;
    int AGENT_VOICEPRINT_UPDATE_FAILED = 10058;
    int AGENT_VOICEPRINT_DELETE_FAILED = 10059;
    int SMS_SEND_TOO_FREQUENTLY = 10060;
    int ACTIVATION_CODE_EMPTY = 10061;
    int ACTIVATION_CODE_ERROR = 10062;
    int DEVICE_ALREADY_ACTIVATED = 10063;
    // Default model deletion error
    int DEFAULT_MODEL_DELETE_ERROR = 10064;
    // Device related error codes
    int MAC_ADDRESS_ALREADY_EXISTS = 10090; // MAC address already exists
    // Model related error codes
    int MODEL_PROVIDER_NOT_EXIST = 10091; // Provider does not exist
    int LLM_NOT_EXIST = 10092; // The specified LLM does not exist
    int MODEL_REFERENCED_BY_AGENT = 10093; // This model configuration is referenced by an agent and cannot be deleted
    int LLM_REFERENCED_BY_INTENT = 10094; // This LLM is referenced by the intent configuration and cannot be deleted
    
    // Login related error codes
    int ADD_DATA_FAILED = 10065; // Failed to add data
    int UPDATE_DATA_FAILED = 10066; // Failed to update data
    int SMS_CAPTCHA_ERROR = 10067; // SMS verification code error
    int MOBILE_REGISTER_DISABLED = 10068; // Mobile registration is disabled
    int USERNAME_NOT_PHONE = 10069; // Username is not a phone number
    int PHONE_ALREADY_REGISTERED = 10070; // Phone number already registered
    int PHONE_NOT_REGISTERED = 10071; // Phone number not registered
    int USER_REGISTER_DISABLED = 10072; // User registration is not allowed
    int RETRIEVE_PASSWORD_DISABLED = 10073; // Password recovery is disabled
    int PHONE_FORMAT_ERROR = 10074; // Invalid phone number format
    int SMS_CODE_ERROR = 10075; // Incorrect SMS code
    
    // Dictionary type related error codes
    int DICT_TYPE_NOT_EXIST = 10076; // Dictionary type does not exist
    int DICT_TYPE_DUPLICATE = 10077; // Dictionary type code is duplicated
    
    // Resource processing related error codes
    int RESOURCE_READ_ERROR = 10078; // Failed to read resource
    
    // Agent related error codes
    int LLM_INTENT_PARAMS_MISMATCH = 10079; // LLM and Intent recognition selection parameters mismatch
    
    // Voiceprint related error codes
    int VOICEPRINT_ALREADY_REGISTERED = 10080; // This voiceprint is already registered
    int VOICEPRINT_DELETE_ERROR = 10081; // Error deleting voiceprint
    int VOICEPRINT_UPDATE_NOT_ALLOWED = 10082; // Voiceprint modification not allowed; voice already registered
    int VOICEPRINT_UPDATE_ADMIN_ERROR = 10083; // Error updating voiceprint; please contact administrator
    int VOICEPRINT_API_URI_ERROR = 10084; // Voiceprint API URL error
    int VOICEPRINT_AUDIO_NOT_BELONG_AGENT = 10085; // Audio data does not belong to the agent
    int VOICEPRINT_AUDIO_EMPTY = 10086; // Audio data is empty
    int VOICEPRINT_REGISTER_REQUEST_ERROR = 10087; // Voiceprint save request failed
    int VOICEPRINT_REGISTER_PROCESS_ERROR = 10088; // Voiceprint save process failed
    int VOICEPRINT_UNREGISTER_REQUEST_ERROR = 10089; // Voiceprint unregister request failed
    int VOICEPRINT_UNREGISTER_PROCESS_ERROR = 10090; // Voiceprint unregister process failed
    int VOICEPRINT_IDENTIFY_REQUEST_ERROR = 10091; // Voiceprint identification request failed
    
    // Server-side management related error codes
    int INVALID_SERVER_ACTION = 10095; // Invalid server action
    int SERVER_WEBSOCKET_NOT_CONFIGURED = 10096; // Server WebSocket address is not configured
    int TARGET_WEBSOCKET_NOT_EXIST = 10097; // Target WebSocket address does not exist
    
    // Parameter validation related error codes
    int WEBSOCKET_URLS_EMPTY = 10098; // WebSocket address list cannot be empty
    int WEBSOCKET_URL_LOCALHOST = 10099; // WebSocket address cannot use localhost or 127.0.0.1
    int WEBSOCKET_URL_FORMAT_ERROR = 10100; // Invalid WebSocket address format
    int WEBSOCKET_CONNECTION_FAILED = 10101; // WebSocket connection test failed
    int OTA_URL_EMPTY = 10102; // OTA address cannot be empty
    int OTA_URL_LOCALHOST = 10103; // OTA address cannot use localhost or 127.0.0.1
    int OTA_URL_PROTOCOL_ERROR = 10104; // OTA address must start with http or https
    int OTA_URL_FORMAT_ERROR = 10105; // OTA address must end with /ota/
    int OTA_INTERFACE_ACCESS_FAILED = 10106; // OTA interface access failed
    int OTA_INTERFACE_FORMAT_ERROR = 10107; // OTA interface returned invalid format
    int OTA_INTERFACE_VALIDATION_FAILED = 10108; // OTA interface validation failed
    int MCP_URL_EMPTY = 10109; // MCP address cannot be empty
    int MCP_URL_LOCALHOST = 10110; // MCP address cannot use localhost or 127.0.0.1
    int MCP_URL_INVALID = 10111; // Invalid MCP address
    int MCP_INTERFACE_ACCESS_FAILED = 10112; // MCP interface access failed
    int MCP_INTERFACE_FORMAT_ERROR = 10113; // MCP interface returned invalid format
    int MCP_INTERFACE_VALIDATION_FAILED = 10114; // MCP interface validation failed
    int VOICEPRINT_URL_EMPTY = 10115; // Voiceprint API address cannot be empty
    int VOICEPRINT_URL_LOCALHOST = 10116; // Voiceprint API address cannot use localhost or 127.0.0.1
    int VOICEPRINT_URL_INVALID = 10117; // Invalid voiceprint API address
    int VOICEPRINT_URL_PROTOCOL_ERROR = 10118; // Voiceprint API address must start with http or https
    int VOICEPRINT_INTERFACE_ACCESS_FAILED = 10119; // Voiceprint API access failed
    int VOICEPRINT_INTERFACE_FORMAT_ERROR = 10120; // Voiceprint API returned invalid format
    int VOICEPRINT_INTERFACE_VALIDATION_FAILED = 10121; // Voiceprint API validation failed
    int MQTT_SECRET_EMPTY = 10122; // MQTT secret cannot be empty
    int MQTT_SECRET_LENGTH_INSECURE = 10123; // MQTT secret length is insecure
    int MQTT_SECRET_CHARACTER_INSECURE = 10124; // MQTT secret must include both uppercase and lowercase letters
    int MQTT_SECRET_WEAK_PASSWORD = 10125; // MQTT secret contains weak password
    
    // Dictionary related error codes
    int DICT_LABEL_DUPLICATE = 10128; // Dictionary label is duplicated
    // Model related error codes
    int MODEL_TYPE_PROVIDE_CODE_NOT_NULL = 10129; // modelType and provideCode cannot be null
}
