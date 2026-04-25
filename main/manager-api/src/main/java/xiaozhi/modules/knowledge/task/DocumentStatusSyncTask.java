package xiaozhi.modules.knowledge.task;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import xiaozhi.modules.knowledge.service.KnowledgeFilesService;

/**
 * Scheduled task that synchronizes knowledge-base document status.
 *
 * Responsibilities:
 * 1. Scan documents currently in RUNNING state.
 * 2. Query RAGFlow for the latest status.
 * 3. Update the database when status changes from RUNNING to SUCCESS or FAIL.
 * 4. Reconcile knowledge-base statistics such as token count after successful parsing.
 */
@Component
@AllArgsConstructor
@Slf4j
public class DocumentStatusSyncTask {

    private final KnowledgeFilesService knowledgeFilesService;

    /**
     * Run synchronization every 30 seconds.
     * fixedDelay ensures the next run starts 30 seconds after the previous one finishes.
     */
    @Scheduled(fixedDelay = 30000)
    public void syncRunningDocuments() {
        try {
            // log.debug("Starting document-status sync task...");
            knowledgeFilesService.syncRunningDocuments();
        } catch (Exception e) {
            log.error("Document-status sync task failed", e);
        }
    }
}
