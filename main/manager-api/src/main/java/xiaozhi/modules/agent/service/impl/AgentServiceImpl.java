package xiaozhi.modules.agent.service.impl;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;

import lombok.AllArgsConstructor;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.page.PageData;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.service.impl.BaseServiceImpl;
import xiaozhi.common.user.UserDetail;
import xiaozhi.common.utils.ConvertUtils;
import xiaozhi.common.utils.JsonUtils;
import xiaozhi.common.utils.ToolUtil;
import xiaozhi.modules.agent.dao.AgentDao;
import xiaozhi.modules.agent.dao.AgentTagDao;
import xiaozhi.modules.agent.dto.AgentCreateDTO;
import xiaozhi.modules.agent.dto.AgentDTO;
import xiaozhi.modules.agent.dto.AgentTagDTO;
import xiaozhi.modules.agent.dto.AgentUpdateDTO;
import xiaozhi.modules.agent.entity.AgentContextProviderEntity;
import xiaozhi.modules.agent.entity.AgentEntity;
import xiaozhi.modules.agent.entity.AgentPluginMapping;
import xiaozhi.modules.agent.entity.AgentTagEntity;
import xiaozhi.modules.agent.entity.AgentTemplateEntity;
import xiaozhi.modules.agent.service.AgentChatHistoryService;
import xiaozhi.modules.agent.service.AgentContextProviderService;
import xiaozhi.modules.agent.service.AgentPluginMappingService;
import xiaozhi.modules.agent.service.AgentService;
import xiaozhi.modules.agent.service.AgentTagService;
import xiaozhi.modules.agent.service.AgentTemplateService;
import xiaozhi.modules.agent.vo.AgentInfoVO;
import xiaozhi.modules.device.entity.DeviceEntity;
import xiaozhi.modules.device.service.DeviceService;
import xiaozhi.modules.model.dto.ModelProviderDTO;
import xiaozhi.modules.model.dto.VoiceDTO;
import xiaozhi.modules.model.entity.ModelConfigEntity;
import xiaozhi.modules.model.service.ModelConfigService;
import xiaozhi.modules.model.service.ModelProviderService;
import xiaozhi.modules.security.user.SecurityUser;
import xiaozhi.modules.sys.enums.SuperAdminEnum;
import xiaozhi.modules.timbre.service.TimbreService;

@Service
@AllArgsConstructor
public class AgentServiceImpl extends BaseServiceImpl<AgentDao, AgentEntity> implements AgentService {
    private final AgentDao agentDao;
    private final AgentTagDao agentTagDao;
    private final TimbreService timbreModelService;
    private final ModelConfigService modelConfigService;
    private final RedisUtils redisUtils;
    private final DeviceService deviceService;
    private final AgentPluginMappingService agentPluginMappingService;
    private final AgentChatHistoryService agentChatHistoryService;
    private final AgentTemplateService agentTemplateService;
    private final ModelProviderService modelProviderService;
    private final AgentContextProviderService agentContextProviderService;
    private final AgentTagService agentTagService;

    @Override
    public PageData<AgentEntity> adminAgentList(Map<String, Object> params) {
        IPage<AgentEntity> page = agentDao.selectPage(
                getPage(params, "agent_name", true),
                new QueryWrapper<>());
        return new PageData<>(page.getRecords(), page.getTotal());
    }

    @Override
    public AgentInfoVO getAgentById(String id) {
        AgentInfoVO agent = agentDao.selectAgentInfoById(id);

        if (agent == null) {
            throw new RenException(ErrorCode.AGENT_NOT_FOUND);
        }

        if (agent.getMemModelId() != null && agent.getMemModelId().equals(Constant.MEMORY_NO_MEM)) {
            agent.setChatHistoryConf(Constant.ChatHistoryConfEnum.IGNORE.getCode());
        }
        if (agent.getChatHistoryConf() == null) {
            agent.setChatHistoryConf(Constant.ChatHistoryConfEnum.RECORD_TEXT_AUDIO.getCode());
        }

        // Load context-provider configuration.
        AgentContextProviderEntity contextProviderEntity = agentContextProviderService.getByAgentId(id);
        if (contextProviderEntity != null) {
            agent.setContextProviders(contextProviderEntity.getContextProviders());
        }

        // Plugin data is already loaded through SQL and does not need an extra query.
        return agent;
    }

