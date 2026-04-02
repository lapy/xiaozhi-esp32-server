package xiaozhi.modules.knowledge.dto.document;

import lombok.*;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.Serializable;
import java.util.List;
import java.util.Map;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.validation.constraints.*;

/**
 * Aggregate DTOs for document management.
 */
@Schema(description = "Aggregate DTOs for document management")
@JsonIgnoreProperties(ignoreUnknown = true)
public class DocumentDTO {

    /**
     * Upload document request parameters.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Upload document request parameters")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class UploadReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Knowledge base ID", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("dataset_id")
        @NotBlank(message = "Knowledge base ID cannot be empty")
        private String datasetId;

        @Schema(description = "File name. Overrides the original file name when provided")
        private String name;

        @Schema(description = "Chunking method")
        @JsonProperty("chunk_method")
        private DocumentDTO.InfoVO.ChunkMethod chunkMethod;

        @Schema(description = "Parser configuration")
        @JsonProperty("parser_config")
        private DocumentDTO.InfoVO.ParserConfig parserConfig;

        @Schema(description = "Virtual folder path (defaults to /)")
        @JsonProperty("parent_path")
        private String parentPath;

        @Schema(description = "Metadata fields")
        @JsonProperty("meta")
        private Map<String, Object> metaFields;

        @Schema(description = "File binary stream (supports PDF, DOCX, TXT, MD, and more)",
                requiredMode = Schema.RequiredMode.REQUIRED)
        @NotNull(message = "Upload file cannot be empty")
        private org.springframework.web.multipart.MultipartFile file;
    }

    /**
     * Update document request parameters.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Update document request parameters")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class UpdateReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "New document name. Must include the file extension and keep the original type")
        private String name;

        @Schema(description = "Enabled state. Disabled documents are excluded from retrieval")
        private Boolean enabled;

        @Schema(description = "New parsing method. Changing this resets the parsing state")
        @JsonProperty("chunk_method")
        private InfoVO.ChunkMethod chunkMethod;

        @Schema(description = "New parser configuration that should match chunk_method")
        @JsonProperty("parser_config")
        private InfoVO.ParserConfig parserConfig;
    }

    /**
     * List document request parameters.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "List document request parameters")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ListReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Page number (default: 1)")
        private Integer page;

        @Schema(description = "Page size (default: 30)")
        @JsonProperty("page_size")
        private Integer pageSize;

        @Schema(description = "Sort field (create_time, name, size; default: create_time)")
        private String orderby;

        @Schema(description = "Whether sorting is descending (default: true)")
        private Boolean desc;

        @Schema(description = "Exact filter: document ID")
        private String id;

        @Schema(description = "Exact filter: full document name including extension")
        private String name;

        @Schema(description = "Fuzzy search: document name keywords")
        private String keywords;

        @Schema(description = "Filter by file suffix list, for example ['pdf', 'docx']")
        private List<String> suffix;

        @Schema(description = "Filter by run-status list")
        private List<InfoVO.RunStatus> run;

        @Schema(description = "Filter by start creation time in milliseconds")
        @JsonProperty("create_time_from")
        private Long createTimeFrom;

        @Schema(description = "Filter by end creation time in milliseconds")
        @JsonProperty("create_time_to")
        private Long createTimeTo;
    }

    /**
     * Batch document operation request parameters, used for delete, parse, and similar actions.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Batch document operation request parameters")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class BatchIdReq implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Document ID list", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("ids") // Kept as ids for consistency, while remaining compatible with document_ids.
        @JsonAlias("document_ids")
        @NotEmpty(message = "Document ID list cannot be empty")
        private List<String> ids;
    }

    /**
     * Knowledge-base document information.
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    @Schema(description = "Knowledge-base document information")
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class InfoVO implements Serializable {
        private static final long serialVersionUID = 1L;

        @Schema(description = "Document ID", requiredMode = Schema.RequiredMode.REQUIRED)
        private String id;

        @Schema(description = "Document thumbnail URL, either Base64 or a link")
        private String thumbnail;

        @Schema(description = "Knowledge base ID", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("dataset_id")
        private String datasetId;

        @Schema(description = "Document parsing method that determines how chunks are created")
        @JsonProperty("chunk_method")
        private ChunkMethod chunkMethod;

        @Schema(description = "Related ETL pipeline ID when available")
        @JsonProperty("pipeline_id")
        private String pipelineId;

        @Schema(description = "Detailed document parser configuration")
        @JsonProperty("parser_config")
        private ParserConfig parserConfig;

        @Schema(description = "Source type such as local, s3, or url")
        @JsonProperty("source_type")
        private String sourceType;

        @Schema(description = "Document file type such as pdf, docx, or txt",
                requiredMode = Schema.RequiredMode.REQUIRED)
        private String type;

        @Schema(description = "Creator user ID")
        @JsonProperty("created_by")
        private String createdBy;

        @Schema(description = "Document name including extension", requiredMode = Schema.RequiredMode.REQUIRED)
        private String name;

        @Schema(description = "File storage path or location identifier")
        private String location;

        @Schema(description = "File size in bytes")
        private Long size;

        @Schema(description = "Total token count after parsing")
        @JsonProperty("token_count")
        private Long tokenCount;

        @Schema(description = "Total chunk count")
        @JsonProperty("chunk_count")
        private Long chunkCount;

        @Schema(description = "Parsing progress from 0.0 to 1.0")
        private Double progress;

        @Schema(description = "Current progress description or error message")
        @JsonProperty("progress_msg")
        private String progressMsg;

        @Schema(description = "Processing start time. RAGFlow returns this in RFC1123 format")
        @JsonProperty("process_begin_at")
        private String processBeginAt;

        @Schema(description = "Total processing duration in seconds")
        @JsonProperty("process_duration")
        private Double processDuration;

        @Schema(description = "Custom metadata key-value pairs")
        @JsonProperty("meta_fields")
        private Map<String, Object> metaFields;

        @Schema(description = "File suffix without the leading dot")
        private String suffix;

        @Schema(description = "Document parsing run status")
        private RunStatus run;

        @Schema(description = "Document availability status: 1 for enabled, 0 for disabled",
                requiredMode = Schema.RequiredMode.REQUIRED)
        private String status;

        @Schema(description = "Creation time in milliseconds", requiredMode = Schema.RequiredMode.REQUIRED)
        @JsonProperty("create_time")
        private Long createTime;

        @Schema(description = "Creation date. RAGFlow returns this in RFC1123 format")
        @JsonProperty("create_date")
        private String createDate;

        @Schema(description = "Last update time in milliseconds")
        @JsonProperty("update_time")
        private Long updateTime;

        @Schema(description = "Last update date. RAGFlow returns this in RFC1123 format")
        @JsonProperty("update_date")
        private String updateDate;

        /**
         * Chunking method enumeration.
         */
        public enum ChunkMethod {
            @Schema(description = "General mode for most plain-text or mixed documents")
            @JsonProperty("naive")
            NAIVE,
            @Schema(description = "Manual mode that allows users to edit chunks directly")
            @JsonProperty("manual")
            MANUAL,
            @Schema(description = "Q&A mode optimized for question-and-answer documents")
            @JsonProperty("qa")
            QA,
            @Schema(description = "Table mode optimized for Excel, CSV, and similar tabular data")
            @JsonProperty("table")
            TABLE,
            @Schema(description = "Paper mode optimized for academic paper layouts")
            @JsonProperty("paper")
            PAPER,
            @Schema(description = "Book mode optimized for chapter-based book structures")
            @JsonProperty("book")
            BOOK,
            @Schema(description = "Legal mode optimized for statutes and legal clauses")
            @JsonProperty("laws")
            LAWS,
            @Schema(description = "Presentation mode optimized for slide decks such as PPT")
            @JsonProperty("presentation")
            PRESENTATION,
            @Schema(description = "Picture mode that performs OCR and image description")
            @JsonProperty("picture")
            PICTURE,
            @Schema(description = "Single-chunk mode that keeps the whole document together")
            @JsonProperty("one")
            ONE,
            @Schema(description = "Knowledge graph mode that extracts entities and relationships")
            @JsonProperty("knowledge_graph")
            KNOWLEDGE_GRAPH,
            @Schema(description = "Email mode optimized for email-style content")
            @JsonProperty("email")
            EMAIL;
        }

