package xiaozhi.modules.knowledge.dto.dataset;

import lombok.*;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.Serializable;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.validation.constraints.*;

/**
 * Aggregate DTOs for knowledge base management.
 * <p>
 * Container for request/response types used by the knowledge base module.
 * </p>
 */
@Schema(description = "Aggregate DTOs for knowledge base management")
@JsonIgnoreProperties(ignoreUnknown = true)
public class DatasetDTO {

    // ========== Shared nested types ==========

    /**
     * Parser configuration.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Parser configuration")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ParserConfig implements Serializable {

        @Schema(description = "Chunk token count", example = "128")
        @JsonProperty("chunk_token_num")
        private Integer chunkTokenNum;

        @Schema(description = "Delimiter", example = "\\n!?;.;!?")
        private String delimiter;

        @Schema(description = "Layout recognition model: DeepDOC / Simple", example = "DeepDOC")
        @JsonProperty("layout_recognize")
        private String layoutRecognize;

        @Schema(description = "Whether to convert Excel files to HTML", example = "false")
        private Boolean html4excel;

        @Schema(description = "Auto-generated keyword count (0 disables it)", example = "0")
        @JsonProperty("auto_keywords")
        private Integer autoKeywords;

        @Schema(description = "Auto-generated question count (0 disables it)", example = "0")
        @JsonProperty("auto_questions")
        private Integer autoQuestions;
    }

    // ========== Requests ==========

    /**
     * Create knowledge base request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Create knowledge base request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class CreateReq implements Serializable {

        @NotBlank(message = "Knowledge base name cannot be empty")
        @Schema(description = "Knowledge base name", requiredMode = Schema.RequiredMode.REQUIRED, example = "my_dataset")
        private String name;

        @Schema(description = "Knowledge base avatar in Base64", example = "")
        private String avatar;

        @Schema(description = "Knowledge base description", example = "Used to store product documents")
        private String description;

        @Schema(description = "Embedding model name", example = "text-embedding-3-large")
        @JsonProperty("embedding_model")
        private String embeddingModel;

        @Schema(description = "Permission setting: me / team", example = "me")
        private String permission;

        @Schema(description = "Chunking method: naive / manual / qa / table / paper / book / laws / presentation / picture / one / knowledge_graph / email",
                example = "naive")
        @JsonProperty("chunk_method")
        private String chunkMethod;

        @Schema(description = "Parser configuration")
        @JsonProperty("parser_config")
        private ParserConfig parserConfig;
    }

    /**
     * Update knowledge base request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Update knowledge base request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class UpdateReq implements Serializable {

        @Schema(description = "Knowledge base name", example = "updated_dataset")
        private String name;

        @Schema(description = "Knowledge base avatar in Base64", example = "")
        private String avatar;

        @Schema(description = "Knowledge base description", example = "Updated description")
        private String description;

        @Schema(description = "Permission setting: me / team", example = "team")
        private String permission;

        @Schema(description = "Embedding model name", example = "text-embedding-3-large")
        @JsonProperty("embedding_model")
        private String embeddingModel;

        @Schema(description = "Chunking method: naive / manual / qa / table / paper / book / laws / presentation / picture / one / knowledge_graph / email",
                example = "naive")
        @JsonProperty("chunk_method")
        private String chunkMethod;

        @Schema(description = "Parser configuration")
        @JsonProperty("parser_config")
        private ParserConfig parserConfig;

        @JsonInclude(JsonInclude.Include.NON_NULL)
        @Schema(description = "PageRank weight (0-100)", example = "50")
        private Integer pagerank;
    }

    /**
     * List knowledge bases request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "List knowledge bases request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ListReq implements Serializable {

        @Schema(description = "Page number, starting from 1", example = "1")
        private Integer page;

        @Schema(description = "Page size", example = "30")
        @JsonProperty("page_size")
        private Integer pageSize;

        @Schema(description = "Sort field: create_time / update_time", example = "create_time")
        private String orderby;

        @Schema(description = "Whether sorting is descending", example = "true")
        private Boolean desc;

        @Schema(description = "Filter by name using fuzzy matching", example = "my_dataset")
        private String name;

        @Schema(description = "Filter by knowledge base ID", example = "abc123")
        private String id;
    }

    /**
     * Bulk delete knowledge bases request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Bulk delete knowledge bases request")
    public static class BatchIdReq implements Serializable {

        @NotNull(message = "Knowledge base ID list cannot be empty")
        @Size(min = 1, message = "At least one knowledge base ID is required")
        @Schema(description = "Knowledge base ID list", requiredMode = Schema.RequiredMode.REQUIRED,
                example = "[\"id1\", \"id2\"]")
        private List<String> ids;
    }

    /**
     * Run GraphRAG request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Run GraphRAG request")
    public static class RunGraphRagReq implements Serializable {

        @Schema(description = "Entity type list", example = "[\"person\", \"organization\"]")
        @JsonProperty("entity_types")
        private List<String> entityTypes;

        @Schema(description = "Build method: light / fast / full", example = "light")
        private String method;
    }

    /**
     * Run RAPTOR request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Run RAPTOR request")
    public static class RunRaptorReq implements Serializable {

        @Schema(description = "Maximum cluster count", example = "64")
        @JsonProperty("max_cluster")
        private Integer maxCluster;

        @Schema(description = "Custom prompt", example = "Please summarize the following content...")
        private String prompt;
    }

    /**
     * Async task ID response.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Async task ID response")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class TaskIdVO implements Serializable {

        @Schema(description = "GraphRAG task ID", example = "task_uuid_12345678")
        @JsonProperty("graphrag_task_id")
        private String graphragTaskId;

        @Schema(description = "RAPTOR task ID", example = "task_uuid_87654321")
        @JsonProperty("raptor_task_id")
        private String raptorTaskId;
    }

    // ========== Responses ==========

    /**
     * Knowledge base details.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Knowledge base details")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class InfoVO implements Serializable {

        @Schema(description = "Knowledge base ID", example = "abc123")
        private String id;

        @Schema(description = "Knowledge base name", example = "my_dataset")
        private String name;

        @Schema(description = "Knowledge base avatar in Base64", example = "")
        private String avatar;

        @Schema(description = "Tenant ID", example = "tenant_001")
        @JsonProperty("tenant_id")
        private String tenantId;

        @Schema(description = "Knowledge base description", example = "Used to store product documents")
        private String description;

        @Schema(description = "Embedding model name", example = "text-embedding-3-large")
        @JsonProperty("embedding_model")
        private String embeddingModel;

        @Schema(description = "Permission setting: me / team", example = "me")
        private String permission;

        @Schema(description = "Chunking method", example = "naive")
        @JsonProperty("chunk_method")
        private String chunkMethod;

        @Schema(description = "Parser configuration")
        @JsonProperty("parser_config")
        private ParserConfig parserConfig;

        @Schema(description = "Total chunk count", example = "1024")
        @JsonProperty("chunk_count")
        private Long chunkCount;

        @Schema(description = "Total document count", example = "50")
        @JsonProperty("document_count")
        private Long documentCount;

        @Schema(description = "Creation time as a timestamp", example = "1700000000000")
        @JsonProperty("create_time")
        private Long createTime;

        @Schema(description = "Update time as a timestamp", example = "1700000001000")
        @JsonProperty("update_time")
        private Long updateTime;

        @Schema(description = "Total token count", example = "102400")
        @JsonProperty("token_num")
        private Long tokenNum;

        @Schema(description = "Creation date in yyyy-MM-dd HH:mm:ss format")
        @JsonProperty("create_date")
        private String createDate;

        @Schema(description = "Last update date in yyyy-MM-dd HH:mm:ss format")
        @JsonProperty("update_date")
        private String updateDate;
    }

    /**
     * Batch operation response.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Batch operation response")
    public static class BatchOperationVO implements Serializable {

        @Schema(description = "Successful operation count", example = "5")
        @JsonProperty("success_count")
        private Integer successCount;

        @Schema(description = "Error list")
        private List<Object> errors;
    }

    // ========== Knowledge-graph types ==========

    /**
     * Knowledge-graph data response mapped from the knowledge_graph endpoint.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Knowledge-graph data response")
    public static class GraphVO implements Serializable {

        @Schema(description = "Graph node list")
        private List<Node> nodes;

        @Schema(description = "Graph edge list")
        private List<Edge> edges;

        @Schema(description = "Mind-map data")
        @JsonProperty("mind_map")
        private Map<String, Object> mindMap;

        /**
         * Graph node.
         */
        @Data
        @NoArgsConstructor
        @AllArgsConstructor
        @Builder
        @Schema(description = "Graph node")
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class Node implements Serializable {

            @Schema(description = "Node ID", example = "node_001")
            private String id;

            @Schema(description = "Node label", example = "Product")
            private String label;

            @Schema(description = "PageRank value", example = "0.85")
            private Double pagerank;

            @Schema(description = "Node color", example = "#FF5733")
            private String color;

            @Schema(description = "Node image URL", example = "https://example.com/icon.png")
            private String img;
        }

