package xiaozhi.modules.sys.service;

import java.util.List;
import java.util.Map;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.sys.dto.SysParamsDTO;
import xiaozhi.modules.sys.entity.SysParamsEntity;

/**
 * Parameter management
 */
public interface SysParamsService extends BaseService<SysParamsEntity> {

    PageData<SysParamsDTO> page(Map<String, Object> params);

    List<SysParamsDTO> list(Map<String, Object> params);

    SysParamsDTO get(Long id);

    void save(SysParamsDTO dto);

    void update(SysParamsDTO dto);

    void delete(String[] ids);

    /**
     * Get parameter value based on parameter code
     *
     * @param paramCode Parameter code
     * @param fromCache Whether to get from cache
     */
    String getValue(String paramCode, Boolean fromCache);

    /**
     * Get Object object of value based on parameter code
     *
     * @param paramCode Parameter code
     * @param clazz     Object class
     */
    <T> T getValueObject(String paramCode, Class<T> clazz);

    /**
     * Update value based on parameter code
     *
     * @param paramCode  Parameter code
     * @param paramValue Parameter value
     */
    int updateValueByCode(String paramCode, String paramValue);

    /**
     * Initialize server secret key
     */
    void initServerSecret();

    /**
     * 获取系统功能菜单配置
     *
     * @param fromCache 是否从缓存获取
     * @return 系统功能菜单配置JSON字符串
     */
    String getSystemWebMenu(boolean fromCache);

    /**
     * 更新系统功能菜单配置（自动处理功能相关的插件清理）
     *
     * @param configJson 新的系统功能菜单配置JSON
     */
    void updateSystemWebMenu(String configJson);
}
