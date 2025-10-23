package xiaozhi.common.utils;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.Date;

/**
 * Date processing
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
public class DateUtils {
    /**
     * Time format (yyyy-MM-dd)
     */
    public final static String DATE_PATTERN = "yyyy-MM-dd";
    /**
     * Time format (yyyy-MM-dd HH:mm:ss)
     */
    public final static String DATE_TIME_PATTERN = "yyyy-MM-dd HH:mm:ss";
    public final static String DATE_TIME_MILLIS_PATTERN = "yyyy-MM-dd HH:mm:ss.SSS";


    /**
     * Date formatting with format: yyyy-MM-dd
     *
     * @param date Date
     * @return Returns date in yyyy-MM-dd format
     */
    public static String format(Date date) {
        return format(date, DATE_PATTERN);
    }

    /**
     * Date formatting with format: yyyy-MM-dd
     *
     * @param date    Date
     * @param pattern Format, e.g.: DateUtils.DATE_TIME_PATTERN
     * @return Returns date in yyyy-MM-dd format
     */
    public static String format(Date date, String pattern) {
        if (date != null) {
            SimpleDateFormat df = new SimpleDateFormat(pattern);
            return df.format(date);
        }
        return null;
    }

    /**
     * Date parsing
     *
     * @param date    Date
     * @param pattern Format, e.g.: DateUtils.DATE_TIME_PATTERN
     * @return Returns Date
     */
    public static Date parse(String date, String pattern) {
        try {
            return new SimpleDateFormat(pattern).parse(date);
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return null;
    }


    public static String getDateTimeNow() {
        return getDateTimeNow(DATE_TIME_PATTERN);
    }

    public static String getDateTimeNow(String pattern) {
        return format(new Date(), pattern);
    }

    public static String millsToSecond(long mills) {
        return String.format("%.3f", mills / 1000.0);
    }

    /**
     * Get short time string: returns "just now" for 10 seconds ago, "X seconds ago", "X hours ago", returns full date time for over a week
     * @param date
     * @return
     */
    public static String getShortTime(Date date) {
        if (date == null) {
            return null;
        }
        // Convert Date to Instant
        LocalDateTime localDateTime = date.toInstant()
                // Get system default timezone
                .atZone(ZoneId.systemDefault())
                // Convert to LocalDateTime
                .toLocalDateTime();
        // Current time
        LocalDateTime now = LocalDateTime.now();
        // Time difference in seconds
        long secondsBetween = ChronoUnit.SECONDS.between(localDateTime, now);

        if (secondsBetween <= 10) {
            return "just now";
        } else if (secondsBetween < 60) {
            return secondsBetween + " seconds ago";
        } else if (secondsBetween < 60 * 60) {
            return secondsBetween / 60 + " minutes ago";
        } else if (secondsBetween < 86400) {
            return secondsBetween / 3600 + " hours ago";
        } else if (secondsBetween < 604800) {
            return secondsBetween / 86400 + " days ago";
        } else {
            // Over a week, show full date time
            return format(date,DATE_TIME_PATTERN);
        }
    }
}
