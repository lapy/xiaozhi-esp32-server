package xiaozhi.modules.knowledge.entity;

import java.io.Serializable;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Document shadow table for RAGFlow documents.
 * Backed by table: ai_knowledge_document.
 */
@Data
@TableName(value = "ai_rag_knowledge_document", autoResultMap = true)
@Schema(description = "Knowledge-base document table")
public class DocumentEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.ASSIGN_UUID)
    @Schema(description = "Local unique ID")
    private String id;

    @Schema(description = "Knowledge-base ID linked to ai_rag_dataset.dataset_id")
    private String datasetId;

    @Schema(description = "Remote RAGFlow document ID")
    private String documentId;

    @Schema(description = "Document name")
    private String name;

    @Schema(description = "File size in bytes")
    private Long size;

    @Schema(description = "File type such as pdf, doc, or txt")
    private String type;

    @Schema(description = "Chunking method")
    private String chunkMethod;

    @Schema(description = "Parser configuration as JSON")
    private String parserConfig;

    @Schema(description = "Availability status (1 enabled/healthy, 0 disabled/invalid)")
    private String status;

    @Schema(description = "Run state (UNSTART/RUNNING/CANCEL/DONE/FAIL)")
    private String run;

    @Schema(description = "Parse progress (0.0 to 1.0)")
    private Double progress;

    @Schema(description = "Thumbnail (Base64 or URL)")
    private String thumbnail;

    @Schema(description = "Parse duration in seconds")
    private Double processDuration;

    @Schema(description = "Custom metadata in JSON format")
    private String metaFields;

    @Schema(description = "Source type such as local, s3, or url")
    private String sourceType;

    @Schema(description = "Parse error message")
    private String error;

    @Schema(description = "Chunk count")
    private Integer chunkCount;

    @Schema(description = "Token count")
    private Long tokenCount;

    @Schema(description = "Enabled flag (0 disabled, 1 enabled)")
    private Integer enabled;

    @Schema(description = "Created by")
    @TableField(fill = FieldFill.INSERT)
    private Long creator;

    @Schema(description = "Created at")
    @TableField(fill = FieldFill.INSERT)
    private Date createdAt;

    @Schema(description = "Updated at")
    @TableField(fill = FieldFill.UPDATE)
    private Date updatedAt;

    @Schema(description = "Last synchronization time")
    private Date lastSyncAt;
}
