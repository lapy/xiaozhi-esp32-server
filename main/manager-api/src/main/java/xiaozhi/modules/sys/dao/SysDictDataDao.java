package xiaozhi.modules.sys.dao;

import java.util.List;

import org.apache.ibatis.annotations.Mapper;

import org.apache.ibatis.annotations.Param;
import xiaozhi.common.dao.BaseDao;
import xiaozhi.modules.sys.entity.SysDictDataEntity;
import xiaozhi.modules.sys.vo.SysDictDataItem;

/**
 * Dictionary data
 */
@Mapper
public interface SysDictDataDao extends BaseDao<SysDictDataEntity> {

    List<SysDictDataItem> getDictDataByType(String dictType);

    /**
     * Get dictionary type code based on dictionary type ID
     * 
     * @param dictTypeId Dictionary type ID
     * @return Dictionary type code
     */
    String getTypeByTypeId(Long dictTypeId);

    /**
     * Get dictionary-type codes by dictionary-data ID list.
     */
    List<String> getDictTypesByIdList(@Param("dictDataIdList") List<Long> dictDataIdList);
}
