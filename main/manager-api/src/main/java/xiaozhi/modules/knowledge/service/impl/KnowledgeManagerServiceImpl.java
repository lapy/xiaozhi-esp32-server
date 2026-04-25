package xiaozhi.modules.knowledge.service.impl;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import xiaozhi.modules.knowledge.service.KnowledgeBaseService;
import xiaozhi.modules.knowledge.service.KnowledgeFilesService;
import xiaozhi.modules.knowledge.service.KnowledgeManagerService;

import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class KnowledgeManagerServiceImpl implements KnowledgeManagerService {

    private final KnowledgeBaseService knowledgeBaseService;
    private final KnowledgeFilesService knowledgeFilesService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteDatasetWithFiles(String datasetId) {
        log.info("=== Cascade delete started: datasetId={} ===", datasetId);

        // 1. Clean all documents under the dataset, including remote RAGFlow data.
        log.info("Step 1: Cleaning related documents...");
        knowledgeFilesService.deleteDocumentsByDatasetId(datasetId);

        // 2. Remove the dataset itself, including remote RAGFlow data.
        log.info("Step 2: Deleting the dataset...");
        knowledgeBaseService.deleteByDatasetId(datasetId);

        log.info("=== Cascade delete completed successfully: datasetId={} ===", datasetId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void batchDeleteDatasetsWithFiles(List<String> datasetIds) {
        if (datasetIds == null || datasetIds.isEmpty())
            return;
        log.info("=== Batch cascade delete started: count={} ===", datasetIds.size());
        for (String id : datasetIds) {
            deleteDatasetWithFiles(id);
        }
    }
}
