package xiaozhi.modules.knowledge.dto.document;

import lombok.*;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.Serializable;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.validation.constraints.*;

/**
 * Chunk-management aggregate DTO.
 */
@Schema(description = "Chunk-management aggregate DTO")
@JsonIgnoreProperties(ignoreUnknown = true)
public class ChunkDTO {

    /**
     * Add-chunk request.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Add-chunk request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class AddReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Chunk content", requiredMode = Schema.RequiredMode.REQUIRED)
        @NotBlank(message = "Chunk content cannot be empty")
        private String content;

        @Schema(description = "Important keyword list")
        @JsonProperty("important_keywords")
        private List<String> importantKeywords;

        @Schema(description = "Preset question list")
        private List<String> questions;
    }

    /**
     * Update-chunk request.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Update-chunk request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class UpdateReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Updated chunk content")
        private String content;

        @Schema(description = "Updated keyword list that replaces the existing one")
        @JsonProperty("important_keywords")
        private List<String> importantKeywords;

        @Schema(description = "Availability flag (true enabled, false disabled)")
        private Boolean available;
    }

    /**
     * Chunk-list request.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Chunk-list request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ListReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Page number, default 1")
        private Integer page;

        @Schema(description = "Page size, default 30")
        @JsonProperty("page_size")
        private Integer pageSize;

        @Schema(description = "Search keywords for full-text retrieval")
        private String keywords;

        @Schema(description = "Exact chunk ID")
        private String id;
    }

    /**
     * Batch chunk-delete request.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Batch chunk-delete request")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class RemoveReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Chunk ID list", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("chunk_ids")
        @NotEmpty(message = "Chunk ID list cannot be empty")
        private List<String> chunkIds;
    }

    /**
     * Document chunk info view object.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Document chunk information")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class InfoVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Chunk ID, usually document_id plus an index", requiredMode = Schema.RequiredMode.REQUIRED)
        private String id;

        @Schema(description = "Chunk text content used for full-text retrieval", requiredMode = Schema.RequiredMode.REQUIRED)
        private String content;

        @Schema(description = "Owning document ID", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("document_id")
        private String documentId;

        @Schema(description = "Document name or keyword")
        @JsonProperty("docnm_kwd")
        private String docnmKwd;

        @Schema(description = "Important keyword list used for enhanced keyword retrieval")
        @JsonProperty("important_keywords")
        private List<String> importantKeywords;

        @Schema(description = "Preset question list used to enhance Q&A mode")
        private List<String> questions;

        @Schema(description = "Linked image ID")
        @JsonProperty("image_id")
        private String imageId;

        @Schema(description = "Owning knowledge-base ID")
        @JsonProperty("dataset_id")
        private String datasetId;

        @Schema(description = "Whether the chunk is available for retrieval")
        private Boolean available;

        @Schema(description = "Chunk positions in the source text, as nested arrays such as [[start, end, filename]]")
        private List<List<Object>> positions;

        @Schema(description = "Token ID list")
        @JsonProperty("token")
        private List<Integer> token;
    }

    /**
     * Chunk-list aggregate response.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Chunk-list aggregate response")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ListVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Chunk information list")
        private List<InfoVO> chunks;

        @Schema(description = "Linked document details")
        private DocumentDTO.InfoVO doc;

        @Schema(description = "Total record count")
        private Long total;
    }
}
