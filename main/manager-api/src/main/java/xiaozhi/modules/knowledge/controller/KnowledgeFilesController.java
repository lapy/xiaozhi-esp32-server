package xiaozhi.modules.knowledge.controller;

import java.util.List;
import java.util.Map;

import org.apache.shiro.authz.annotation.RequiresPermissions;
import org.springdoc.core.annotations.ParameterObject;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.AllArgsConstructor;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.page.PageData;
import xiaozhi.common.utils.Result;
import xiaozhi.modules.knowledge.dto.KnowledgeBaseDTO;
import xiaozhi.modules.knowledge.dto.KnowledgeFilesDTO;
import xiaozhi.modules.knowledge.dto.document.ChunkDTO;
import xiaozhi.modules.knowledge.dto.document.DocumentDTO;
import xiaozhi.modules.knowledge.dto.document.RetrievalDTO;
import xiaozhi.modules.knowledge.service.KnowledgeBaseService;
import xiaozhi.modules.knowledge.service.KnowledgeFilesService;
import xiaozhi.modules.security.user.SecurityUser;

@AllArgsConstructor
@RestController
@RequestMapping("/datasets/{dataset_id}")
@Tag(name = "Knowledge Base Document Management")
public class KnowledgeFilesController {

    private final KnowledgeFilesService knowledgeFilesService;
    private final KnowledgeBaseService knowledgeBaseService;

    /**
     * Verify whether the current user can operate on the specified knowledge base.
     *
     * @param datasetId knowledge-base ID
     */
    private void validateKnowledgeBasePermission(String datasetId) {
        // Resolve the current user ID.
        Long currentUserId = SecurityUser.getUserId();

        // Load knowledge-base details.
        KnowledgeBaseDTO knowledgeBase = knowledgeBaseService.getByDatasetId(datasetId);

        // Users may operate only on knowledge bases they created.
        if (knowledgeBase.getCreator() == null || !knowledgeBase.getCreator().equals(currentUserId)) {
            throw new RenException(ErrorCode.NO_PERMISSION);
        }
    }

    @GetMapping("/documents")
    @Operation(summary = "List documents with pagination")
    @RequiresPermissions("sys:role:normal")
    public Result<PageData<KnowledgeFilesDTO>> getPageList(
            @PathVariable("dataset_id") String datasetId,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String status,
            @RequestParam(required = false, defaultValue = "1") Integer page,
            @RequestParam(required = false, defaultValue = "10") Integer page_size) {
        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);

