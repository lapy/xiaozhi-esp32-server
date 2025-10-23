package xiaozhi.modules.security.password;

/**
 * Password utility class
 * Copyright (c) Renren Open Source All rights reserved.
 * Website: https://www.renren.io
 */
public class PasswordUtils {
    private static PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    /**
     * Encrypt
     *
     * @param str String
     * @return Returns encrypted string
     */
    public static String encode(String str) {
        return passwordEncoder.encode(str);
    }

    /**
     * Compare if passwords are equal
     *
     * @param str      Plain text password
     * @param password Encrypted password
     * @return true: success false: failure
     */
    public static boolean matches(String str, String password) {
        return passwordEncoder.matches(str, password);
    }

    public static void main(String[] args) {
        String str = "admin";
        String password = encode(str);

        System.out.println(password);
        System.out.println(matches(str, password));
    }

}