        /**
         * Run status enumeration.
         */
        public enum RunStatus {
            @Schema(description = "Not started yet and waiting in the parsing queue")
            @JsonProperty("UNSTART")
            UNSTART,
            @Schema(description = "Currently parsing or indexing")
            @JsonProperty("RUNNING")
            RUNNING,
            @Schema(description = "Canceled manually by the user")
            @JsonProperty("CANCEL")
            CANCEL,
            @Schema(description = "Completed successfully")
            @JsonProperty("DONE")
            DONE,
            @Schema(description = "Failed during parsing")
            @JsonProperty("FAIL")
            FAIL;
        }

        /**
         * Layout recognition model enumeration.
         */
        public enum LayoutRecognize {
            @Schema(description = "Deep document understanding model for complex layouts")
            @JsonProperty("DeepDOC")
            DeepDOC,
            @Schema(description = "Simple rule-based model for plain text")
            @JsonProperty("Simple")
            Simple;
        }

        @Data
        @Builder
        @NoArgsConstructor
        @AllArgsConstructor
        @Schema(description = "Document parser configuration")
        @JsonIgnoreProperties(ignoreUnknown = true)
        public static class ParserConfig implements Serializable {
            private static final long serialVersionUID = 1L;

            @Schema(description = "Maximum tokens per chunk (recommended: 512, 1024, 2048)")
            @JsonProperty("chunk_token_num")
            private Integer chunkTokenNum;