    @Override
    public boolean insert(AgentEntity entity) {
        // Auto-generate a UUID when the ID is empty.
        if (entity.getId() == null || entity.getId().trim().isEmpty()) {
            entity.setId(UUID.randomUUID().toString().replace("-", ""));
        }

        // Auto-generate an agent code with a prefix when missing.
        if (entity.getAgentCode() == null || entity.getAgentCode().trim().isEmpty()) {
            entity.setAgentCode("AGT_" + System.currentTimeMillis());
        }

        // Default the sort field to 0 when it is empty.
        if (entity.getSort() == null) {
            entity.setSort(0);
        }

        return super.insert(entity);
    }

    @Override
    public void deleteAgentByUserId(Long userId) {
        UpdateWrapper<AgentEntity> wrapper = new UpdateWrapper<>();
        wrapper.eq("user_id", userId);
        baseDao.delete(wrapper);
    }

    @Override
    public List<AgentDTO> getUserAgents(Long userId, String keyword, String searchType) {
        QueryWrapper<AgentEntity> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_id", userId).orderByDesc("created_at");

        // Apply keyword filtering based on the selected search type.
        if (StringUtils.isNotBlank(keyword)) {
            if ("mac".equals(searchType)) {
                // Search by MAC address: find devices first, then resolve their agents.
                List<DeviceEntity> devices = Optional
                        .ofNullable(deviceService.searchDevicesByMacAddress(keyword, userId)).orElseGet(ArrayList::new);
                // Collect the agent IDs linked to those devices.
                List<String> agentIds = devices.stream()
                        .map(DeviceEntity::getAgentId)
                        .distinct()
                        .collect(Collectors.toList());
                if (ToolUtil.isNotEmpty(agentIds)) {
                    queryWrapper.in("id", agentIds);
                } else {
                    return new ArrayList<>();
                }
            } else {
                // Default name search: match both agent names and tag names.
                List<String> tagAgentIds = agentTagService.getAgentIdsByTagName(keyword);
                if (ToolUtil.isNotEmpty(tagAgentIds)) {
                    queryWrapper.and(wrapper -> wrapper
                            .like("agent_name", keyword)
                            .or()
                            .in("id", tagAgentIds));
                } else {
                    queryWrapper.like("agent_name", keyword);
                }
            }
        }

        // Run the query.
        List<AgentEntity> agentEntities = baseDao.selectList(queryWrapper);

        // Convert to DTOs and populate the required fields.
        return agentEntities.stream().map(this::buildAgentDTO).collect(Collectors.toList());
    }

    /**
     * Convert AgentEntity to AgentDTO.
     */
    private AgentDTO buildAgentDTO(AgentEntity agent) {
        AgentDTO dto = new AgentDTO();
        dto.setId(agent.getId());
        dto.setAgentName(agent.getAgentName());
        dto.setSystemPrompt(agent.getSystemPrompt());

        // Load the TTS model name.
        dto.setTtsModelName(modelConfigService.getModelNameById(agent.getTtsModelId()));

        // Load the LLM model name.
        dto.setLlmModelName(modelConfigService.getModelNameById(agent.getLlmModelId()));

        // Load the VLLM model name.
        dto.setVllmModelName(modelConfigService.getModelNameById(agent.getVllmModelId()));

        // Keep the memory model identifier.
        dto.setMemModelId(agent.getMemModelId());

        // Load the TTS voice name.
        dto.setTtsVoiceName(timbreModelService.getTimbreNameById(agent.getTtsVoiceId()));

        // Load the agent's most recent device connection time.
        dto.setLastConnectedAt(deviceService.getLatestLastConnectionTime(agent.getId()));

        // Load the device count.
        dto.setDeviceCount(getDeviceCountByAgentId(agent.getId()));

        // Load the tag list.
        List<AgentTagEntity> tags = agentTagDao.selectByAgentId(agent.getId());
        if (ToolUtil.isNotEmpty(tags)) {
            dto.setTags(tags.stream().map(this::convertTagToDTO).collect(Collectors.toList()));
        }

        return dto;
    }

    private AgentTagDTO convertTagToDTO(AgentTagEntity entity) {
        AgentTagDTO dto = new AgentTagDTO();
        dto.setId(entity.getId());
        dto.setTagName(entity.getTagName());
        return dto;
    }

