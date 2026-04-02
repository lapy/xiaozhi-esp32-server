package xiaozhi.modules.knowledge.dto.bot;

import lombok.*;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.Serializable;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.*;

@Schema(description = "External bot aggregate DTO")
public class BotDTO {

    // ========== 1. SearchBot ==========

    // Maps to /api/v1/searchbots/ask
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "SearchBot ask request")
    public static class SearchAskReq implements Serializable {
        @Schema(description = "User question", requiredMode = Schema.RequiredMode.REQUIRED, example = "What is RAG?")
        @NotBlank(message = "Question cannot be empty")
        @JsonProperty("question")
        private String question;

        @Schema(description = "Whether to return references", defaultValue = "false")
        @JsonProperty("quote")
        @Builder.Default
        private Boolean quote = false;

        @Schema(description = "Whether to stream the response", defaultValue = "true")
        @JsonProperty("stream")
        @Builder.Default
        private Boolean stream = true;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "SearchBot ask response")
    public static class SearchAskVO implements Serializable {
        @Schema(description = "Answer content")
        @JsonProperty("answer")
        private String answer;

        @Schema(description = "Reference sources, usually aligned with RetrievalDTO.HitVO")
        @JsonProperty("reference")
        private Map<String, Object> reference;
    }

    // Maps to /api/v1/searchbots/related_questions
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Related-question request")
    public static class RelatedQuestionReq implements Serializable {
        @Schema(description = "User question", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "Question cannot be empty")
        @JsonProperty("question")
        private String question;
    }

    // Maps to /api/v1/searchbots/mindmap
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Mind-map request")
    public static class MindMapReq implements Serializable {
        @Schema(description = "User question", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "Question cannot be empty")
        @JsonProperty("question")
        private String question;
    }

    // ========== 2. AgentBot ==========

    // Maps to /api/v1/agentbots/{id}/inputs
    @Data
    @Builder
    @AllArgsConstructor
    @Schema(description = "AgentBot input-definition request")
    public static class AgentInputsReq implements Serializable {
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "AgentBot input-definition response")
    public static class AgentInputsVO implements Serializable {
        @Schema(description = "Form variable definition list")
        @JsonProperty("variables")
        private List<Map<String, Object>> variables;
    }

    // Maps to /api/v1/agentbots/{id}/completions
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "AgentBot conversation request")
    public static class AgentCompletionReq implements Serializable {
        @Schema(description = "Input parameter values")
        @JsonProperty("inputs")
        private Map<String, Object> inputs;

        @Schema(description = "User query", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "Query content cannot be empty")
        @JsonProperty("question")
        private String question;

        @Schema(description = "Whether to stream the response", defaultValue = "true")
        @JsonProperty("stream")
        @Builder.Default
        private Boolean stream = true;

        @Schema(description = "Session ID")
        @JsonProperty("session_id")
        private String sessionId;
    }
}