            @Schema(description = "Chunk delimiter (supports escape sequences such as \\n)")
            private String delimiter;

            @Schema(description = "Layout recognition model (DeepDOC/Simple)")
            @JsonProperty("layout_recognize")
            private LayoutRecognize layoutRecognize;

            @Schema(description = "Whether Excel content should be converted to HTML tables")
            @JsonProperty("html4excel")
            private Boolean html4excel;

            @Schema(description = "Number of auto-generated keywords (0 disables extraction)")
            @JsonProperty("auto_keywords")
            private Integer autoKeywords;

            @Schema(description = "Number of auto-generated questions (0 disables generation)")
            @JsonProperty("auto_questions")
            private Integer autoQuestions;

            @Schema(description = "Number of auto-generated tags")
            @JsonProperty("topn_tags")
            private Integer topnTags;

            @Schema(description = "Advanced RAPTOR index configuration")
            private RaptorConfig raptor;

            @Schema(description = "GraphRAG knowledge graph configuration")
            @JsonProperty("graphrag")
            private GraphRagConfig graphRag;

            @Data
            @Builder
            @NoArgsConstructor
            @AllArgsConstructor
            @Schema(description = "RAPTOR recursive summary index configuration")
            @JsonIgnoreProperties(ignoreUnknown = true)
            public static class RaptorConfig implements Serializable {
                private static final long serialVersionUID = 1L;
                @Schema(description = "Whether RAPTOR indexing is enabled")
                @JsonProperty("use_raptor")
                private Boolean useRaptor;
            }

            @Data
            @Builder
            @NoArgsConstructor
            @AllArgsConstructor
            @Schema(description = "GraphRAG graph-enhanced retrieval configuration")
            @JsonIgnoreProperties(ignoreUnknown = true)
            public static class GraphRagConfig implements Serializable {
                private static final long serialVersionUID = 1L;
                @Schema(description = "Whether GraphRAG indexing is enabled")
                @JsonProperty("use_graphrag")
                private Boolean useGraphRag;
            }
        }
    }
}