        // Build query parameters.
        KnowledgeFilesDTO knowledgeFilesDTO = new KnowledgeFilesDTO();
        knowledgeFilesDTO.setDatasetId(datasetId);
        knowledgeFilesDTO.setName(name);
        knowledgeFilesDTO.setStatus(status);
        PageData<KnowledgeFilesDTO> pageData = knowledgeFilesService.getPageList(knowledgeFilesDTO, page, page_size);
        return new Result<PageData<KnowledgeFilesDTO>>().ok(pageData);
    }

    @GetMapping("/documents/status/{status}")
    @Operation(summary = "List documents by status with pagination")
    @RequiresPermissions("sys:role:normal")
    public Result<PageData<KnowledgeFilesDTO>> getPageListByStatus(
            @PathVariable("dataset_id") String datasetId,
            @PathVariable("status") String status,
            @RequestParam(required = false, defaultValue = "1") Integer page,
            @RequestParam(required = false, defaultValue = "10") Integer page_size) {
        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);
        // Build query parameters.
        KnowledgeFilesDTO knowledgeFilesDTO = new KnowledgeFilesDTO();
        knowledgeFilesDTO.setDatasetId(datasetId);
        knowledgeFilesDTO.setStatus(status);
        PageData<KnowledgeFilesDTO> pageData = knowledgeFilesService.getPageList(knowledgeFilesDTO, page, page_size);
        return new Result<PageData<KnowledgeFilesDTO>>().ok(pageData);
    }

    @PostMapping("/documents")
    @Operation(summary = "Upload a document to a knowledge base")
    @RequiresPermissions("sys:role:normal")
    public Result<KnowledgeFilesDTO> uploadDocument(
            @PathVariable("dataset_id") String datasetId,
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) String name,
            @RequestParam(required = false) String chunkMethod,
            @RequestParam(required = false) String metaFields,
            @RequestParam(required = false) String parserConfig) {

        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);

        KnowledgeFilesDTO resp = knowledgeFilesService.uploadDocument(datasetId, file, name,
                metaFields != null ? parseJsonMap(metaFields) : null,
                chunkMethod,
                parserConfig != null ? parseJsonMap(parserConfig) : null);
        return new Result<KnowledgeFilesDTO>().ok(resp);
    }

    @DeleteMapping("/documents")
    @Operation(summary = "Delete documents in batch")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> delete(@PathVariable("dataset_id") String datasetId,
            @RequestBody DocumentDTO.BatchIdReq req) {
        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);

        knowledgeFilesService.deleteDocuments(datasetId, req);
        return new Result<>();
    }

    @DeleteMapping("/documents/{document_id}")
    @Operation(summary = "Delete a single document")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> deleteSingle(@PathVariable("dataset_id") String datasetId,
            @PathVariable("document_id") String documentId) {
        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);

        DocumentDTO.BatchIdReq req = new DocumentDTO.BatchIdReq();
        req.setIds(java.util.Collections.singletonList(documentId));
        knowledgeFilesService.deleteDocuments(datasetId, req);
        return new Result<>();
    }

    @PostMapping("/chunks")
    @Operation(summary = "Parse and chunk documents")
    @RequiresPermissions("sys:role:normal")
    public Result<Void> parseDocuments(@PathVariable("dataset_id") String datasetId,
            @RequestBody Map<String, List<String>> requestBody) {
        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);

        List<String> documentIds = requestBody.get("document_ids");
        if (documentIds == null || documentIds.isEmpty()) {
            return new Result<Void>().error("The document_ids parameter cannot be empty");
        }

        boolean success = knowledgeFilesService.parseDocuments(datasetId, documentIds);
        if (success) {
            return new Result<Void>();
        } else {
            return new Result<Void>().error("Document parsing failed, and the document may still be processing");
        }
    }

    @GetMapping("/documents/{document_id}/chunks")
    @Operation(summary = "List chunks for a specific document")
    @RequiresPermissions("sys:role:normal")
    public Result<ChunkDTO.ListVO> listChunks(
            @PathVariable("dataset_id") String datasetId,
            @PathVariable("document_id") String documentId,
            @ParameterObject ChunkDTO.ListReq req) {

        // Validate permissions. This also checks knowledge-base existence and ownership.
        validateKnowledgeBasePermission(datasetId);

        // Apply defaults.
        if (req.getPage() == null)
            req.setPage(1);
        if (req.getPageSize() == null)
            req.setPageSize(50);

        // Delegate to the service layer and return a strongly typed chunk list.
        ChunkDTO.ListVO result = knowledgeFilesService.listChunks(datasetId, documentId, req);
        return new Result<ChunkDTO.ListVO>().ok(result);
    }

    @PostMapping("/retrieval-test")
    @Operation(summary = "Run retrieval test")
    @RequiresPermissions("sys:role:normal")
    public Result<RetrievalDTO.ResultVO> retrievalTest(
            @PathVariable("dataset_id") String datasetId,
            @RequestBody RetrievalDTO.TestReq req) {

        // Validate knowledge-base permissions.
        validateKnowledgeBasePermission(datasetId);

        // Default to the current dataset when no dataset IDs are provided.
        if (req.getDatasetIds() == null || req.getDatasetIds().isEmpty()) {
            req.setDatasetIds(java.util.Arrays.asList(datasetId));
        }

        // Clamp pagination parameters to prevent negative slicing errors on the RAGFlow side.
        if (req.getPage() == null || req.getPage() < 1) {
            req.setPage(1);
        }
        if (req.getPageSize() == null || req.getPageSize() < 1) {
            req.setPageSize(100);
        }

        // Call the retrieval service and return a strongly typed aggregate result.
        RetrievalDTO.ResultVO result = knowledgeFilesService.retrievalTest(req);
        return new Result<RetrievalDTO.ResultVO>().ok(result);
    }

    /**
     * Parse a JSON string into a map.
     */
    private Map<String, Object> parseJsonMap(String jsonString) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            return objectMapper.readValue(jsonString, new TypeReference<Map<String, Object>>() {
            });
        } catch (Exception e) {
            throw new RuntimeException("Failed to parse JSON string: " + jsonString, e);
        }
    }
}