        /**
         * Graph edge.
         */
        @Data
        @NoArgsConstructor
        @AllArgsConstructor
        @Builder
        @Schema(description = "Graph edge")
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class Edge implements Serializable {

            @Schema(description = "Source node ID", example = "node_001")
            private String source;

            @Schema(description = "Target node ID", example = "node_002")
            private String target;

            @Schema(description = "Edge weight", example = "0.75")
            private Double weight;

            @Schema(description = "Edge label describing the relationship", example = "belongs_to")
            private String label;
        }
    }

    // ========== Async task tracing (GraphRAG/RAPTOR) ==========

    /**
     * Async task-trace response mapped from task-progress endpoints.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Async task-trace response")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class TaskTraceVO implements Serializable {

        @Schema(description = "Task ID", example = "task_001")
        private String id;

        @Schema(description = "Document ID", example = "doc_001")
        @JsonProperty("doc_id")
        private String docId;

        @Schema(description = "Starting page number", example = "1")
        @JsonProperty("from_page")
        private Integer fromPage;

        @Schema(description = "Ending page number", example = "10")
        @JsonProperty("to_page")
        private Integer toPage;

        @Schema(description = "Progress percentage from 0.0 to 1.0", example = "0.75")
        private Double progress;

        @Schema(description = "Progress message", example = "Processing page 5...")
        @JsonProperty("progress_msg")
        private String progressMsg;

        @Schema(description = "Creation time as a timestamp", example = "1700000000000")
        @JsonProperty("create_time")
        private Long createTime;

        @Schema(description = "Update time as a timestamp", example = "1700000001000")
        @JsonProperty("update_time")
        private Long updateTime;
    }
}
