import hmac
import base64
import hashlib
import time


class AuthenticationError(Exception):
    """Authentication exception."""

    pass


class AuthManager:
    """
    Unified authentication manager.

    Generates and verifies the client_id / device_id / token authentication
    tuple using HMAC-SHA256.

    The token carries only the signature and timestamp, not the raw
    client_id/device_id values. Those values are transmitted separately
    during connection setup.

    MQTT usage:
      client_id: client_id
      username: device_id
      password: token

    WebSocket usage:
      header: {Device-ID: device_id, Client-ID: client_id, Authorization: Bearer token, ...}
    """

    def __init__(self, secret_key: str, expire_seconds: int = 60 * 60 * 24 * 30):
        if not expire_seconds or expire_seconds < 0:
            self.expire_seconds = 60 * 60 * 24 * 30
        else:
            self.expire_seconds = expire_seconds
        self.secret_key = secret_key

    def _sign(self, content: str) -> str:
        """Generate an HMAC-SHA256 signature and return it as Base64."""
        sig = hmac.new(
            self.secret_key.encode("utf-8"), content.encode("utf-8"), hashlib.sha256
        ).digest()
        return base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")

    def generate_token(self, client_id: str, username: str) -> str:
        """
        Generate a token.

        Args:
            client_id: Device connection ID
            username: Device username, usually the device ID

        Returns:
            str: Encoded token string
        """
        ts = int(time.time())
        content = f"{client_id}|{username}|{ts}"
        signature = self._sign(content)
        # The token includes only the signature and timestamp.
        token = f"{signature}.{ts}"
        return token

    def verify_token(self, token: str, client_id: str, username: str) -> bool:
        """
        Verify whether the token is valid.

        Args:
            token: Token provided by the client
            client_id: Client ID used for the connection
            username: Username used for the connection
        """
        try:
            sig_part, ts_str = token.split(".")
            ts = int(ts_str)
            if int(time.time()) - ts > self.expire_seconds:
                return False  # Expired

            expected_sig = self._sign(f"{client_id}|{username}|{ts}")
            if not hmac.compare_digest(sig_part, expected_sig):
                return False

            return True
        except Exception:
            return False
