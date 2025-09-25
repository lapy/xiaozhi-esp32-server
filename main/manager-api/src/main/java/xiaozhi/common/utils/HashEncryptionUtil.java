package xiaozhi.common.utils;

import lombok.extern.slf4j.Slf4j;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Hash encryption algorithm utility class
 * @author zjy
 */
@Slf4j
public class HashEncryptionUtil {
    /**
     * Encrypt using md5
     * @param context Content to be encrypted
     * @return Hash value
     */
    public static String Md5hexDigest(String context){
        return hexDigest(context,"MD5");
    }

    /**
     * Encrypt using specified hash algorithm
     * @param context Content to be encrypted
     * @param algorithm Hash algorithm
     * @return Hash value
     */
   public static String hexDigest(String context,String algorithm ){
       // Get MD5 algorithm instance
       MessageDigest md = null;
       try {
           md = MessageDigest.getInstance(algorithm);
       } catch (NoSuchAlgorithmException e) {
           log.error("Encryption failed algorithm: {}",algorithm);
           throw new RuntimeException("Encryption failed, system does not support "+ algorithm +" hash algorithm");
       }
       // Calculate MD5 value of agent id
       byte[] messageDigest = md.digest(context.getBytes());
       // Convert byte array to hexadecimal string
       StringBuilder hexString = new StringBuilder();
       for (byte b : messageDigest) {
           String hex = Integer.toHexString(0xFF & b);
           if (hex.length() == 1) {
               hexString.append('0');
           }
           hexString.append(hex);
       }
       return hexString.toString();
   }

}
