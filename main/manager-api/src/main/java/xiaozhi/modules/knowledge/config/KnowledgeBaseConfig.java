package xiaozhi.modules.knowledge.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import xiaozhi.modules.knowledge.rag.KnowledgeBaseAdapterFactory;

/**
 * Knowledge-base configuration class.
 * Registers beans used by the knowledge-base module.
 */
@Configuration
public class KnowledgeBaseConfig {

    /**
     * Provide the KnowledgeBaseAdapterFactory bean.
     *
     * @return KnowledgeBaseAdapterFactory instance
     */
    @Bean
    public KnowledgeBaseAdapterFactory knowledgeBaseAdapterFactory() {
        return new KnowledgeBaseAdapterFactory();
    }
}
