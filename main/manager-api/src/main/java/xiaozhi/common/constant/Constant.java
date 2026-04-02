package xiaozhi.common.constant;

import lombok.Getter;

/**
 * Shared constants.
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
public interface Constant {
    /**
     * Success.
     */
    int SUCCESS = 1;
    /**
     * Failure.
     */
    int FAIL = 0;
    /**
     * OK
     */
    String OK = "OK";
    /**
     * User identifier.
     */
    String USER_KEY = "userId";
    /**
     * Menu root-node identifier.
     */
    Long MENU_ROOT = 0L;
    /**
     * Department root-node identifier.
     */
    Long DEPT_ROOT = 0L;
    /**
     * Data-dictionary root-node identifier.
     */
    Long DICT_ROOT = 0L;
    /**
     * Ascending sort.
     */
    String ASC = "asc";
    /**
     * Descending sort.
     */
    String DESC = "desc";
    /**
     * Create-time field name.
     */
    String CREATE_DATE = "create_date";

    /**
     * Primary ID field name.
     */
    String ID = "id";

    /**
     * Data-permission filter.
     */
    String SQL_FILTER = "sqlFilter";

    /**
     * Current page number.
     */
    String PAGE = "page";
    /**
     * Page size.
     */
    String LIMIT = "limit";
    /**
     * Sort field.
     */
    String ORDER_FIELD = "orderField";
    /**
     * Sort direction.
     */
    String ORDER = "order";

    /**
     * Authorization header name.
     */
    String AUTHORIZATION = "Authorization";

    /**
     * Server secret.
     */
    String SERVER_SECRET = "server.secret";

    /**
     * SM2 public key.
     */
    String SM2_PUBLIC_KEY = "server.public_key";

    /**
     * SM2 private key.
     */
    String SM2_PRIVATE_KEY = "server.private_key";

    /**
     * WebSocket URL.
     */
    String SERVER_WEBSOCKET = "server.websocket";

    /**
     * MQTT gateway configuration.
     */
    String SERVER_MQTT_GATEWAY = "server.mqtt_gateway";

    /**
     * OTA URL.
     */
    String SERVER_OTA = "server.ota";

    /**
     * Whether user registration is allowed.
     */
    String SERVER_ALLOW_USER_REGISTER = "server.allow_user_register";

    /**
     * Control-panel URL shown with the six-digit verification code.
     */
    String SERVER_FRONTED_URL = "server.fronted_url";

    /**
     * Path separator.
     */
    String FILE_EXTENSION_SEG = ".";

    /**
     * MCP endpoint path.
     */
    String SERVER_MCP_ENDPOINT = "server.mcp_endpoint";

    /**
     * Voiceprint endpoint path.
     */
    String SERVER_VOICE_PRINT = "server.voice_print";

    /**
     * MQTT signature key.
     */
    String SERVER_MQTT_SECRET = "server.mqtt_signature_key";

    /**
     * WebSocket auth toggle.
     */
    String SERVER_AUTH_ENABLED = "server.auth.enabled";

    /**
     * No memory.
     */
    String MEMORY_NO_MEM = "Memory_nomem";

    /**
     * Report chat history only, without memory summaries.
     */
    String MEMORY_MEM_REPORT_ONLY = "Memory_mem_report_only";

    /**
     * RAG config type.
     */
    String RAG_CONFIG_TYPE = "RAG";

    enum SysBaseParam {
        /**
         * ICP registration number.
         */
        BEIAN_ICP_NUM("server.beian_icp_num"),
        /**
         * GA registration number.
         */
        BEIAN_GA_NUM("server.beian_ga_num"),
        /**
         * System name.
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
     * Training status.
     */
    enum TrainStatus {
        /**
         * Not trained.
         */
        NOT_TRAINED(0),
        /**
         * Training in progress.
         */
        TRAINING(1),
        /**
         * Trained.
         */
        TRAINED(2),
        /**
         * Training failed.
         */
        TRAIN_FAILED(3);

        private final int code;

        TrainStatus(int code) {
            this.code = code;
        }

        public int getCode() {
            return code;
        }
    }

    /**
     * System SMS parameters
     */
    enum SysMSMParam {
        /**
         * Twilio account SID
         */
        TWILIO_SMS_ACCOUNT_SID("twilio.sms.account_sid"),
        /**
         * Twilio auth token
         */
        TWILIO_SMS_AUTH_TOKEN("twilio.sms.auth_token"),
        /**
         * Twilio phone number (from)
         */
        TWILIO_SMS_PHONE_NUMBER("twilio.sms.phone_number"),
        /**
         * Twilio SMS template message
         */
        TWILIO_SMS_TEMPLATE_MESSAGE("twilio.sms.template_message"),
        /**
         * Max SMS per phone number per day
         */
        SERVER_SMS_MAX_SEND_COUNT("server.sms_max_send_count"),
        /**
         * Enable mobile registration
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
     * Data operation state.
     */
    enum DataOperation {
        /**
         * Inserted.
         */
        INSERT("I"),
        /**
         * Updated.
         */
        UPDATE("U"),
        /**
         * Deleted.
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
        IGNORE(0, "Do not record"),
        RECORD_TEXT(1, "Record text"),
        RECORD_TEXT_AUDIO(2, "Record text and audio");

        private final int code;
        private final String name;

        ChatHistoryConfEnum(int code, String name) {
            this.code = code;
            this.name = name;
        }
    }

    /**
     * Version number.
     */
    public static final String VERSION = "0.9.2";

    /**
     * Invalid firmware URL.
     */
    String INVALID_FIRMWARE_URL = "http://xiaozhi.server.com:8002/xiaozhi/otaMag/download/NOT_ACTIVATED_FIRMWARE_THIS_IS_A_INVALID_URL";

    /**
     * Dictionary types.
     */
    enum DictType {
        /**
         * Phone country code.
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