    @Override
    public Integer getDeviceCountByAgentId(String agentId) {
        if (StringUtils.isBlank(agentId)) {
            return 0;
        }

        // Check Redis first.
        Integer cachedCount = (Integer) redisUtils.get(RedisKeys.getAgentDeviceCountById(agentId));
        if (cachedCount != null) {
            return cachedCount;
        }

        // Fall back to the database if Redis has no cached value.
        Integer deviceCount = agentDao.getDeviceCountByAgentId(agentId);

        // Cache the result in Redis.
        if (deviceCount != null) {
            redisUtils.set(RedisKeys.getAgentDeviceCountById(agentId), deviceCount, 60);
        }

        return deviceCount != null ? deviceCount : 0;
    }

    @Override
    public AgentEntity getDefaultAgentByMacAddress(String macAddress) {
        if (StringUtils.isEmpty(macAddress)) {
            return null;
        }
        return agentDao.getDefaultAgentByMacAddress(macAddress);
    }

    @Override
    public boolean checkAgentPermission(String agentId, Long userId) {
        if (SecurityUser.getUser() == null || SecurityUser.getUser().getId() == null) {
            return false;
        }
        // Load agent information.
        AgentEntity agent = getAgentById(agentId);
        if (agent == null) {
            return false;
        }

        // Super admins always have access.
        if (SecurityUser.getUser().getSuperAdmin() == SuperAdminEnum.YES.value()) {
            return true;
        }

        // Otherwise the caller must own the agent.
        return userId.equals(agent.getUserId());
    }

