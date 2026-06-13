package xiaozhi.modules.device.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Data
@Schema(description = "Device OTA version-check response, including activation requirements")
public class DeviceReportRespDTO {
    @Schema(description = "Server time")
    private ServerTime server_time;

    @Schema(description = "Activation data")
    private Activation activation;

    @Schema(description = "Error message")
    private String error;

    @Schema(description = "Firmware information")
    private Firmware firmware;

    @Schema(description = "WebSocket configuration")
    private Websocket websocket;

    @Schema(description = "MQTT gateway configuration")
    private MQTT mqtt;

    @Getter
    @Setter
    public static class Firmware {
        @Schema(description = "Version")
        private String version;
        @Schema(description = "Download URL")
        private String url;
    }

    public static DeviceReportRespDTO createError(String message) {
        DeviceReportRespDTO resp = new DeviceReportRespDTO();
        resp.setError(message);
        return resp;
    }

    @Setter
    @Getter
    public static class Activation {
        @Schema(description = "Activation code")
        private String code;

        @Schema(description = "Activation message, usually the activation URL")
        private String message;

        @Schema(description = "Challenge code")
        private String challenge;
    }

    @Getter
    @Setter
    public static class ServerTime {
        @Schema(description = "Timestamp")
        private Long timestamp;

        @Schema(description = "Time zone")
        private String timeZone;

        @Schema(description = "Time-zone offset in minutes")
        private Integer timezone_offset;
    }

    @Getter
    @Setter
    public static class Websocket {
        @Schema(description = "WebSocket server URL")
        private String url;
        @Schema(description = "WebSocket authentication token")
        private String token;
    }

    @Getter
    @Setter
    public static class MQTT {
        @Schema(description = "MQTT endpoint URL")
        private String endpoint;
        @Schema(description = "Unique MQTT client identifier")
        private String client_id;
        @Schema(description = "MQTT authentication username")
        private String username;
        @Schema(description = "MQTT authentication password")
        private String password;
        @Schema(description = "Topic published by ESP32")
        private String publish_topic;
        @Schema(description = "Topic subscribed to by ESP32")
        private String subscribe_topic;
    }
}
