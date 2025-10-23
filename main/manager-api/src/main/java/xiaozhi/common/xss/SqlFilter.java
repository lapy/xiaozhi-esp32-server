package xiaozhi.common.xss;

import org.apache.commons.lang3.StringUtils;

import xiaozhi.common.exception.ErrorCode;
import xiaozhi.common.exception.RenException;

/**
 * SQL filtering
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
public class SqlFilter {

    /**
     * SQL injection filtering
     *
     * @param str String to be validated
     */
    public static String sqlInject(String str) {
        if (StringUtils.isBlank(str)) {
            return null;
        }
        // Remove '|"|;|\ characters
        str = StringUtils.replace(str, "'", "");
        str = StringUtils.replace(str, "\"", "");
        str = StringUtils.replace(str, ";", "");
        str = StringUtils.replace(str, "\\", "");

        // Convert to lowercase
        str = str.toLowerCase();

        // Illegal characters
        String[] keywords = { "master", "truncate", "insert", "select", "delete", "update", "declare", "alter",
                "drop" };

        // Check if contains illegal characters
        for (String keyword : keywords) {
            if (str.contains(keyword)) {
                throw new RenException(ErrorCode.INVALID_SYMBOL);
            }
        }

        return str;
    }
}
