package xiaozhi.modules.model.service;

import java.util.List;

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
     * Get model name by ID
     * 
     * @param id Model ID
     * @return Model name
     */
    String getModelNameById(String id);

    /**
     * Get model configuration by ID
     * 
     * @param id      Model ID
     * @param isCache Whether to cache
     * @return Model configuration entity
     */
    ModelConfigEntity getModelById(String id, boolean isCache);

    /**
     * Set default model
     * 
     * @param modelType Model type
     * @param isDefault Whether default
     */
    void setDefaultModel(String modelType, int isDefault);
}
