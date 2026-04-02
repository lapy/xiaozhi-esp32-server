package xiaozhi.modules.agent.service.impl;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;

import lombok.RequiredArgsConstructor;
import xiaozhi.common.constant.Constant;
import xiaozhi.modules.agent.dto.AgentChatHistoryDTO;
import xiaozhi.modules.agent.dto.AgentChatSummaryDTO;
import xiaozhi.modules.agent.dto.AgentMemoryDTO;
import xiaozhi.modules.agent.dto.AgentUpdateDTO;
import xiaozhi.modules.agent.entity.AgentChatHistoryEntity;
import xiaozhi.modules.agent.service.AgentChatHistoryService;
import xiaozhi.modules.agent.service.AgentChatSummaryService;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.agent.vo.AgentInfoVO;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.llm.service.LLMService;
import xiaozhi.modules.model.entity.ModelConfigEntity;
import xiaozhi.modules.model.service.ModelConfigService;

/**
 * Agent chat-history summary service implementation.
 * Mirrors the summary logic from the Python mem_local_short.py flow.
 */
@Service
@RequiredArgsConstructor
public class AgentChatSummaryServiceImpl implements AgentChatSummaryService {

    private static final Logger log = LoggerFactory.getLogger(AgentChatSummaryServiceImpl.class);

    private final AgentChatHistoryService agentChatHistoryService;
    private final AgentService agentService;
    private final DeviceService deviceService;
    private final LLMService llmService;
    private final ModelConfigService modelConfigService;

    // Summary rules and limits.
    private static final int MAX_SUMMARY_LENGTH = 1800; // Maximum summary length.
    private static final Pattern JSON_PATTERN = Pattern.compile("\\{.*?\\}", Pattern.DOTALL);
    private static final Pattern DEVICE_CONTROL_PATTERN = Pattern.compile("device control|device operation|control device|device status",
            Pattern.CASE_INSENSITIVE);
    private static final Pattern WEATHER_PATTERN = Pattern.compile("weather|temperature|humidity|rain|forecast", Pattern.CASE_INSENSITIVE);
    private static final Pattern DATE_PATTERN = Pattern.compile("date|time|day of week|month|year", Pattern.CASE_INSENSITIVE);
    private static final String SERVICE_UNAVAILABLE = "Service temporarily unavailable";
    private static final String SUMMARY_GENERATION_FAILED = "Summary generation failed";

    private AgentChatSummaryDTO generateChatSummary(String sessionId) {
        try {
            System.out.println("Starting chat summary generation for session " + sessionId);

            // 1. Load chat history by sessionId.
            List<AgentChatHistoryDTO> chatHistory = getChatHistoryBySessionId(sessionId);
            if (chatHistory == null || chatHistory.isEmpty()) {
                return new AgentChatSummaryDTO(sessionId, "No chat history was found for this session");
            }

            // 2. Resolve the agent information.
            String agentId = getAgentIdFromSession(sessionId, chatHistory);
            if (StringUtils.isBlank(agentId)) {
                return new AgentChatSummaryDTO(sessionId, "Unable to determine the agent information");
            }

            // 3. Extract meaningful conversation content.
            List<String> meaningfulMessages = extractMeaningfulMessages(chatHistory);
            if (meaningfulMessages.isEmpty()) {
                return new AgentChatSummaryDTO(sessionId, "There is no meaningful conversation content to summarize");
            }

            // 4. Generate the summary. Length enforcement happens downstream.
            String summary = generateSummaryFromMessages(meaningfulMessages, agentId);

            log.info("Generated a chat summary for session {} with length {} characters", sessionId, summary.length());
            return new AgentChatSummaryDTO(sessionId, agentId, summary);

        } catch (Exception e) {
            log.error("Failed to generate a chat summary for session {}: {}", sessionId, e.getMessage());
            return new AgentChatSummaryDTO(sessionId, "An error occurred while generating the summary: " + e.getMessage());
        }
    }

    @Override
    public boolean generateAndSaveChatSummary(String sessionId) {
        try {
            // 1. Load the device associated with the session.
            DeviceEntity device = getDeviceBySessionId(sessionId);
            if (device == null) {
                log.info("No device was found for session {}", sessionId);
                return false;
            }

            // 2. Skip summarization when the memory model is report-only.
            String memModelId = agentService.getAgentById(device.getAgentId()).getMemModelId();
            if (memModelId != null && memModelId.equals(Constant.MEMORY_MEM_REPORT_ONLY)) {
                log.info("Session {} uses report-only chat history mode, skipping memory summarization", sessionId);
                return true;
            }

            // 3. Generate the summary.
            AgentChatSummaryDTO summaryDTO = generateChatSummary(sessionId);
            if (!summaryDTO.isSuccess()) {
                log.info("Summary generation failed: {}", summaryDTO.getErrorMessage());
                return false;
            }

            // 4. Update agent memory.
            AgentMemoryDTO memoryDTO = new AgentMemoryDTO();
            memoryDTO.setSummaryMemory(summaryDTO.getSummary());

            // Update memory through the existing agent interface.
            agentService.updateAgentById(device.getAgentId(),
                    new AgentUpdateDTO() {
                        {
                            setSummaryMemory(summaryDTO.getSummary());
                        }
                    });

            log.info("Saved the session {} chat summary to agent {}", sessionId, device.getAgentId());
            return true;

        } catch (Exception e) {
            log.error("Failed to save the chat summary for session {}: {}", sessionId, e.getMessage());
            return false;
        }
    }

