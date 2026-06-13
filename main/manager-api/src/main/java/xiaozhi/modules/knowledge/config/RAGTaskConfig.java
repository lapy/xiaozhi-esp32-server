package xiaozhi.modules.knowledge.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Scheduled-task configuration for the knowledge-base module.
 * Enables Spring scheduling support.
 */
@Configuration
@Profile("!test")
@EnableScheduling
public class RAGTaskConfig {
}
