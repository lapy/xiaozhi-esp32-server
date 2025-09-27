package xiaozhi.modules.model.service.impl;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.metadata.OrderItem; 
import com.baomidou.mybatisplus.extension.plugins.pagination.Page; 

import cn.hutool.core.collection.CollectionUtil;
import lombok.AllArgsConstructor;
import xiaozhi.common.constant.Constant;
import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;
import xiaozhi.common.page.PageData;
import xiaozhi.common.redis.RedisKeys;
import xiaozhi.common.redis.RedisUtils;
import xiaozhi.common.service.impl.BaseServiceImpl;
import xiaozhi.common.utils.ConvertUtils;
import xiaozhi.modules.agent.dao.AgentDao;
import xiaozhi.modules.agent.entity.AgentEntity;
import xiaozhi.modules.model.dao.ModelConfigDao;
import xiaozhi.modules.model.dto.LlmModelBasicInfoDTO;
import xiaozhi.modules.model.dto.ModelBasicInfoDTO;
import xiaozhi.modules.model.dto.ModelConfigBodyDTO;
import xiaozhi.modules.model.dto.ModelConfigDTO;
import xiaozhi.modules.model.dto.ModelProviderDTO;
import xiaozhi.modules.model.entity.ModelConfigEntity;
import xiaozhi.modules.model.service.ModelConfigService;
import xiaozhi.modules.model.service.ModelProviderService;

