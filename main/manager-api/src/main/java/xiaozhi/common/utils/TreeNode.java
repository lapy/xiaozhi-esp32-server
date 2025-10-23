package xiaozhi.common.utils;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import lombok.Data;

/**
 * Tree node, all classes that need to implement tree nodes should inherit from this class
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
@Data
public class TreeNode<T> implements Serializable {

    /**
     * Primary key
     */
    private Long id;
    /**
     * Parent ID
     */
    private Long pid;
    /**
     * Child node list
     */
    private List<T> children = new ArrayList<>();

}
