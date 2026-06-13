package xiaozhi.modules.knowledge.dto.document;

import lombok.*;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.Serializable;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.validation.constraints.*;

/**
 * Aggregate DTOs for retrieval and metadata management.
 */
@Schema(description = "Aggregate DTOs for retrieval and metadata management")
@JsonIgnoreProperties(ignoreUnknown = true)
public class RetrievalDTO {

    /**
     * Aggregated document information.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Aggregated document information")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class DocAggVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Document name")
        @JsonProperty("doc_name")
        private String docName;

        @Schema(description = "Document ID")
        @JsonProperty("doc_id")
        private String docId;

        @Schema(description = "Count")
        private Integer count;
    }

    /**
     * Retrieval test request parameters.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Retrieval test request parameters")
    @JsonIgnoreProperties(ignoreUnknown = true)
    @JsonInclude(JsonInclude.Include.NON_NULL)
    public static class TestReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Knowledge base ID list", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("dataset_ids")
        @NotEmpty(message = "Knowledge base ID list cannot be empty")
        private List<String> datasetIds;

        @Schema(description = "Optional document ID list used to restrict retrieval scope")
        @JsonProperty("document_ids")
        private List<String> documentIds;

        @Schema(description = "Retrieval question", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "Retrieval question cannot be empty")
        private String question;

        @Schema(description = "Page number (default: 1)")
        private Integer page;

        @Schema(description = "Page size (default: 10)")
        @JsonProperty("page_size")
        private Integer pageSize;

        @Schema(description = "Similarity threshold (default: 0.2)")
        @JsonProperty("similarity_threshold")
        private Float similarityThreshold;

        @Schema(description = "Vector similarity weight (default: 0.3)")
        @JsonProperty("vector_similarity_weight")
        private Float vectorSimilarityWeight;

        @Schema(description = "Top-K chunks to return (default: 1024)")
        @JsonProperty("top_k")
        private Integer topK;

        @Schema(description = "Rerank model ID")
        @JsonProperty("rerank_id")
        private String rerankId;

        @Schema(description = "Whether keywords should be highlighted")
        private Boolean highlight;

        @Schema(description = "Whether keyword retrieval is enabled")
        private Boolean keyword;

        @Schema(description = "Optional cross-language translation list")
        @JsonProperty("cross_languages")
        private List<String> crossLanguages;

        @Schema(description = "Metadata filter conditions as a JSON object")
        @JsonProperty("metadata_condition")
        private Map<String, Object> metadataCondition;
    }

    /**
     * Retrieval hit details.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Retrieval hit details")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class HitVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Chunk ID", requiredMode = Schema.RequiredMode.REQUIRED)
        private String id;

        @Schema(description = "Chunk content", requiredMode = Schema.RequiredMode.REQUIRED)
        private String content;

        @Schema(description = "Owning document ID", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("document_id")
        private String documentId;

        @Schema(description = "Owning knowledge base ID")
        @JsonProperty("dataset_id")
        private String datasetId;

        @Schema(description = "Document name")
        @JsonProperty("document_name")
        private String documentName;

        @Schema(description = "Document keywords")
        @JsonProperty("document_keyword")
        private String documentKeyword;

        @Schema(description = "Overall similarity score", requiredMode = Schema.RequiredMode.REQUIRED)
        private Float similarity;

        @Schema(description = "Vector similarity score")
        @JsonProperty("vector_similarity")
        private Float vectorSimilarity;

        @Schema(description = "Keyword similarity score")
        @JsonProperty("term_similarity")
        private Float termSimilarity;

        @Schema(description = "Index position")
        private Integer index;

        @Schema(description = "Highlighted content")
        private String highlight;

        @Schema(description = "Important keyword list")
        @JsonProperty("important_keywords")
        private List<String> importantKeywords;

        @Schema(description = "Preset question list")
        private List<String> questions;

        @Schema(description = "Image ID")
        @JsonProperty("image_id")
        private String imageId;

        @Schema(description = "Position index. RAGFlow returns nested arrays such as [[start, end, filename]]")
        private Object positions;
    }

    /**
     * Knowledge base metadata summary.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Knowledge base metadata summary")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class MetaSummaryVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Total document count", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("total_doc_count")
        private Long totalDocCount;

        @Schema(description = "Total token count", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("total_token_count")
        private Long totalTokenCount;

        @Schema(description = "File type distribution keyed by suffix")
        @JsonProperty("file_type_distribution")
        private Map<String, Long> fileTypeDistribution;

        @Schema(description = "Document status distribution keyed by status code")
        @JsonProperty("status_distribution")
        private Map<String, Long> statusDistribution;

        @Schema(description = "Custom metadata statistics keyed by field name")
        @JsonProperty("custom_metadata")
        private Map<String, Object> customMetadata;
    }

    /**
     * Batch metadata update request parameters.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Batch metadata update request parameters")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class MetaBatchReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Selector used to specify which documents should be updated")
        private Selector selector;

        @Schema(description = "Metadata entries to add or update")
        private List<UpdateItem> updates;

        @Schema(description = "Metadata keys to delete")
        private List<DeleteItem> deletes;

        /**
         * Document selector.
         */
        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @Schema(description = "Metadata update selector")
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class Selector implements Serializable {
            private static final long serialVersionUID = 1L;

            @Schema(description = "Explicit document ID list")
            @JsonProperty("document_ids")
            private List<String> documentIds;

            @Schema(description = "Metadata condition match keyed by field name")
            @JsonProperty("metadata_condition")
            private Map<String, Object> metadataCondition;
        }

        /**
         * Update item.
         */
        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @Schema(description = "Metadata update item")
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class UpdateItem implements Serializable {
            private static final long serialVersionUID = 1L;

            @Schema(description = "Metadata key", requiredMode = Schema.RequiredMode.REQUIRED)
            private String key;

            @Schema(description = "Metadata value", requiredMode = Schema.RequiredMode.REQUIRED)
            private Object value;
        }

        /**
         * Delete item.
         */
        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @Schema(description = "Metadata delete item")
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class DeleteItem implements Serializable {
            private static final long serialVersionUID = 1L;

            @Schema(description = "Metadata key to delete", requiredMode = Schema.RequiredMode.REQUIRED)
            private String key;
        }
    }

    /**
     * Retrieval-test aggregate response.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Retrieval-test aggregate response")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ResultVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Retrieved chunk-hit list")
        private List<HitVO> chunks;

        @Schema(description = "Document distribution summary")
        @JsonProperty("doc_aggs")
        private List<DocAggVO> docAggs;

        @Schema(description = "Total hit count")
        private Long total;
    }
}