    // Update agent information by ID.
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateAgentById(String agentId, AgentUpdateDTO dto) {
        // Load the existing entity first.
        AgentEntity existingEntity = this.getAgentById(agentId);
        if (existingEntity == null) {
            throw new RenException(ErrorCode.AGENT_NOT_FOUND);
        }

        // Only update non-null fields from the request.
        if (dto.getAgentName() != null) {
            existingEntity.setAgentName(dto.getAgentName());
        }
        if (dto.getAgentCode() != null) {
            existingEntity.setAgentCode(dto.getAgentCode());
        }
        if (dto.getAsrModelId() != null) {
            existingEntity.setAsrModelId(dto.getAsrModelId());
        }
        if (dto.getVadModelId() != null) {
            existingEntity.setVadModelId(dto.getVadModelId());
        }
        if (dto.getLlmModelId() != null) {
            existingEntity.setLlmModelId(dto.getLlmModelId());
        }
        if (dto.getSlmModelId() != null) {
            existingEntity.setSlmModelId(dto.getSlmModelId());
        }
        if (dto.getVllmModelId() != null) {
            existingEntity.setVllmModelId(dto.getVllmModelId());
        }
        if (dto.getTtsModelId() != null) {
            existingEntity.setTtsModelId(dto.getTtsModelId());
        }
        if (dto.getTtsVoiceId() != null) {
            existingEntity.setTtsVoiceId(dto.getTtsVoiceId());
        }
        if (dto.getTtsLanguage() != null) {
            existingEntity.setTtsLanguage(dto.getTtsLanguage());
        }
        if (dto.getTtsVolume() != null) {
            existingEntity.setTtsVolume(dto.getTtsVolume());
        }
        if (dto.getTtsRate() != null) {
            existingEntity.setTtsRate(dto.getTtsRate());
        }
        if (dto.getTtsPitch() != null) {
            existingEntity.setTtsPitch(dto.getTtsPitch());
        }
        if (dto.getMemModelId() != null) {
            existingEntity.setMemModelId(dto.getMemModelId());
        }
        if (dto.getIntentModelId() != null) {
            existingEntity.setIntentModelId(dto.getIntentModelId());
        }
        if (dto.getSystemPrompt() != null) {
            existingEntity.setSystemPrompt(dto.getSystemPrompt());
        }
        if (dto.getSummaryMemory() != null) {
            existingEntity.setSummaryMemory(dto.getSummaryMemory());
        }
        if (dto.getChatHistoryConf() != null) {
            existingEntity.setChatHistoryConf(dto.getChatHistoryConf());
        }
        if (dto.getLangCode() != null) {
            existingEntity.setLangCode(dto.getLangCode());
        }
        if (dto.getLanguage() != null) {
            existingEntity.setLanguage(dto.getLanguage());
        }
        if (dto.getSort() != null) {
            existingEntity.setSort(dto.getSort());
        }

        // Update function-plugin mappings.
        List<AgentUpdateDTO.FunctionInfo> functions = dto.getFunctions();
        if (functions != null) {
            // 1. Collect submitted plugin IDs.
            List<String> newPluginIds = functions.stream()
                    .map(AgentUpdateDTO.FunctionInfo::getPluginId)
                    .toList();

            // 2. Load all current mappings for this agent.
            List<AgentPluginMapping> existing = agentPluginMappingService.list(
                    new QueryWrapper<AgentPluginMapping>()
                            .eq("agent_id", agentId));
            Map<String, AgentPluginMapping> existMap = existing.stream()
                    .collect(Collectors.toMap(AgentPluginMapping::getPluginId, Function.identity()));

            // 3. Build entities to save or update.
            List<AgentPluginMapping> allToPersist = functions.stream().map(info -> {
                AgentPluginMapping m = new AgentPluginMapping();
                m.setAgentId(agentId);
                m.setPluginId(info.getPluginId());
                m.setParamInfo(JsonUtils.toJsonString(info.getParamInfo()));
                AgentPluginMapping old = existMap.get(info.getPluginId());
                if (old != null) {
                    // Existing mappings carry their ID so they are updated instead of inserted.
                    m.setId(old.getId());
                }
                return m;
            }).toList();

            // 4. Split the set into updates and inserts.
            List<AgentPluginMapping> toUpdate = allToPersist.stream()
                    .filter(m -> m.getId() != null)
                    .toList();
            List<AgentPluginMapping> toInsert = allToPersist.stream()
                    .filter(m -> m.getId() == null)
                    .toList();

            if (!toUpdate.isEmpty()) {
                agentPluginMappingService.updateBatchById(toUpdate);
            }
            if (!toInsert.isEmpty()) {
                agentPluginMappingService.saveBatch(toInsert);
            }

            // 5. Remove plugin mappings that are no longer part of the submission.
            List<Long> toDelete = existing.stream()
                    .filter(old -> !newPluginIds.contains(old.getPluginId()))
                    .map(AgentPluginMapping::getId)
                    .toList();
            if (!toDelete.isEmpty()) {
                agentPluginMappingService.removeBatchByIds(toDelete);
            }
        }

        // Set updater metadata.
        UserDetail user = SecurityUser.getUser();
        existingEntity.setUpdater(user.getId());
        existingEntity.setUpdatedAt(new Date());

        // Apply the memory-strategy cleanup rules.
        // Delete all history when memory is disabled or report-only.
        if (existingEntity.getMemModelId() == null || existingEntity.getMemModelId().equals(Constant.MEMORY_NO_MEM)
                || existingEntity.getMemModelId().equals(Constant.MEMORY_MEM_REPORT_ONLY)) {
            agentChatHistoryService.deleteByAgentId(existingEntity.getId(), true, true);
            existingEntity.setSummaryMemory("");
        } else if (existingEntity.getChatHistoryConf() != null && existingEntity.getChatHistoryConf() == 1) {
            // Delete audio data only.
            agentChatHistoryService.deleteByAgentId(existingEntity.getId(), true, false);
        }

        // Update context-provider configuration.
        if (dto.getContextProviders() != null) {
            AgentContextProviderEntity contextEntity = new AgentContextProviderEntity();
            contextEntity.setAgentId(agentId);
            contextEntity.setContextProviders(dto.getContextProviders());
            agentContextProviderService.saveOrUpdateByAgentId(contextEntity);
        }

        boolean b = validateLLMIntentParams(dto.getLlmModelId(), dto.getIntentModelId());
        if (!b) {
            throw new RenException(ErrorCode.LLM_INTENT_PARAMS_MISMATCH);
        }
        this.updateById(existingEntity);
    }

