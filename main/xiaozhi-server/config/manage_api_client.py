import os
import time
import base64
from typing import Optional, Dict

import httpx

TAG = __name__


class DeviceNotFoundException(Exception):
    pass


class DeviceBindException(Exception):
    def __init__(self, bind_code):
        self.bind_code = bind_code
        super().__init__(f"Device binding exception, bind code: {bind_code}")


class ManageApiClient:
    _instance = None
    _client = None
    _secret = None

    def __new__(cls, config):
        """Singleton pattern ensures global unique instance and supports passing configuration parameters"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._init_client(config)
        return cls._instance

    @classmethod
    def _init_client(cls, config):
        """Initialize persistent connection pool"""
        cls.config = config.get("manager-api")

        if not cls.config:
            raise Exception("manager-api configuration error")

        if not cls.config.get("url") or not cls.config.get("secret"):
            raise Exception("manager-api url or secret configuration error")

        if "your" in cls.config.get("secret"):
            raise Exception("Please configure manager-api secret first")

        cls._secret = cls.config.get("secret")
        cls.max_retries = cls.config.get("max_retries", 6)  # Maximum retry count
        cls.retry_delay = cls.config.get("retry_delay", 10)  # Initial retry delay (seconds)
        # NOTE(goody): 2025/4/16 Unified management of HTTP related resources, can add thread pool or timeout later
        # Can also uniformly configure apiToken etc. to use common Auth later
        cls._client = httpx.Client(
            base_url=cls.config.get("url"),
            headers={
                "User-Agent": f"PythonClient/2.0 (PID:{os.getpid()})",
                "Accept": "application/json",
                "Authorization": "Bearer " + cls._secret,
            },
            timeout=cls.config.get("timeout", 30),  # Default timeout 30 seconds
        )

    @classmethod
    def _request(cls, method: str, endpoint: str, **kwargs) -> Dict:
        """Send single HTTP request and handle response"""
        endpoint = endpoint.lstrip("/")
        response = cls._client.request(method, endpoint, **kwargs)
        response.raise_for_status()

        result = response.json()

        # Handle API returned business errors
        if result.get("code") == 10041:
            raise DeviceNotFoundException(result.get("msg"))
        elif result.get("code") == 10042:
            raise DeviceBindException(result.get("msg"))
        elif result.get("code") != 0:
            raise Exception(f"API returned error: {result.get('msg', 'Unknown error')}")

        # Return success data
        return result.get("data") if result.get("code") == 0 else None

    @classmethod
    def _should_retry(cls, exception: Exception) -> bool:
        """Determine if exception should be retried"""
        # Network connection related errors
        if isinstance(
            exception, (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError)
        ):
            return True

        # HTTP status code errors
        if isinstance(exception, httpx.HTTPStatusError):
            status_code = exception.response.status_code
            return status_code in [408, 429, 500, 502, 503, 504]

        return False

    @classmethod
    def _execute_request(cls, method: str, endpoint: str, **kwargs) -> Dict:
        """Request executor with retry mechanism"""
        retry_count = 0

        while retry_count <= cls.max_retries:
            try:
                # Execute request
                return cls._request(method, endpoint, **kwargs)
            except Exception as e:
                # Determine if should retry
                if retry_count < cls.max_retries and cls._should_retry(e):
                    retry_count += 1
                    print(
                        f"{method} {endpoint} request failed, will retry {retry_count} times after {cls.retry_delay:.1f} seconds"
                    )
                    time.sleep(cls.retry_delay)
                    continue
                else:
                    # Do not retry, directly raise exception
                    raise

    @classmethod
    def safe_close(cls):
        """Safely close connection pool"""
        if cls._client:
            cls._client.close()
            cls._instance = None


def get_server_config() -> Optional[Dict]:
    """Get server basic configuration"""
    return ManageApiClient._instance._execute_request("POST", "/config/server-base")


def get_agent_models(
    mac_address: str, client_id: str, selected_module: Dict
) -> Optional[Dict]:
    """Get agent model configuration"""
    return ManageApiClient._instance._execute_request(
        "POST",
        "/config/agent-models",
        json={
            "macAddress": mac_address,
            "clientId": client_id,
            "selectedModule": selected_module,
        },
    )


def save_mem_local_short(mac_address: str, short_momery: str) -> Optional[Dict]:
    try:
        return ManageApiClient._instance._execute_request(
            "PUT",
            f"/agent/saveMemory/" + mac_address,
            json={
                "summaryMemory": short_momery,
            },
        )
    except Exception as e:
        print(f"Failed to store short-term memory to server: {e}")
        return None


def report(
    mac_address: str, session_id: str, chat_type: int, content: str, audio, report_time
) -> Optional[Dict]:
    """Business method example with circuit breaker"""
    if not content or not ManageApiClient._instance:
        return None
    try:
        return ManageApiClient._instance._execute_request(
            "POST",
            f"/agent/chat-history/report",
            json={
                "macAddress": mac_address,
                "sessionId": session_id,
                "chatType": chat_type,
                "content": content,
                "reportTime": report_time,
                "audioBase64": (
                    base64.b64encode(audio).decode("utf-8") if audio else None
                ),
            },
        )
    except Exception as e:
        print(f"TTS reporting failed: {e}")
        return None


def init_service(config):
    ManageApiClient(config)


def manage_api_http_safe_close():
    ManageApiClient.safe_close()
