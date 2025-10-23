package xiaozhi.common.entity;

import java.io.Serializable;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;

import lombok.Data;

/**
 * Base entity class, all entities need to inherit from this
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
@Data
public abstract class BaseEntity implements Serializable {
    /**
     * id
     */
    @TableId
    private Long id;
    /**
     * Creator
     */
    @TableField(fill = FieldFill.INSERT)
    private Long creator;
    /**
     * Creation time
     */
    @TableField(fill = FieldFill.INSERT)
    private Date createDate;
}