@Service
@AllArgsConstructor
public class ModelConfigServiceImpl extends BaseServiceImpl<ModelConfigDao, ModelConfigEntity>
        implements ModelConfigService {

    private final ModelConfigDao modelConfigDao;
    private final ModelProviderService modelProviderService;
    private final RedisUtils redisUtils;
    private final AgentDao agentDao;

    @Override
    public List<ModelBasicInfoDTO> getModelCodeList(String modelType, String modelName) {
        List<ModelConfigEntity> entities = modelConfigDao.selectList(
                new QueryWrapper<ModelConfigEntity>()
                        .eq("model_type", modelType)
                        .eq("is_enabled", 1)
                        .like(StringUtils.isNotBlank(modelName), "model_name", "%" + modelName + "%")
                        .select("id", "model_name"));
        return ConvertUtils.sourceToTarget(entities, ModelBasicInfoDTO.class);
    }

    @Override
    public List<LlmModelBasicInfoDTO> getLlmModelCodeList(String modelName) {
        List<ModelConfigEntity> entities = modelConfigDao.selectList(
                new QueryWrapper<ModelConfigEntity>()
                        .eq("model_type", "llm")
                        .eq("is_enabled", 1)
                        .like(StringUtils.isNotBlank(modelName), "model_name", "%" + modelName + "%")
                        .select("id", "model_name", "config_json"));
        // Process retrieved content
        return entities.stream().map(item -> {
            LlmModelBasicInfoDTO dto = new LlmModelBasicInfoDTO();
            dto.setId(item.getId());
            dto.setModelName(item.getModelName());
            String type = item.getConfigJson().get("type").toString();
            dto.setType(type);
            return dto;
        }).toList();
    }

    @Override
    public PageData<ModelConfigDTO> getPageList(String modelType, String modelName, String page, String limit) {
        Map<String, Object> params = new HashMap<String, Object>();
        params.put(Constant.PAGE, page);
        params.put(Constant.LIMIT, limit);
        
        // No longer use default getPage method, directly create Page object and customize sorting
        long curPage = Long.parseLong(page);
        long pageSize = Long.parseLong(limit);
        Page<ModelConfigEntity> pageInfo = new Page<>(curPage, pageSize);
        
        // Add sorting rules: first by is_enabled descending, then by sort ascending
        pageInfo.addOrder(OrderItem.desc("is_enabled"));
        pageInfo.addOrder(OrderItem.asc("sort"));
        
        // Execute pagination query
        IPage<ModelConfigEntity> modelConfigEntityIPage = modelConfigDao.selectPage(
                pageInfo,
                new QueryWrapper<ModelConfigEntity>()
                        .eq("model_type", modelType)
                        .like(StringUtils.isNotBlank(modelName), "model_name", "%" + modelName + "%"));
        
        return getPageData(modelConfigEntityIPage, ModelConfigDTO.class);
    }

    @Override
    public ModelConfigDTO add(String modelType, String provideCode, ModelConfigBodyDTO modelConfigBodyDTO) {
        // First verify if provider exists
        if (StringUtils.isBlank(modelType) || StringUtils.isBlank(provideCode)) {
            throw new RenException(ErrorCode.MODEL_TYPE_PROVIDE_CODE_NOT_NULL);
        }
        List<ModelProviderDTO> providerList = modelProviderService.getList(modelType, provideCode);
        if (CollectionUtil.isEmpty(providerList)) {
            throw new RenException(ErrorCode.MODEL_PROVIDER_NOT_EXIST);
        }

        // Then save the model provided by the provider
        ModelConfigEntity modelConfigEntity = ConvertUtils.sourceToTarget(modelConfigBodyDTO, ModelConfigEntity.class);
        modelConfigEntity.setModelType(modelType);
        modelConfigEntity.setIsDefault(0);
        modelConfigDao.insert(modelConfigEntity);
        return ConvertUtils.sourceToTarget(modelConfigEntity, ModelConfigDTO.class);
    }

    @Override
    public ModelConfigDTO edit(String modelType, String provideCode, String id, ModelConfigBodyDTO modelConfigBodyDTO) {
        // First verify if provider exists
        if (StringUtils.isBlank(modelType) || StringUtils.isBlank(provideCode)) {
            throw new RenException(ErrorCode.MODEL_TYPE_PROVIDE_CODE_NOT_NULL);
        }
        List<ModelProviderDTO> providerList = modelProviderService.getList(modelType, provideCode);
        if (CollectionUtil.isEmpty(providerList)) {
            throw new RenException(ErrorCode.MODEL_PROVIDER_NOT_EXIST);
        }
        if (modelConfigBodyDTO.getConfigJson().containsKey("llm")) {
            String llm = modelConfigBodyDTO.getConfigJson().get("llm").toString();
            ModelConfigEntity modelConfigEntity = modelConfigDao.selectOne(new LambdaQueryWrapper<ModelConfigEntity>()
                    .eq(ModelConfigEntity::getId, llm));
            String selectModelType = (modelConfigEntity == null || modelConfigEntity.getModelType() == null) ? null
                    : modelConfigEntity.getModelType().toUpperCase();
            if (modelConfigEntity == null || !"LLM".equals(selectModelType)) {
                throw new RenException(ErrorCode.LLM_NOT_EXIST);
            }
            String type = modelConfigEntity.getConfigJson().get("type").toString();
            // If the queried large language model is openai, ollama, or gemini, intent recognition parameters can be selected
            if (!"openai".equals(type) && !"ollama".equals(type) && !"gemini".equals(type)) {
                throw new RenException(ErrorCode.INVALID_LLM_TYPE);
            }
        }

        // Then update the model provided by the provider
        ModelConfigEntity modelConfigEntity = ConvertUtils.sourceToTarget(modelConfigBodyDTO, ModelConfigEntity.class);
        modelConfigEntity.setId(id);
        modelConfigEntity.setModelType(modelType);
        modelConfigDao.updateById(modelConfigEntity);
        // Clear cache
        redisUtils.delete(RedisKeys.getModelConfigById(modelConfigEntity.getId()));
        return ConvertUtils.sourceToTarget(modelConfigEntity, ModelConfigDTO.class);
    }

    @Override
    public void delete(String id) {
        // Check if it is default
        ModelConfigEntity modelConfig = modelConfigDao.selectById(id);
        if (modelConfig != null && modelConfig.getIsDefault() == 1) {
            throw new RenException(ErrorCode.DEFAULT_MODEL_DELETE_ERROR);
        }
        // Verify if there are references
        checkAgentReference(id);
        checkIntentConfigReference(id);

        modelConfigDao.deleteById(id);
    }

    /**
     * Check if agent configuration has references
     * 
     * @param modelId Model ID
     */
    private void checkAgentReference(String modelId) {
        List<AgentEntity> agents = agentDao.selectList(
                new QueryWrapper<AgentEntity>()
                        .eq("vad_model_id", modelId)
                        .or()
                        .eq("asr_model_id", modelId)
                        .or()
                        .eq("llm_model_id", modelId)
                        .or()
                        .eq("tts_model_id", modelId)
                        .or()
                        .eq("mem_model_id", modelId)
                        .or()
                        .eq("vllm_model_id", modelId)
                        .or()
                        .eq("intent_model_id", modelId));
        if (!agents.isEmpty()) {
            String agentNames = agents.stream()
                    .map(AgentEntity::getAgentName)
                    .collect(Collectors.joining("、"));
            throw new RenException(ErrorCode.MODEL_REFERENCED_BY_AGENT, agentNames);
        }
    }

    /**
     * Check if intent recognition configuration has references
     * 
     * @param modelId Model ID
     */
    private void checkIntentConfigReference(String modelId) {
        ModelConfigEntity modelConfig = modelConfigDao.selectById(modelId);
        if (modelConfig != null
                && "LLM".equals(modelConfig.getModelType() == null ? null : modelConfig.getModelType().toUpperCase())) {
            List<ModelConfigEntity> intentConfigs = modelConfigDao.selectList(
                    new QueryWrapper<ModelConfigEntity>()
                            .eq("model_type", "Intent")
                            .like("config_json", "%" + modelId + "%"));
            if (!intentConfigs.isEmpty()) {
                throw new RenException(ErrorCode.LLM_REFERENCED_BY_INTENT);
            }
        }
    }

    @Override
    public String getModelNameById(String id) {
        if (StringUtils.isBlank(id)) {
            return null;
        }

        String cachedName = (String) redisUtils.get(RedisKeys.getModelNameById(id));

        if (StringUtils.isNotBlank(cachedName)) {
            return cachedName;
        }

        ModelConfigEntity entity = modelConfigDao.selectById(id);
        if (entity != null) {
            String modelName = entity.getModelName();
            if (StringUtils.isNotBlank(modelName)) {
                redisUtils.set(RedisKeys.getModelNameById(id), modelName);
            }
            return modelName;
        }

        return null;
    }

    @Override
    public ModelConfigEntity getModelById(String id, boolean isCache) {
        if (StringUtils.isBlank(id)) {
            return null;
        }
        if (isCache) {
            ModelConfigEntity cachedConfig = (ModelConfigEntity) redisUtils.get(RedisKeys.getModelConfigById(id));
            if (cachedConfig != null) {
                return ConvertUtils.sourceToTarget(cachedConfig, ModelConfigEntity.class);
            }
        }
        ModelConfigEntity entity = modelConfigDao.selectById(id);
        if (entity != null) {
            redisUtils.set(RedisKeys.getModelConfigById(id), entity);
        }
        return entity;
    }

    @Override
    public void setDefaultModel(String modelType, int isDefault) {
        ModelConfigEntity entity = new ModelConfigEntity();
        entity.setIsDefault(isDefault);
        modelConfigDao.update(entity, new QueryWrapper<ModelConfigEntity>()
                .eq("model_type", modelType));
    }
}
