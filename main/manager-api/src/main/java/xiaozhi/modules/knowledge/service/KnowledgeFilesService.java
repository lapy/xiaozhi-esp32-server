package xiaozhi.modules.knowledge.service;

import java.util.List;
import java.util.Map;

import org.springframework.web.multipart.MultipartFile;

import xiaozhi.common.page.PageData;
import xiaozhi.modules.knowledge.dto.KnowledgeFilesDTO;
import xiaozhi.modules.knowledge.dto.document.ChunkDTO;
import xiaozhi.modules.knowledge.dto.document.RetrievalDTO;
import xiaozhi.modules.knowledge.dto.document.DocumentDTO;

/**
 * Knowledge-base document service interface.
 */
public interface KnowledgeFilesService {

        /**
         * Query the document list with pagination.
         *
         * @param knowledgeFilesDTO query filters
         * @param page              page number
         * @param limit             page size
         * @return paginated document data
         */
        PageData<KnowledgeFilesDTO> getPageList(KnowledgeFilesDTO knowledgeFilesDTO, Integer page, Integer limit);

        /**
         * Get document details by document ID and knowledge-base ID.
         *
         * @param documentId document ID
         * @param datasetId  knowledge-base ID
         * @return document details as a strongly typed InfoVO
         */
        DocumentDTO.InfoVO getByDocumentId(String documentId, String datasetId);

        /**
         * Upload a document to a knowledge base.
         *
         * @param datasetId    knowledge-base ID
         * @param file         uploaded file
         * @param name         document name
         * @param metaFields   metadata fields
         * @param chunkMethod  chunking method
         * @param parserConfig parser configuration
         * @return uploaded document information
         */
        KnowledgeFilesDTO uploadDocument(String datasetId, MultipartFile file, String name,
                        Map<String, Object> metaFields, String chunkMethod,
                        Map<String, Object> parserConfig);

        /**
         * Delete documents in batch.
         *
         * @param datasetId knowledge-base ID
         * @param req       delete request containing document IDs
         */
        void deleteDocuments(String datasetId, DocumentDTO.BatchIdReq req);

        /**
         * Get RAG configuration details.
         *
         * @param ragModelId RAG model configuration ID
         * @return RAG configuration
         */
        Map<String, Object> getRAGConfig(String ragModelId);

        /**
         * Parse and chunk documents.
         *
         * @param datasetId   knowledge-base ID
         * @param documentIds document ID list
         * @return parse result
         */
        boolean parseDocuments(String datasetId, List<String> documentIds);

        /**
         * List chunks for a specific document.
         *
         * @param datasetId  knowledge-base ID
         * @param documentId document ID
         * @param req        chunk-list request
         * @return chunk list information
         */
        ChunkDTO.ListVO listChunks(String datasetId, String documentId, ChunkDTO.ListReq req);

        /**
         * Run a retrieval test.
         *
         * @param req retrieval-test request
         * @return retrieval-test result
         */
        RetrievalDTO.ResultVO retrievalTest(RetrievalDTO.TestReq req);

        /**
         * Save a shadow record for a document.
         */
        void saveDocumentShadow(String datasetId, KnowledgeFilesDTO result, String originalName, String chunkMethod,
                        Map<String, Object> parserConfig);

        /**
         * Delete document shadow records in batch and sync aggregate stats.
         *
         * @param documentIds document ID list
         * @param datasetId   dataset ID
         * @param chunkDelta  total chunk count to subtract
         * @param tokenDelta  total token count to subtract
         */
        void deleteDocumentShadows(List<String> documentIds, String datasetId, Long chunkDelta, Long tokenDelta);

        /**
         * Remove all documents linked to a dataset.
         *
         * @param datasetId dataset ID
         */
        void deleteDocumentsByDatasetId(String datasetId);

        /**
         * Synchronize all documents currently in RUNNING state.
         */
        void syncRunningDocuments();
}
