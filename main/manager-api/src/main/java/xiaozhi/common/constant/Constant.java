package xiaozhi.common.constant;

import lombok.Getter;

/**
 * Constants
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
public interface Constant {
    /**
     * Success
     */
    int SUCCESS = 1;
    /**
     * Failure
     */
    int FAIL = 0;
    /**
     * OK
     */
    String OK = "OK";
    /**
     * User identifier
     */
    String USER_KEY = "userId";
    /**
     * Menu root node identifier
     */
    Long MENU_ROOT = 0L;
    /**
     * Department root node identifier
     */
    Long DEPT_ROOT = 0L;
    /**
     * Data dictionary root node identifier
     */
    Long DICT_ROOT = 0L;
    /**
     * Ascending order
     */
    String ASC = "asc";
    /**
     * Descending order
     */
    String DESC = "desc";
    /**
     * Create time field name
     */
    String CREATE_DATE = "create_date";

    /**
     * Create time field name
     */
    String ID = "id";

    /**
     * Data permission filter
     */
    String SQL_FILTER = "sqlFilter";

    /**
     * Current page number
     */
    String PAGE = "page";
    /**
     * Records displayed per page
     */
    String LIMIT = "limit";
    /**
     * Sort field
     */
    String ORDER_FIELD = "orderField";
    /**
     * Sort order
     */
    String ORDER = "order";

    /**
     * Request header authorization identifier
     */
    String AUTHORIZATION = "Authorization";

    /**
     * Server secret key
     */
    String SERVER_SECRET = "server.secret";

    /**
     * WebSocket address
     */
    String SERVER_WEBSOCKET = "server.websocket";

    /**
     * MQTT gateway configuration
     */
    String SERVER_MQTT_GATEWAY = "server.mqtt_gateway";

    /**
     * OTA address
     */
    String SERVER_OTA = "server.ota";

    /**
     * Whether to allow user registration
     */
    String SERVER_ALLOW_USER_REGISTER = "server.allow_user_register";

    /**
     * Control panel address displayed when sending six-digit verification code
     */
    String SERVER_FRONTED_URL = "server.fronted_url";

    /**
     * Path separator
     */
    String FILE_EXTENSION_SEG = ".";

    /**
     * MCP access point path
     */
    String SERVER_MCP_ENDPOINT = "server.mcp_endpoint";

    /**
     * MCP access point path
     */
    String SERVER_VOICE_PRINT = "server.voice_print";

    /**
     * MQTT secret key
     */
    String SERVER_MQTT_SECRET = "server.mqtt_signature_key";

    /**
     * No memory
     */
    String MEMORY_NO_MEM = "Memory_nomem";

    enum SysBaseParam {
        /**
         * ICP filing number
         */
        BEIAN_ICP_NUM("server.beian_icp_num"),
        /**
         * GA filing number
         */
        BEIAN_GA_NUM("server.beian_ga_num"),
        /**
         * System name
         */
        SERVER_NAME("server.name");

        private String value;

        SysBaseParam(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    /**
     * System SMS
     */
    enum SysMSMParam {
        /**
         * Twilio Account SID
         */
        TWILIO_SMS_ACCOUNT_SID("twilio.sms.account_sid"),
        /**
         * Twilio Auth Token
         */
        TWILIO_SMS_AUTH_TOKEN("twilio.sms.auth_token"),
        /**
         * Twilio Phone Number (Sender)
         */
        TWILIO_SMS_PHONE_NUMBER("twilio.sms.phone_number"),
        /**
         * Twilio SMS Template Message
         */
        TWILIO_SMS_TEMPLATE_MESSAGE("twilio.sms.template_message"),
        /**
         * Maximum SMS send count per number
         */
        SERVER_SMS_MAX_SEND_COUNT("server.sms_max_send_count"),
        /**
         * Whether to enable mobile registration
         */
        SERVER_ENABLE_MOBILE_REGISTER("server.enable_mobile_register");

        private String value;

        SysMSMParam(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    /**
     * Data status
     */
    enum DataOperation {
        /**
         * Insert
         */
        INSERT("I"),
        /**
         * Updated
         */
        UPDATE("U"),
        /**
         * Deleted
         */
        DELETE("D");

        private String value;

        DataOperation(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    @Getter
    enum ChatHistoryConfEnum {
        IGNORE(0, "No record"),
        RECORD_TEXT(1, "Record text"),
        RECORD_TEXT_AUDIO(2, "Record both text and audio");

        private final int code;
        private final String name;

        ChatHistoryConfEnum(int code, String name) {
            this.code = code;
            this.name = name;
        }
    }

    /**
     * Version number
     */
    public static final String VERSION = "0.8.3";

    /**
     * Invalid firmware URL
     */
    String INVALID_FIRMWARE_URL = "http://xiaozhi.server.com:8003/xiaozhi/otaMag/download/NOT_ACTIVATED_FIRMWARE_THIS_IS_A_INVALID_URL";

    /**
     * Dictionary type
     */
    enum DictType {
        /**
         * Mobile area code
         */
        MOBILE_AREA("MOBILE_AREA");

        private String value;

        DictType(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }
}