    /**
     * Validate whether the LLM and intent-recognition parameters are compatible.
     *
     * @param llmModelId LLM model ID
     * @param intentModelId intent-recognition model ID
     * @return true when compatible, false otherwise
     */
    private boolean validateLLMIntentParams(String llmModelId, String intentModelId) {
        if (StringUtils.isBlank(llmModelId)) {
            return true;
        }
        ModelConfigEntity llmModelData = modelConfigService.selectById(llmModelId);
        String type = llmModelData.getConfigJson().get("type").toString();
        // OpenAI and Ollama can work with any intent-recognition selection.
        if ("openai".equals(type) || "ollama".equals(type)) {
            return true;
        }
        // Other model types cannot use the Intent_function_call intent option.
        return !"Intent_function_call".equals(intentModelId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public String createAgent(AgentCreateDTO dto) {
        // Convert the request to an entity.
        AgentEntity entity = ConvertUtils.sourceToTarget(dto, AgentEntity.class);

        // Load the default template.
        AgentTemplateEntity template = agentTemplateService.getDefaultTemplate();
        if (template != null) {
            // Apply template defaults.
            entity.setAsrModelId(template.getAsrModelId());
            entity.setVadModelId(template.getVadModelId());
            entity.setLlmModelId(template.getLlmModelId());
            entity.setVllmModelId(template.getVllmModelId());
            entity.setTtsModelId(template.getTtsModelId());

            if (template.getTtsVoiceId() == null && template.getTtsModelId() != null) {
                ModelConfigEntity ttsModel = modelConfigService.selectById(template.getTtsModelId());
                if (ttsModel != null && ttsModel.getConfigJson() != null) {
                    Map<String, Object> config = ttsModel.getConfigJson();
                    String voice = (String) config.get("voice");
                    if (StringUtils.isBlank(voice)) {
                        voice = (String) config.get("speaker");
                    }
                    VoiceDTO timbre = timbreModelService.getByVoiceCode(template.getTtsModelId(), voice);
                    if (timbre != null) {
                        template.setTtsVoiceId(timbre.getId());
                    }
                }
            }

            entity.setTtsVoiceId(template.getTtsVoiceId());
            entity.setMemModelId(template.getMemModelId());
            entity.setIntentModelId(template.getIntentModelId());
            entity.setSystemPrompt(template.getSystemPrompt());
            entity.setSummaryMemory(template.getSummaryMemory());

            // Set the default chatHistoryConf based on the memory model type.
            if (template.getMemModelId() != null) {
                if (template.getMemModelId().equals("Memory_nomem")) {
                    // Models without memory do not record chat history by default.
                    entity.setChatHistoryConf(0);
                } else {
                    // Models with memory record both text and audio by default.
                    entity.setChatHistoryConf(2);
                }
            } else {
                entity.setChatHistoryConf(template.getChatHistoryConf());
            }

            entity.setLangCode(template.getLangCode());
            entity.setLanguage(template.getLanguage());
        }

        if (entity.getSlmModelId() == null) {
            String defaultSlmModelId = getDefaultLLMModelId();
            if (defaultSlmModelId != null) {
                entity.setSlmModelId(defaultSlmModelId);
            }
        }

        // Set owner and creator metadata.
        UserDetail user = SecurityUser.getUser();
        entity.setUserId(user.getId());
        entity.setCreator(user.getId());
        entity.setCreatedAt(new Date());

        // Save the agent.
        insert(entity);

        // Set default plugins.
        List<AgentPluginMapping> toInsert = new ArrayList<>();
        // Music playback, weather lookup, and news lookup.
        String[] pluginIds = new String[] { "SYSTEM_PLUGIN_MUSIC", "SYSTEM_PLUGIN_WEATHER",
                "SYSTEM_PLUGIN_NEWS_NEWSNOW" };
        for (String pluginId : pluginIds) {
            ModelProviderDTO provider = modelProviderService.getById(pluginId);
            if (provider == null) {
                continue;
            }
            AgentPluginMapping mapping = new AgentPluginMapping();
            mapping.setPluginId(pluginId);

            Map<String, Object> paramInfo = new HashMap<>();
            List<Map<String, Object>> fields = JsonUtils.parseObject(provider.getFields(), List.class);
            if (fields != null) {
                for (Map<String, Object> field : fields) {
                    paramInfo.put((String) field.get("key"), field.get("default"));
                }
            }
            mapping.setParamInfo(JsonUtils.toJsonString(paramInfo));
            mapping.setAgentId(entity.getId());
            toInsert.add(mapping);
        }
        // Save the default plugins.
        agentPluginMappingService.saveBatch(toInsert);
        return entity.getId();
    }

    private String getDefaultLLMModelId() {
        try {
            List<ModelConfigEntity> llmConfigs = modelConfigService.getEnabledModelsByType("LLM");
            if (llmConfigs == null || llmConfigs.isEmpty()) {
                return null;
            }

            for (ModelConfigEntity config : llmConfigs) {
                if (config.getIsDefault() != null && config.getIsDefault() == 1) {
                    return config.getId();
                }
            }

            return llmConfigs.get(0).getId();
        } catch (Exception e) {
            return null;
        }
    }

}
