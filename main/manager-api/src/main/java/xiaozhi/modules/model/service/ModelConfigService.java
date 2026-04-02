package xiaozhi.modules.model.service;

import java.util.List;
import java.util.Map;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.model.dto.LlmModelBasicInfoDTO;
import xiaozhi.modules.model.dto.ModelBasicInfoDTO;
import xiaozhi.modules.model.dto.ModelConfigBodyDTO;
import xiaozhi.modules.model.dto.ModelConfigDTO;
import xiaozhi.modules.model.entity.ModelConfigEntity;

public interface ModelConfigService extends BaseService<ModelConfigEntity> {

    List<ModelBasicInfoDTO> getModelCodeList(String modelType, String modelName);

    List<LlmModelBasicInfoDTO> getLlmModelCodeList(String modelName);

    PageData<ModelConfigDTO> getPageList(String modelType, String modelName, String page, String limit);

    ModelConfigDTO add(String modelType, String provideCode, ModelConfigBodyDTO modelConfigBodyDTO);

    ModelConfigDTO edit(String modelType, String provideCode, String id, ModelConfigBodyDTO modelConfigBodyDTO);

    void delete(String id);

    /**
     * Get a model name by ID.
     *
     * @param id model ID
     * @return model name
     */
    String getModelNameById(String id);

    /**
     * Get a model configuration by ID from cache.
     *
     * @param id model ID
     * @return model configuration entity
     */
    ModelConfigEntity getModelByIdFromCache(String id);

    /**
     * Set the default model.
     *
     * @param modelType model type
     * @param isDefault whether it is the default model, 1 for yes and 0 for no
     */
    void setDefaultModel(String modelType, int isDefault);

    /**
     * Get the list of matching TTS platforms.
     *
     * @return TTS platform list containing id and modelName
     */
    List<Map<String, Object>> getTtsPlatformList();

    /**
     * Get all enabled model configurations for a model type.
     *
     * @param modelType model type such as LLM, TTS, or ASR
     * @return enabled model configuration list
     */
    List<ModelConfigEntity> getEnabledModelsByType(String modelType);
}
