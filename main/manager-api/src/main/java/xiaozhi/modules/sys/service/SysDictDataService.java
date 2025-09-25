package xiaozhi.modules.sys.service;

import java.util.List;
import java.util.Map;

import xiaozhi.common.page.PageData;
import xiaozhi.common.service.BaseService;
import xiaozhi.modules.sys.dto.SysDictDataDTO;
import xiaozhi.modules.sys.entity.SysDictDataEntity;
import xiaozhi.modules.sys.vo.SysDictDataItem;
import xiaozhi.modules.sys.vo.SysDictDataVO;

/**
 * Data dictionary
 */
public interface SysDictDataService extends BaseService<SysDictDataEntity> {

    /**
     * Paginated query data dictionary information
     *
     * @param params Query parameters, including pagination info and query conditions
     * @return Return paginated query results of data dictionary
     */
    PageData<SysDictDataVO> page(Map<String, Object> params);

    /**
     * Get data dictionary entity by ID
     *
     * @param id Unique identifier of data dictionary entity
     * @return Return detailed information of data dictionary entity
     */
    SysDictDataVO get(Long id);

    /**
     * Save new data dictionary item
     *
     * @param dto Data transfer object for saving data dictionary item
     */
    void save(SysDictDataDTO dto);

    /**
     * Update data dictionary item
     *
     * @param dto Update data transfer object for data dictionary item
     */
    void update(SysDictDataDTO dto);

    /**
     * Delete data dictionary item
     *
     * @param ids Array of IDs of data dictionary items to delete
     */
    void delete(Long[] ids);

    /**
     * Delete corresponding dictionary data based on dictionary type ID
     *
     * @param dictTypeId Dictionary type ID
     */
    void deleteByTypeId(Long dictTypeId);

    /**
     * Get dictionary data list based on dictionary type
     *
     * @param dictType Dictionary type
     * @return Return dictionary data list
     */
    List<SysDictDataItem> getDictDataByType(String dictType);

}