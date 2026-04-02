package xiaozhi.modules.knowledge.rag.impl;

import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

import org.apache.commons.lang3.StringUtils;
import org.springframework.core.io.AbstractResource;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.multipart.MultipartFile;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.extern.slf4j.Slf4j;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.page.PageData;
import xiaozhi.modules.knowledge.dto.KnowledgeFilesDTO;
import xiaozhi.modules.knowledge.dto.dataset.DatasetDTO;
import xiaozhi.modules.knowledge.dto.document.ChunkDTO;
import xiaozhi.modules.knowledge.dto.document.RetrievalDTO;
import xiaozhi.modules.knowledge.dto.document.DocumentDTO;
import xiaozhi.modules.knowledge.rag.KnowledgeBaseAdapter;
import xiaozhi.modules.knowledge.rag.RAGFlowClient;

/**
 * RAGFlow knowledge-base adapter implementation.
 * <p>
 * Refactoring note:
 * This class now uses {@link RAGFlowClient} to centralize HTTP communication
 * and fix the old scattered timeout and error-handling behavior.
 * </p>
 */
@Slf4j
public class RAGFlowAdapter extends KnowledgeBaseAdapter {

    private static final String ADAPTER_TYPE = "ragflow";

    private Map<String, Object> config;
    private ObjectMapper objectMapper;
    // Client instance created during initialization.
    private RAGFlowClient client;

    public RAGFlowAdapter() {
        this.objectMapper = new ObjectMapper();
    }

    @Override
    public String getAdapterType() {
        return ADAPTER_TYPE;
    }

    @Override
    public void initialize(Map<String, Object> config) {
        this.config = config;
        validateConfig(config);

        String baseUrl = getConfigValue(config, "base_url", "baseUrl");
        String apiKey = getConfigValue(config, "api_key", "apiKey");

        // Initialize the client. Default timeout is 30 seconds and can be overridden in config.
        int timeout = 30;
        Object timeoutObj = getConfigValue(config, "timeout", "timeout");
        if (timeoutObj != null) {
            try {
                timeout = Integer.parseInt(timeoutObj.toString());
            } catch (Exception e) {
                log.warn("Failed to parse the timeout configuration, using the default value of 30s");
            }
        }
        this.client = new RAGFlowClient(baseUrl, apiKey, timeout);
        log.info("RAGFlow adapter initialization completed and the client is ready");
    }

    @Override
    public boolean validateConfig(Map<String, Object> config) {
        if (config == null) {
            throw new RenException(ErrorCode.RAG_CONFIG_NOT_FOUND);
        }

        String baseUrl = getConfigValue(config, "base_url", "baseUrl");
        String apiKey = getConfigValue(config, "api_key", "apiKey");

        if (StringUtils.isBlank(baseUrl)) {
            throw new RenException(ErrorCode.RAG_API_ERROR_URL_NULL);
        }

        if (StringUtils.isBlank(apiKey)) {
            throw new RenException(ErrorCode.RAG_API_ERROR_API_KEY_NULL);
        }

        if (apiKey.contains("your")) {
            throw new RenException(ErrorCode.RAG_API_ERROR_API_KEY_INVALID);
        }

        if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) {
            throw new RenException(ErrorCode.RAG_API_ERROR_URL_INVALID);
        }

