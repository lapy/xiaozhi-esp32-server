package xiaozhi.modules.knowledge.dto;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "Knowledge-base DTO")
public class KnowledgeBaseDTO implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    @Schema(description = "Unique ID")
    private String id;

    @Schema(description = "Knowledge-base ID")
    private String datasetId;

    @Schema(description = "RAG model configuration ID")
    private String ragModelId;

    @Schema(description = "Knowledge-base name")
    private String name;

    @Schema(description = "Knowledge-base avatar in Base64")
    private String avatar;

    @Schema(description = "Knowledge-base description")
    private String description;

    @Schema(description = "Embedding model name")
    private String embeddingModel;

    @Schema(description = "Permission setting, for example me or team")
    private String permission;

    @Schema(description = "Chunking method")
    private String chunkMethod;

    @Schema(description = "Parser configuration as JSON")
    private String parserConfig;

    @Schema(description = "Total chunk count")
    private Long chunkCount;

    @Schema(description = "Total token count")
    private Long tokenNum;

    @Schema(description = "Status flag (0 disabled, 1 enabled)")
    private Integer status;

    @Schema(description = "Created by")
    private Long creator;

    @Schema(description = "Created at")
    private Date createdAt;

    @Schema(description = "Updated by")
    private Long updater;

    @Schema(description = "Updated at")
    private Date updatedAt;

    @Schema(description = "Document count")
    private Integer documentCount;
}
