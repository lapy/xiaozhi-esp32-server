package xiaozhi.modules.knowledge.dto.file;

import lombok.*;
import io.swagger.v3.oas.annotations.media.Schema;
import java.io.Serializable;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.*;
import org.springframework.web.multipart.MultipartFile;

/**
 * Aggregate DTOs for file management.
 * <p>
 * Container for request/response objects used by the file module.
 * </p>
 */
@Schema(description = "Aggregate DTOs for file management")
public class FileDTO {

    // ========== Requests ==========

    /**
     * File upload request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "File upload request")
    public static class UploadReq implements Serializable {

        @NotNull(message = "File cannot be empty")
        @Schema(description = "Uploaded file", requiredMode = Schema.RequiredMode.REQUIRED)
        private MultipartFile file;

        @Schema(description = "Parent folder ID. Uploads to the root when empty", example = "folder_001")
        @JsonProperty("parent_id")
        private String parentId;
    }

    /**
     * Create folder request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Create folder request")
    public static class CreateReq implements Serializable {

        @NotBlank(message = "Folder name cannot be empty")
        @Schema(description = "Folder name", requiredMode = Schema.RequiredMode.REQUIRED, example = "New Folder")
        private String name;

        @Schema(description = "Parent folder ID. Creates in the root when empty", example = "folder_001")
        @JsonProperty("parent_id")
        private String parentId;

        @NotBlank(message = "Type cannot be empty")
        @Schema(description = "Type: FOLDER", requiredMode = Schema.RequiredMode.REQUIRED, example = "FOLDER")
        @Builder.Default
        private String type = "FOLDER";
    }

    /**
     * Rename request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Rename request")
    public static class RenameReq implements Serializable {

        @NotBlank(message = "File ID cannot be empty")
        @Schema(description = "File or folder ID", requiredMode = Schema.RequiredMode.REQUIRED, example = "file_001")
        @JsonProperty("file_id")
        private String fileId;

        @NotBlank(message = "New name cannot be empty")
        @Schema(description = "New name", requiredMode = Schema.RequiredMode.REQUIRED, example = "renamed-file")
        private String name;
    }

    /**
     * Move request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Move request")
    public static class MoveReq implements Serializable {

        @NotEmpty(message = "Source file ID list cannot be empty")
        @Schema(description = "Source file or folder ID list", requiredMode = Schema.RequiredMode.REQUIRED,
                example = "[\"file_001\", \"file_002\"]")
        @JsonProperty("src_file_ids")
        private List<String> srcFileIds;

        @NotBlank(message = "Destination folder ID cannot be empty")
        @Schema(description = "Destination folder ID", requiredMode = Schema.RequiredMode.REQUIRED,
                example = "folder_002")
        @JsonProperty("dest_file_id")
        private String destFileId;
    }

    /**
     * Bulk delete request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Bulk delete request")
    public static class RemoveReq implements Serializable {

        @NotEmpty(message = "File ID list cannot be empty")
        @Schema(description = "File or folder ID list", requiredMode = Schema.RequiredMode.REQUIRED,
                example = "[\"file_001\", \"file_002\"]")
        @JsonProperty("file_ids")
        private List<String> fileIds;
    }

    /**
     * Convert-to-knowledge-base request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Convert-to-knowledge-base request")
    public static class ConvertReq implements Serializable {

        @NotEmpty(message = "File ID list cannot be empty")
        @Schema(description = "File ID list", requiredMode = Schema.RequiredMode.REQUIRED,
                example = "[\"file_001\", \"file_002\"]")
        @JsonProperty("file_ids")
        private List<String> fileIds;

        @NotEmpty(message = "Knowledge base ID list cannot be empty")
        @Schema(description = "Target knowledge base ID list", requiredMode = Schema.RequiredMode.REQUIRED,
                example = "[\"kb_001\"]")
        @JsonProperty("kb_ids")
        private List<String> kbIds;
    }

    /**
     * List query request.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "List query request")
    public static class ListReq implements Serializable {

        @Schema(description = "Parent folder ID. Queries the root directory when empty", example = "folder_001")
        @JsonProperty("parent_id")
        private String parentId;

        @Schema(description = "Keyword search", example = "document")
        private String keywords;

        @Schema(description = "Page number, starting from 1", example = "1")
        private Integer page;

        @Schema(description = "Page size", example = "30")
        @JsonProperty("page_size")
        private Integer pageSize;

        @Schema(description = "Sort field: create_time / update_time / name / size", example = "create_time")
        private String orderby;

        @Schema(description = "Whether sorting is descending", example = "true")
        private Boolean desc;
    }

    // ========== Responses ==========

    /**
     * Basic file or folder information.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Basic file or folder information")
    public static class InfoVO implements Serializable {

        @Schema(description = "File or folder ID", example = "file_001")
        private String id;

        @Schema(description = "Parent folder ID", example = "folder_001")
        @JsonProperty("parent_id")
        private String parentId;

        @Schema(description = "Tenant ID", example = "tenant_001")
        @JsonProperty("tenant_id")
        private String tenantId;

        @Schema(description = "Creator ID", example = "user_001")
        @JsonProperty("created_by")
        private String createdBy;

        @Schema(description = "Type: FOLDER / FILE", example = "FOLDER")
        private String type;

        @Schema(description = "Name", example = "My Folder")
        private String name;

        @Schema(description = "Path location", example = "/root/folder")
        private String location;

        @Schema(description = "File size in bytes", example = "1024")
        private Long size;

        @Schema(description = "Source type", example = "local")
        @JsonProperty("source_type")
        private String sourceType;

        @Schema(description = "Creation time as a timestamp", example = "1700000000000")
        @JsonProperty("create_time")
        private Long createTime;

        @Schema(description = "Formatted creation date", example = "2024-01-15 10:30:00")
        @JsonProperty("create_date")
        private String createDate;

        @Schema(description = "Update time as a timestamp", example = "1700000001000")
        @JsonProperty("update_time")
        private Long updateTime;

        @Schema(description = "Formatted update date", example = "2024-01-15 11:00:00")
        @JsonProperty("update_date")
        private String updateDate;

        @Schema(description = "File extension", example = "pdf")
        private String extension;
    }

    /**
     * List response.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "File list response")
    public static class ListVO implements Serializable {

        @Schema(description = "Total record count", example = "100")
        private Long total;

        @Schema(description = "Current parent folder information")
        @JsonProperty("parent_folder")
        private InfoVO parentFolder;

        @Schema(description = "List of files and folders")
        private List<InfoVO> files;

        @Schema(description = "Breadcrumb navigation path")
        private List<InfoVO> breadcrumb;
    }

    /**
     * Conversion result item.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "File conversion result item")
    public static class ConvertVO implements Serializable {

        @Schema(description = "Conversion record ID", example = "convert_001")
        private String id;

        @Schema(description = "Source file ID", example = "file_001")
        @JsonProperty("file_id")
        private String fileId;

        @Schema(description = "Target document ID", example = "doc_001")
        @JsonProperty("document_id")
        private String documentId;

        @Schema(description = "Creation time as a timestamp", example = "1700000000000")
        @JsonProperty("create_time")
        private Long createTime;

        @Schema(description = "Formatted creation date", example = "2024-01-15 10:30:00")
        @JsonProperty("create_date")
        private String createDate;

        @Schema(description = "Update time as a timestamp", example = "1700000001000")
        @JsonProperty("update_time")
        private Long updateTime;

        @Schema(description = "Formatted update date", example = "2024-01-15 11:00:00")
        @JsonProperty("update_date")
        private String updateDate;
    }

    /**
     * Conversion status.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "File conversion status")
    public static class ConvertStatusVO implements Serializable {

        @Schema(description = "Conversion status: pending / processing / completed / failed", example = "completed")
        private String status;

        @Schema(description = "Conversion progress (0.0 - 1.0)", example = "1.0")
        private Float progress;

        @Schema(description = "Status message", example = "Conversion completed")
        private String message;
    }

    /**
     * Breadcrumb data.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Breadcrumb navigation")
    public static class BreadcrumbVO implements Serializable {

        @Schema(description = "Parent folder list from root to current path")
        @JsonProperty("parent_folders")
        private List<InfoVO> parentFolders;
    }

    /**
     * Root folder information.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Root folder information")
    public static class RootFolderVO implements Serializable {

        @Schema(description = "Root folder information")
        @JsonProperty("root_folder")
        private InfoVO rootFolder;
    }

    /**
     * Parent folder information.
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    @Schema(description = "Parent folder information")
    public static class ParentFolderVO implements Serializable {

        @Schema(description = "Parent folder information")
        @JsonProperty("parent_folder")
        private InfoVO parentFolder;
    }
}