    /**
     * Load chat history by session ID.
     */
    private List<AgentChatHistoryDTO> getChatHistoryBySessionId(String sessionId) {
        try {
            // The existing interface requires agentId, so resolve the related agent first.
            String agentId = findAgentIdBySessionId(sessionId);
            if (StringUtils.isBlank(agentId)) {
                return null;
            }
            return agentChatHistoryService.getChatHistoryBySessionId(agentId, sessionId);
        } catch (Exception e) {
            log.error("Failed to load chat history for session {}: {}", sessionId, e.getMessage());
            return null;
        }
    }

    /**
     * Find the agent ID linked to a session ID.
     */
    private String findAgentIdBySessionId(String sessionId) {
        try {
            // Use the first record in the session to resolve the agent ID.
            QueryWrapper<AgentChatHistoryEntity> wrapper = new QueryWrapper<>();
            wrapper.select("agent_id")
                    .eq("session_id", sessionId)
                    .last("LIMIT 1");

            AgentChatHistoryEntity entity = agentChatHistoryService.getOne(wrapper);
            return entity != null ? entity.getAgentId() : null;
        } catch (Exception e) {
            log.error("Failed to find the agent ID for session {}: {}", sessionId, e.getMessage());
            return null;
        }
    }

    /**
     * Get the agent ID for the session.
     */
    private String getAgentIdFromSession(String sessionId, List<AgentChatHistoryDTO> chatHistory) {
        // Resolve the agent ID directly from the database.
        return findAgentIdBySessionId(sessionId);
    }

    /**
     * Extract meaningful conversation content from user messages only.
     */
    private List<String> extractMeaningfulMessages(List<AgentChatHistoryDTO> chatHistory) {
        List<String> meaningfulMessages = new ArrayList<>();

        for (AgentChatHistoryDTO message : chatHistory) {
            // Only process user messages (chatType = 1).
            if (message.getChatType() != null && message.getChatType() == 1) {
                String content = extractContentFromMessage(message);
                if (isMeaningfulMessage(content)) {
                    meaningfulMessages.add(content);
                }
            }
        }

        return meaningfulMessages;
    }

    /**
     * Extract content from a message, including JSON payloads.
     */
    private String extractContentFromMessage(AgentChatHistoryDTO message) {
        String content = message.getContent();
        if (StringUtils.isBlank(content)) {
            return "";
        }

        // Handle JSON-formatted content in a way that stays aligned with ChatHistoryDialog.vue.
        Matcher matcher = JSON_PATTERN.matcher(content);
        if (matcher.find()) {
            String jsonContent = matcher.group();
            // Simplified extraction: pull text content from the JSON body.
            return extractTextFromJson(jsonContent);
        }

        return content;
    }

    /**
     * Extract text content from JSON.
     */
    private String extractTextFromJson(String jsonContent) {
        // Simplified extraction: read the content field.
        Pattern contentPattern = Pattern.compile("\"content\"\s*:\s*\"([^\"]*)\"");
        Matcher matcher = contentPattern.matcher(jsonContent);
        if (matcher.find()) {
            return matcher.group(1);
        }
        return jsonContent;
    }

    /**
     * Determine whether a message is meaningful for summarization.
     */
    private boolean isMeaningfulMessage(String content) {
        if (StringUtils.isBlank(content)) {
            return false;
        }

        // Exclude device-control instructions.
        if (DEVICE_CONTROL_PATTERN.matcher(content).find()) {
            return false;
        }

        // Exclude weather, date, and similar low-value content.
        if (WEATHER_PATTERN.matcher(content).find() || DATE_PATTERN.matcher(content).find()) {
            return false;
        }

        // Exclude overly short messages.
        return content.length() >= 5;
    }

    /**
     * Generate a summary from the extracted messages.
     */
    private String generateSummaryFromMessages(List<String> messages, String agentId) {
        if (messages.isEmpty()) {
            return "This conversation did not contain enough important information to summarize.";
        }

        // Build the full conversation body.
        StringBuilder conversation = new StringBuilder();
        for (int i = 0; i < messages.size(); i++) {
            conversation.append("Message ").append(i + 1).append(": ").append(messages.get(i)).append("\n");
        }

        try {
            // Load current summary memory for the agent.
            String historyMemory = getCurrentAgentMemory(agentId);

            // Call the LLM service and pass agentId so the correct model configuration is used.
            String summary = callJavaLLMForSummaryWithHistory(conversation.toString(), historyMemory, agentId);

            // Apply the maximum summary length rule.
            if (summary.length() > MAX_SUMMARY_LENGTH) {
                summary = summary.substring(0, MAX_SUMMARY_LENGTH) + "...";
            }

            return summary;
        } catch (Exception e) {
            log.error("Java-side LLM summary generation failed: {}", e.getMessage());
            throw new RuntimeException("The LLM service is unavailable, so the chat summary could not be generated");
        }
    }