        return true;
    }

    /**
     * Helper: read config values using either camelCase or snake_case keys.
     */
    private String getConfigValue(Map<String, Object> config, String snakeKey, String camelKey) {
        if (config.containsKey(snakeKey)) {
            return (String) config.get(snakeKey);
        }
        if (config.containsKey(camelKey)) {
            return (String) config.get(camelKey);
        }
        return null;
    }

    /**
     * Helper: ensure the client has been initialized.
     */
    private RAGFlowClient getClient() {
        if (this.client == null) {
            // Attempt to initialize again.
            if (this.config != null) {
                initialize(this.config);
            } else {
                throw new RenException(ErrorCode.RAG_CONFIG_NOT_FOUND, "Adapter has not been initialized");
            }
        }
        return this.client;
    }

    private RenException convertToRenException(Exception e) {
        if (e instanceof RenException) {
            return (RenException) e;
        }
        return new RenException(ErrorCode.RAG_API_ERROR, e.getMessage());
    }

    @Override
    public PageData<KnowledgeFilesDTO> getDocumentList(String datasetId, DocumentDTO.ListReq req) {
        try {
            log.info("=== [RAGFlow] Loading document list: datasetId={} ===", datasetId);

            // Convert the DTO to a query-parameter map through Jackson.
            @SuppressWarnings("unchecked")
            Map<String, Object> params = objectMapper.convertValue(req, Map.class);

            Map<String, Object> response = getClient().get("/api/v1/datasets/" + datasetId + "/documents", params);

            Object dataObj = response.get("data");
            return parseDocumentListResponse(dataObj, req.getPage() != null ? req.getPage() : 1,
                    req.getPageSize() != null ? req.getPageSize() : 10);

        } catch (Exception e) {
            log.error("Failed to load the document list", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public DocumentDTO.InfoVO getDocumentById(String datasetId, String documentId) {
        try {
            log.info("=== [RAGFlow] Loading document details: datasetId={}, documentId={} ===", datasetId, documentId);
            DocumentDTO.ListReq req = DocumentDTO.ListReq.builder()
                    .id(documentId)
                    .page(1)
                    .pageSize(1)
                    .build();

            @SuppressWarnings("unchecked")
            Map<String, Object> params = objectMapper.convertValue(req, Map.class);
            Map<String, Object> response = getClient().get("/api/v1/datasets/" + datasetId + "/documents", params);

            Object dataObj = response.get("data");
            if (dataObj instanceof Map) {
                Map<String, Object> dataMap = (Map<String, Object>) dataObj;
                List<?> documents = (List<?>) dataMap.get("docs");
                if (documents != null && !documents.isEmpty()) {
                    return objectMapper.convertValue(documents.get(0), DocumentDTO.InfoVO.class);
                }
            }
            return null;
        } catch (Exception e) {
            log.error("Failed to load document details: documentId={}", documentId, e);
            throw convertToRenException(e);
        }
    }

    @Override
    public KnowledgeFilesDTO uploadDocument(DocumentDTO.UploadReq req) {
        String datasetId = req.getDatasetId();
        MultipartFile file = req.getFile();
        try {
            log.info("=== [RAGFlow] Uploading document: datasetId={} ===", datasetId);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new MultipartFileResource(file));

            if (StringUtils.isNotBlank(req.getName())) {
                body.add("name", req.getName());
            }
            if (req.getMetaFields() != null && !req.getMetaFields().isEmpty()) {
                body.add("meta", objectMapper.writeValueAsString(req.getMetaFields()));
            }
            if (req.getChunkMethod() != null) {
                // Convert the enum to the lowercase string expected by RAGFlow, for example NAIVE -> naive.
                body.add("chunk_method", req.getChunkMethod().name().toLowerCase());
            }
            if (req.getParserConfig() != null) {
                body.add("parser_config", objectMapper.writeValueAsString(req.getParserConfig()));
            }
            if (StringUtils.isNotBlank(req.getParentPath())) {
                body.add("parent_path", req.getParentPath());
            }

            Map<String, Object> response = getClient().postMultipart("/api/v1/datasets/" + datasetId + "/documents",
                    body);

            Object dataObj = response.get("data");
            return parseUploadResponse(dataObj, datasetId, file);

        } catch (Exception e) {
            log.error("Document upload failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public PageData<KnowledgeFilesDTO> getDocumentListByStatus(String datasetId, Integer status, Integer page,
            Integer limit) {
        List<DocumentDTO.InfoVO.RunStatus> runStatusList = null;
        if (status != null) {
            runStatusList = new ArrayList<>();
            switch (status) {
                case 0:
                    runStatusList.add(DocumentDTO.InfoVO.RunStatus.UNSTART);
                    break;
                case 1:
                    runStatusList.add(DocumentDTO.InfoVO.RunStatus.RUNNING);
                    break;
                case 2:
                    runStatusList.add(DocumentDTO.InfoVO.RunStatus.CANCEL);
                    break;
                case 3:
                    runStatusList.add(DocumentDTO.InfoVO.RunStatus.DONE);
                    break;
                case 4:
                    runStatusList.add(DocumentDTO.InfoVO.RunStatus.FAIL);
                    break;
                default:
                    break;
            }
        }
        DocumentDTO.ListReq req = DocumentDTO.ListReq.builder()
                .run(runStatusList)
                .page(page)
                .pageSize(limit)
                .build();
        return getDocumentList(datasetId, req);
    }

    @Override
    public void deleteDocument(String datasetId, DocumentDTO.BatchIdReq req) {
        try {
            log.info("=== [RAGFlow] Bulk deleting documents: datasetId={}, count={} ===", datasetId,
                    req.getIds() != null ? req.getIds().size() : 0);
            getClient().delete("/api/v1/datasets/" + datasetId + "/documents", req);
        } catch (Exception e) {
            log.error("Bulk document deletion failed: datasetId={}", datasetId, e);
            throw convertToRenException(e);
        }
    }

    @Override
    public boolean parseDocuments(String datasetId, List<String> documentIds) {
        try {
            log.info("=== [RAGFlow] Parsing documents ===");
            Map<String, Object> body = new HashMap<>();
            body.put("document_ids", documentIds);

            getClient().post("/api/v1/datasets/" + datasetId + "/chunks", body);
            return true;
        } catch (Exception e) {
            log.error("Document parsing failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public ChunkDTO.ListVO listChunks(String datasetId, String documentId, ChunkDTO.ListReq req) {
        try {
            // [Refactor] Convert query parameters dynamically with objectMapper to avoid hard-coded mapping.
            Map<String, Object> params = objectMapper.convertValue(req, new TypeReference<Map<String, Object>>() {
            });

            Map<String, Object> response = getClient()
                    .get("/api/v1/datasets/" + datasetId + "/documents/" + documentId + "/chunks", params);

            Object dataObj = response.get("data");
            if (dataObj == null) {
                log.warn("[RAGFlow] listChunks returned an empty data payload, docId={}", documentId);
                return ChunkDTO.ListVO.builder()
                        .chunks(new ArrayList<>())
                        .total(0L)
                        .build();
            }

            ChunkDTO.ListVO result = objectMapper.convertValue(dataObj, ChunkDTO.ListVO.class);
            if (result.getTotal() == null) {
                result.setTotal(0L);
            }
            return result;
        } catch (Exception e) {
            log.error("Failed to load chunks: docId={}", documentId, e);
            throw convertToRenException(e);
        }
    }

    @Override
    public RetrievalDTO.ResultVO retrievalTest(RetrievalDTO.TestReq req) {
        try {
            // [Production Reinforce] Normalize paging defensively because the Python side is sensitive
            // to zero or negative slicing and can raise ValueError.
            if (req.getPage() != null && req.getPage() < 1) {
                req.setPage(1);
            }
            if (req.getPageSize() != null && req.getPageSize() < 1) {
                req.setPageSize(10); // Default to 10 rows.
            }
            if (req.getTopK() != null && req.getTopK() < 1) {
                req.setTopK(1024); // Internal RAGFlow default TopK.
            }
            // Normalize the similarity threshold to the 0.0 to 1.0 range.
            if (req.getSimilarityThreshold() != null) {
                if (req.getSimilarityThreshold() < 0f)
                    req.setSimilarityThreshold(0.2f);
                if (req.getSimilarityThreshold() > 1f)
                    req.setSimilarityThreshold(1.0f);
            }

            // [Refactor] Pass the strongly typed DTO directly and let getClient handle serialization.
            Map<String, Object> response = getClient().post("/api/v1/retrieval", req);

            Object dataObj = response.get("data");
            if (dataObj == null) {
                log.warn("[RAGFlow] retrievalTest returned an empty data payload");
                return RetrievalDTO.ResultVO.builder()
                        .chunks(new ArrayList<>())
                        .docAggs(new ArrayList<>())
                        .total(0L)
                        .build();
            }

            RetrievalDTO.ResultVO result = objectMapper.convertValue(dataObj, RetrievalDTO.ResultVO.class);
            if (result.getTotal() == null) {
                result.setTotal(0L);
            }
            return result;
        } catch (Exception e) {
            log.error("Retrieval test failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public boolean testConnection() {
        try {
            getClient().get("/api/v1/health", null);
            return true;
        } catch (Exception e) {
            log.error("Connection test failed: {}", e.getMessage());
            return false;
        }
    }

    @Override
    public Map<String, Object> getStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("adapterType", getAdapterType());
        status.put("configKeys", config != null ? config.keySet() : "not configured");
        status.put("connectionTest", testConnection());
        status.put("lastChecked", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        return status;
    }

    @Override
    public Map<String, Object> getSupportedConfig() {
        Map<String, Object> supportedConfig = new HashMap<>();
        supportedConfig.put("base_url", "RAGFlow API base URL");
        supportedConfig.put("api_key", "RAGFlow API key");
        supportedConfig.put("timeout", "Request timeout in milliseconds");
        return supportedConfig;
    }

    @Override
    public Map<String, Object> getDefaultConfig() {
        Map<String, Object> defaultConfig = new HashMap<>();
        defaultConfig.put("timeout", 30000);
        return defaultConfig;
    }

    @Override
    public DatasetDTO.InfoVO createDataset(DatasetDTO.CreateReq req) {
        try {
            // [Production Fix] Strengthen default handling so the RAGFlow API does not fail
            // when fields are empty or missing.
            if (StringUtils.isBlank(req.getPermission())) {
                req.setPermission("me");
            }
            if (StringUtils.isBlank(req.getChunkMethod())) {
                req.setChunkMethod("naive");
            }

            // Auto-fill the embedding model. Prefer the request value, then the configured default.
            if (StringUtils.isBlank(req.getEmbeddingModel())) {
                String defaultModel = (String) getConfigValue(config, "embedding_model", "embeddingModel");
                if (StringUtils.isNotBlank(defaultModel)) {
                    log.info("RAGFlow: using the configured default embedding model: {}", defaultModel);
                    req.setEmbeddingModel(defaultModel);
                }
                // If there is no configured default, leave it empty and let the server decide.
            }

            // Auto-fill avatar with a 1x1 transparent pixel when empty so MIME-prefix validation passes.
            if (StringUtils.isBlank(req.getAvatar())) {
                req.setAvatar(
                        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");
            }

            // Pass the strongly typed request object directly. Jackson will handle JsonProperty mapping.
            Map<String, Object> response = getClient().post("/api/v1/datasets", req);

            // Safely read data and map it fully through DatasetDTO.InfoVO.
            Object dataObj = response.get("data");
            if (dataObj != null) {
                return objectMapper.convertValue(dataObj, DatasetDTO.InfoVO.class);
            }
            throw new RenException(ErrorCode.RAG_API_ERROR, "Invalid response from createDataset: missing data object");
        } catch (Exception e) {
            log.error("Dataset creation failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public DatasetDTO.InfoVO updateDataset(String datasetId, DatasetDTO.UpdateReq req) {
        try {
            // The recommended RAGFlow update path includes the dataset ID.
            Map<String, Object> response = getClient().put("/api/v1/datasets/" + datasetId, req);

            Object dataObj = response.get("data");
            if (dataObj != null) {
                return objectMapper.convertValue(dataObj, DatasetDTO.InfoVO.class);
            }
            return null;
        } catch (Exception e) {
            log.error("Dataset update failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public DatasetDTO.BatchOperationVO deleteDataset(DatasetDTO.BatchIdReq req) {
        try {
            // RAGFlow uses DELETE /api/v1/datasets for bulk dataset removal.
            Map<String, Object> response = getClient().delete("/api/v1/datasets", req);

            Object dataObj = response.get("data");
            if (dataObj != null) {
                return objectMapper.convertValue(dataObj, DatasetDTO.BatchOperationVO.class);
            }
            return null;
        } catch (Exception e) {
            log.error("Bulk dataset deletion failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public Integer getDocumentCount(String datasetId) {
        try {
            // [Fix] Use the list/filter endpoint to load details (GET /datasets?id={id}).
            Map<String, Object> params = new HashMap<>();
            params.put("id", datasetId);
            params.put("page", 1);
            params.put("page_size", 1);

            Map<String, Object> response = getClient().get("/api/v1/datasets", params);
            Object dataObj = response.get("data");

            if (dataObj instanceof List) {
                List<?> list = (List<?>) dataObj;
                if (!list.isEmpty()) {
                    Object firstItem = list.get(0);
                    if (firstItem instanceof Map) {
                        Object countObj = ((Map<?, ?>) firstItem).get("document_count");
                        if (countObj instanceof Number) {
                            return ((Number) countObj).intValue();
                        }
                    }
                }
            }
            // Fallback when nothing is found or the structure is not what we expect.
            return 0;
        } catch (Exception e) {
            log.warn("Failed to load document count: {}", e.getMessage());
            return 0;
        }
    }

    @Override
    public void postStream(String endpoint, Object body, Consumer<String> onData) {
        try {
            getClient().postStream(endpoint, body, onData);
        } catch (Exception e) {
            log.error("Streaming request failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public Object postSearchBotAsk(Map<String, Object> config, Object body,
            Consumer<String> onData) {
        // SearchBot is effectively a dataset-search wrapper, or possibly a not-yet-public API.
        // Assume there is no dedicated SDK route beyond retrieval/chat behavior.
        // BotDTO implies a /api/v1/searchbots/ask endpoint.
        // The config may override defaults, but in practice this adapter usually uses its own client.
        // If SearchBot should use a different key later, that can be revisited.

        // For now assume /api/v1/searchbots/ask or an equivalent endpoint exists.
        try {
            getClient().postStream("/api/v1/searchbots/ask", body, onData);
            return null;
        } catch (Exception e) {
            log.error("SearchBot ask failed", e);
            throw convertToRenException(e);
        }
    }

    @Override
    public void postAgentBotCompletion(Map<String, Object> config, String agentId, Object body,
            Consumer<String> onData) {
        // AgentBot maps to /api/v1/agentbots/{id}/completions.
        try {
            getClient().postStream("/api/v1/agentbots/" + agentId + "/completions", body, onData);
        } catch (Exception e) {
            log.error("AgentBot completion failed", e);
            throw convertToRenException(e);
        }
    }

    // Reuse the existing helper parsing path to preserve compatibility.
    // [Bug Fix] Do not swallow deserialization errors, or upper layers may misclassify the document as deleted.
    private PageData<KnowledgeFilesDTO> parseDocumentListResponse(Object dataObj, long curPage, long pageSize) {
        if (dataObj == null) {
            return new PageData<>(new ArrayList<>(), 0);
        }

        Map<String, Object> dataMap = (Map<String, Object>) dataObj;
        List<Map<String, Object>> documents = (List<Map<String, Object>>) dataMap.get("docs");
        if (documents == null || documents.isEmpty()) {
            // RAGFlow explicitly returned an empty document list. That is a valid empty state.
            return new PageData<>(new ArrayList<>(), 0);
        }

        List<KnowledgeFilesDTO> list = new ArrayList<>();
        for (Object docObj : documents) {
            try {
                // Be tolerant per document so one deserialization failure does not block the rest.
                DocumentDTO.InfoVO info = objectMapper.convertValue(docObj, DocumentDTO.InfoVO.class);
                list.add(mapToKnowledgeFilesDTO(info, null));
            } catch (Exception e) {
                log.warn("[RAGFlow] Single-document DTO conversion failed, skipping that document: {}", e.getMessage());
            }
        }

        long total = 0;
        if (dataMap.containsKey("total")) {
            total = ((Number) dataMap.get("total")).longValue();
        }

        return new PageData<>(list, total);
    }

    private KnowledgeFilesDTO parseUploadResponse(Object dataObj, String datasetId, MultipartFile file) {
        KnowledgeFilesDTO result = null;

        // Try to extract documentId from the response payload.
        if (dataObj != null) {
            try {
                DocumentDTO.InfoVO info = null;
                if (dataObj instanceof Map) {
                    info = objectMapper.convertValue(dataObj, DocumentDTO.InfoVO.class);
                } else if (dataObj instanceof List) {
                    List<?> list = (List<?>) dataObj;
                    if (!list.isEmpty()) {
                        info = objectMapper.convertValue(list.get(0), DocumentDTO.InfoVO.class);
                    }
                }

                if (info != null) {
                    result = mapToKnowledgeFilesDTO(info, datasetId);
                }
            } catch (Exception e) {
                log.warn("Failed to parse upload response data: {}", e.getMessage());
            }
        }

        if (result == null) {
            log.error("Could not extract documentId from the RAGFlow response, payload: {}", dataObj);
            // Return a minimal DTO instead of null so upstream callers do not hit NPEs.
            result = new KnowledgeFilesDTO();
            result.setDatasetId(datasetId);
            result.setName(file.getOriginalFilename());
            result.setFileSize(file.getSize());
            result.setStatus("1");
        }

        return result;
    }

    /**
     * Map RAGFlow's strongly typed InfoVO to the internal KnowledgeFilesDTO.
     * Keep all available fields in sync, including names, sizes, status, and parser config.
     */
    private KnowledgeFilesDTO mapToKnowledgeFilesDTO(DocumentDTO.InfoVO info, String datasetId) {
        KnowledgeFilesDTO dto = new KnowledgeFilesDTO();
        if (info == null)
            return dto;

        dto.setId(info.getId());
        dto.setDocumentId(info.getId());
        dto.setDatasetId(StringUtils.isNotBlank(info.getDatasetId()) ? info.getDatasetId() : datasetId);
        dto.setName(info.getName());
        dto.setFileSize(info.getSize());

        // Status mapping.
        if (info.getRun() != null) {
            dto.setRun(info.getRun().name());
        }

        if (StringUtils.isNotBlank(info.getStatus())) {
            dto.setStatus(info.getStatus());
        } else {
            dto.setStatus("1"); // Enabled by default.
        }

        // Timestamp synchronization.
        if (info.getCreateTime() != null) {
            dto.setCreatedAt(new Date(info.getCreateTime()));
        }
        if (info.getUpdateTime() != null) {
            dto.setUpdatedAt(new Date(info.getUpdateTime()));
        }

        // Fill the core metadata fields (Issue 1).
        dto.setProgress(info.getProgress());
        dto.setThumbnail(info.getThumbnail());
        dto.setProcessDuration(info.getProcessDuration());
        dto.setSourceType(info.getSourceType());
        dto.setChunkCount(info.getChunkCount() != null ? info.getChunkCount().intValue() : 0);
        dto.setTokenCount(info.getTokenCount());
        dto.setError(info.getProgressMsg()); // Reuse the progress message as the error hint field.

        // Synchronize extended fields.
        dto.setMetaFields(info.getMetaFields());
        if (info.getChunkMethod() != null) {
            dto.setChunkMethod(info.getChunkMethod().name().toLowerCase());
        }
        if (info.getParserConfig() != null) {
            dto.setParserConfig(objectMapper.convertValue(info.getParserConfig(), Map.class));
        }

        return dto;
    }

    private static class MultipartFileResource extends AbstractResource {
        private final MultipartFile multipartFile;

        public MultipartFileResource(MultipartFile multipartFile) {
            this.multipartFile = multipartFile;
        }

        @Override
        public String getDescription() {
            return "MultipartFile resource [" + multipartFile.getOriginalFilename() + "]";
        }

        @Override
        public String getFilename() {
            return multipartFile.getOriginalFilename();
        }

        @Override
        public InputStream getInputStream() throws IOException {
            return multipartFile.getInputStream();
        }

        @Override
        public long contentLength() throws IOException {
            return multipartFile.getSize();
        }

        @Override
        public boolean exists() {
            return !multipartFile.isEmpty();
        }
    }
}
