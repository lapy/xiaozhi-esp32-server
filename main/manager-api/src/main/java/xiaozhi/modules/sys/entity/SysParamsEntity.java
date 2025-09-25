package xiaozhi.modules.sys.entity;

import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;

import lombok.Data;
import lombok.EqualsAndHashCode;
import xiaozhi.common.entity.BaseEntity;

/**
 * Parameter management
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("sys_params")
public class SysParamsEntity extends BaseEntity {
    /**
     * Parameter code
     */
    private String paramCode;
    /**
     * Parameter value
     */
    private String paramValue;
    /**
     * Value type: string-text, number-numeric, boolean-boolean, array-array
     */
    private String valueType;
    /**
     * Type 0: System parameter 1: Non-system parameter
     */
    private Integer paramType;
    /**
     * Remark
     */
    private String remark;
    /**
     * Updater
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updater;
    /**
     * Update time
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Date updateDate;

}