    /**
     * Load the current summary memory for the agent.
     */
    private String getCurrentAgentMemory(String agentId) {
        try {
            if (StringUtils.isBlank(agentId)) {
                return null;
            }

            // Load agent information.
            AgentInfoVO agentInfo = agentService.getAgentById(agentId);
            if (agentInfo == null) {
                return null;
            }

            // Return the current summary memory for the agent.
            return agentInfo.getSummaryMemory();
        } catch (Exception e) {
            log.error("Failed to load agent history memory, agentId={}, error={}", agentId, e.getMessage());
            return null;
        }
    }

    /**
     * Call the Java-side LLM service to generate a summary with history merging support.
     */
    private String callJavaLLMForSummaryWithHistory(String conversation, String historyMemory, String agentId) {
        try {
            // Load the configured model ID used for memory summarization.
            String modelId = getMemorySummaryModelId(agentId);

            if (StringUtils.isBlank(modelId)) {
                log.info("No dedicated LLM model was found for memory summarization, using the default LLM service");
                return llmService.generateSummaryWithHistory(conversation, historyMemory, null, null);
            }

            // Use the configured model ID and include historical memory in the prompt.
            String summary = llmService.generateSummaryWithHistory(conversation, historyMemory, null, modelId);

            if (StringUtils.isNotBlank(summary)
                    && !summary.equals(SERVICE_UNAVAILABLE)
                    && !summary.equals(SUMMARY_GENERATION_FAILED)) {
                return summary;
            }

            throw new RuntimeException("The Java-side LLM service returned an invalid response: " + summary);

        } catch (Exception e) {
            log.error("Java-side LLM summary call failed, agentId={}, error={}", agentId, e.getMessage());
            throw e;
        }
    }

    /**
     * Call the Java-side LLM service to generate a summary.
     */
    private String callJavaLLMForSummary(String conversation, String agentId) {
        try {
            // Load the configured model ID used for memory summarization.
            String modelId = getMemorySummaryModelId(agentId);

            if (StringUtils.isBlank(modelId)) {
                log.info("No dedicated LLM model was found for memory summarization, using the default LLM service");
                return llmService.generateSummary(conversation);
            }

            // Use the configured model ID.
            String summary = llmService.generateSummaryWithModel(conversation, modelId);

            if (StringUtils.isNotBlank(summary)
                    && !summary.equals(SERVICE_UNAVAILABLE)
                    && !summary.equals(SUMMARY_GENERATION_FAILED)) {
                return summary;
            }

            throw new RuntimeException("The Java-side LLM service returned an invalid response: " + summary);

        } catch (Exception e) {
            log.error("Java-side LLM summary call failed, agentId={}, error={}", agentId, e.getMessage());
            throw e;
        }
    }

    /**
     * Return the LLM model ID used for memory summarization.
     */
    private String getMemorySummaryModelId(String agentId) {
        try {
            if (StringUtils.isBlank(agentId)) {
                return null;
            }

            // Load agent information.
            AgentInfoVO agentInfo = agentService.getAgentById(agentId);
            if (agentInfo == null) {
                return null;
            }

            // Read the agent's memory model ID.
            String memModelId = agentInfo.getMemModelId();
            if (StringUtils.isBlank(memModelId)) {
                return null;
            }

            // Load the memory model configuration.
            ModelConfigEntity memModelConfig = modelConfigService.getModelByIdFromCache(memModelId);
            if (memModelConfig == null || memModelConfig.getConfigJson() == null) {
                return null;
            }

            // Extract the linked LLM model ID from the memory model configuration.
            Map<String, Object> configMap = memModelConfig.getConfigJson();
            String llmModelId = (String) configMap.get("llm");

            if (StringUtils.isBlank(llmModelId)) {
                // Fall back to the agent's default LLM model when the memory model does not specify one.
                return agentInfo.getLlmModelId();
            }

            return llmModelId;
        } catch (Exception e) {
            log.error("Failed to load the memory-summary LLM model ID, agentId={}, error={}",
                    agentId, e.getMessage());
            return null;
        }
    }

    /**
     * Load device information by session ID.
     */
    private DeviceEntity getDeviceBySessionId(String sessionId) {
        try {
            // Use the first session record to resolve the MAC address.
            QueryWrapper<AgentChatHistoryEntity> wrapper = new QueryWrapper<>();
            wrapper.select("mac_address")
                    .eq("session_id", sessionId)
                    .last("LIMIT 1");

            AgentChatHistoryEntity entity = agentChatHistoryService.getOne(wrapper);
            if (entity != null && StringUtils.isNotBlank(entity.getMacAddress())) {
                return deviceService.getDeviceByMacAddress(entity.getMacAddress());
            }
            return null;
        } catch (Exception e) {
            log.error("Failed to load device information for session {}: {}", sessionId, e.getMessage());
            return null;
        }
    }
}
