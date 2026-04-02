package xiaozhi.modules.knowledge.dto.chat;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonProperty;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Chat completion request DTO in an OpenAI-compatible format.
 */
@Data
@Schema(description = "Chat completion request")
public class ChatCompletionRequest implements Serializable {

    @Schema(description = "Model identifier, usually agent_id or bot_id", requiredMode = Schema.RequiredMode.REQUIRED)
    @JsonProperty("model")
    private String model;

    @Schema(description = "Conversation message list", requiredMode = Schema.RequiredMode.REQUIRED)
    @JsonProperty("messages")
    private List<Message> messages;

    @Schema(description = "Whether to stream the response", defaultValue = "false")
    @JsonProperty("stream")
    private Boolean stream = false;

    @Schema(description = "Temperature from 0 to 1", defaultValue = "0.7")
    @JsonProperty("temperature")
    private Double temperature;

    @Schema(description = "Optional session ID used to continue a conversation")
    @JsonProperty("session_id")
    private String sessionId;

    @Schema(description = "Additional optional RAGFlow-specific parameters")
    private Map<String, Object> extra;

    @Data
    public static class Message implements Serializable {
        @Schema(description = "Role, such as system, user, or assistant", requiredMode = Schema.RequiredMode.REQUIRED)
        private String role;

        @Schema(description = "Message content", requiredMode = Schema.RequiredMode.REQUIRED)
        private String content;
    }
}
