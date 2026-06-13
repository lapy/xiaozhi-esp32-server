package xiaozhi.modules.knowledge.service;

import java.util.List;

/**
 * Domain orchestration service for the knowledge-base module.
 * Handles cross-service workflows between KnowledgeBase and KnowledgeFiles.
 */
public interface KnowledgeManagerService {

    /**
     * Cascade-delete a knowledge base and all of its documents, including local DB and remote RAGFlow data.
     *
     * @param datasetId knowledge-base ID
     */
    void deleteDatasetWithFiles(String datasetId);

    /**
     * Cascade-delete knowledge bases in batch.
     *
     * @param datasetIds knowledge-base ID list
     */
    void batchDeleteDatasetsWithFiles(List<String> datasetIds);
}
