package xiaozhi.modules.knowledge.rag;

import java.util.List;
import java.util.Map;

import xiaozhi.modules.knowledge.dto.dataset.DatasetDTO;

import xiaozhi.common.page.PageData;
import xiaozhi.modules.knowledge.dto.KnowledgeFilesDTO;
import xiaozhi.modules.knowledge.dto.document.DocumentDTO;
import xiaozhi.modules.knowledge.dto.document.ChunkDTO;
import xiaozhi.modules.knowledge.dto.document.RetrievalDTO;
import java.util.function.Consumer;

/**
 * Abstract base class for knowledge-base API adapters.
 * Defines the common operations shared by multiple backend implementations.
 */
public abstract class KnowledgeBaseAdapter {

        /**
         * Return the adapter type identifier.
         * 
         * @return adapter type, for example ragflow, milvus, or pinecone
         */
        public abstract String getAdapterType();

        /**
         * Initialize the adapter configuration.
         * 
         * @param config configuration values
         */
        public abstract void initialize(Map<String, Object> config);

        /**
         * Validate the adapter configuration.
         * 
         * @param config configuration values
         * @return validation result
         */
        public abstract boolean validateConfig(Map<String, Object> config);

        /**
         * Query the document list with pagination.
         * 
         * @param datasetId knowledge base ID
         * @param req query parameters
         * @return paged result
         */
        public abstract PageData<KnowledgeFilesDTO> getDocumentList(String datasetId,
                        DocumentDTO.ListReq req);

        /**
         * Load document details by document ID.
         * 
         * @param datasetId knowledge base ID
         * @param documentId document ID
         * @return document details as a strongly typed InfoVO
         */
        public abstract DocumentDTO.InfoVO getDocumentById(String datasetId, String documentId);

        /**
         * Upload a document to the knowledge base.
         * 
         * @param req upload request parameters
         * @return uploaded document information
         */
        public abstract KnowledgeFilesDTO uploadDocument(DocumentDTO.UploadReq req);

        /**
         * Query the document list by status with pagination.
         * 
         * @param datasetId knowledge base ID
         * @param status document parsing status
         * @param page page number
         * @param limit page size
         * @return paged result
         */
        public abstract PageData<KnowledgeFilesDTO> getDocumentListByStatus(String datasetId,
                        Integer status,
                        Integer page,
                        Integer limit);

        /**
         * Delete one or more documents.
         * 
         * @param datasetId knowledge base ID
         * @param req request object containing document IDs
         */
        public abstract void deleteDocument(String datasetId, DocumentDTO.BatchIdReq req);

        /**
         * Parse documents into chunks.
         * 
         * @param datasetId knowledge base ID
         * @param documentIds document ID list
         * @return parse result
         */
        public abstract boolean parseDocuments(String datasetId, List<String> documentIds);

        /**
         * List chunks for the specified document.
         * 
         * @param datasetId knowledge base ID
         * @param documentId document ID
         * @param req list request parameters such as paging and keywords
         * @return chunk list response
         */
        public abstract ChunkDTO.ListVO listChunks(String datasetId,
                        String documentId,
                        ChunkDTO.ListReq req);

        /**
         * Run a retrieval test against the knowledge base.
         * 
         * @param req retrieval test request
         * @return retrieval test result
         */
        public abstract RetrievalDTO.ResultVO retrievalTest(
                        RetrievalDTO.TestReq req);

        /**
         * Test the backend connection.
         * 
         * @return connection test result
         */
        public abstract boolean testConnection();

        /**
         * Return adapter status information.
         * 
         * @return status information
         */
        public abstract Map<String, Object> getStatus();

        /**
         * Return supported configuration parameters.
         * 
         * @return configuration description
         */
        public abstract Map<String, Object> getSupportedConfig();

        /**
         * Return default configuration values.
         * 
         * @return default configuration
         */
        public abstract Map<String, Object> getDefaultConfig();

        /**
         * Create a dataset.
         * 
         * @param req creation parameters
         * @return dataset details
         */
        public abstract DatasetDTO.InfoVO createDataset(DatasetDTO.CreateReq req);

        /**
         * Update a dataset.
         * 
         * @param datasetId dataset ID
         * @param req update parameters
         * @return dataset details
         */
        public abstract DatasetDTO.InfoVO updateDataset(String datasetId, DatasetDTO.UpdateReq req);

        /**
         * Delete one or more datasets.
         * 
         * @param req delete request parameters containing IDs
         * @return batch operation result
         */
        public abstract DatasetDTO.BatchOperationVO deleteDataset(DatasetDTO.BatchIdReq req);

        /**
         * Return the document count for a dataset.
         * 
         * @param datasetId dataset ID
         * @return document count
         */
        public abstract Integer getDocumentCount(String datasetId);

        /**
         * Send a streaming request over SSE.
         * 
         * @param endpoint API endpoint
         * @param body request body
         * @param onData data callback
         */
        public abstract void postStream(String endpoint, Object body, Consumer<String> onData);

        /**
         * Ask SearchBot.
         *
         * @param config RAG configuration
         * @param body request body
         * @param onData data callback
         * @return response object
         */
        public abstract Object postSearchBotAsk(Map<String, Object> config, Object body,
                        Consumer<String> onData);

        /**
         * Run an AgentBot completion.
         *
         * @param config RAG configuration
         * @param agentId Agent ID
         * @param body request body
         * @param onData data callback
         */
        public abstract void postAgentBotCompletion(Map<String, Object> config, String agentId, Object body,
                        Consumer<String> onData);
}
