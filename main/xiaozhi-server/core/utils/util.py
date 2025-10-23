import re
import os
import json
import copy
import wave
import socket
import requests
import subprocess
import numpy as np
import opuslib_next
from io import BytesIO
from core.utils import p3
from pydub import AudioSegment
from typing import Callable, Any

TAG = __name__
emoji_map = {
    "neutral": "😶",
    "happy": "🙂",
    "laughing": "😆",
    "funny": "😂",
    "sad": "😔",
    "angry": "😠",
    "crying": "😭",
    "loving": "😍",
    "embarrassed": "😳",
    "surprised": "😲",
    "shocked": "😱",
    "thinking": "🤔",
    "winking": "😉",
    "cool": "😎",
    "relaxed": "😌",
    "delicious": "🤤",
    "kissy": "😘",
    "confident": "😏",
    "sleepy": "😴",
    "silly": "😜",
    "confused": "🙄",
}


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google's DNS servers
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return "127.0.0.1"


def is_private_ip(ip_addr):
    """
    Check if an IP address is a private IP address (compatible with IPv4 and IPv6).

    @param {string} ip_addr - The IP address to check.
    @return {bool} True if the IP address is private, False otherwise.
    """
    try:
        # Validate IPv4 or IPv6 address format
        if not re.match(
            r"^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$", ip_addr
        ):
            return False  # Invalid IP address format

        # IPv4 private address ranges
        if "." in ip_addr:  # IPv4 address
            ip_parts = list(map(int, ip_addr.split(".")))
            if ip_parts[0] == 10:
                return True  # 10.0.0.0/8 range
            elif ip_parts[0] == 172 and 16 <= ip_parts[1] <= 31:
                return True  # 172.16.0.0/12 range
            elif ip_parts[0] == 192 and ip_parts[1] == 168:
                return True  # 192.168.0.0/16 range
            elif ip_addr == "127.0.0.1":
                return True  # Loopback address
            elif ip_parts[0] == 169 and ip_parts[1] == 254:
                return True  # Link-local address 169.254.0.0/16
            else:
                return False  # Not a private IPv4 address
        else:  # IPv6 address
            ip_addr = ip_addr.lower()
            if ip_addr.startswith("fc00:") or ip_addr.startswith("fd00:"):
                return True  # Unique Local Addresses (FC00::/7)
            elif ip_addr == "::1":
                return True  # Loopback address
            elif ip_addr.startswith("fe80:"):
                return True  # Link-local unicast addresses (FE80::/10)
            else:
                return False  # Not a private IPv6 address

    except (ValueError, IndexError):
        return False  # IP address format error or insufficient segments


def get_ip_info(ip_addr, logger):
    try:
        # Import global cache manager
        from core.utils.cache.manager import cache_manager, CacheType

        # First get from cache
        cached_ip_info = cache_manager.get(CacheType.IP_INFO, ip_addr)
        if cached_ip_info is not None:
            return cached_ip_info

        # Cache miss, call API
        if is_private_ip(ip_addr):
            ip_addr = ""
        url = f"https://ipapi.co/{ip_addr}/json/"
        resp = requests.get(url).json()
        ip_info = {"city": resp.get("city")}

        # Store in cache
        cache_manager.set(CacheType.IP_INFO, ip_addr, ip_info)
        return ip_info
    except Exception as e:
        logger.bind(tag=TAG).error(f"Error getting client ip info: {e}")
        return {}


def write_json_file(file_path, data):
    """Write data to JSON file"""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def remove_punctuation_and_length(text):
    # Unicode ranges for full-width and half-width punctuation
    full_width_punctuations = (
        "！＂＃＄％＆＇（）＊＋，－。／：；＜＝＞？＠［＼］＾＿｀｛｜｝～"
    )
    half_width_punctuations = r'!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
    space = " "  # Half-width space
    full_width_space = "　"  # Full-width space

    # Remove full-width and half-width punctuation and spaces
    result = "".join(
        [
            char
            for char in text
            if char not in full_width_punctuations
            and char not in half_width_punctuations
            and char not in space
            and char not in full_width_space
        ]
    )

    if result == "Yeah":
        return 0, ""
    return len(result), result


def check_model_key(modelType, modelKey):
    if "your" in modelKey:
        return f"Configuration error: {modelType} API key not set, current value: {modelKey}"
    return None


def parse_string_to_list(value, separator=";"):
    """
    Convert input value to list
    Args:
        value: Input value, can be None, string or list
        separator: Separator, default is semicolon
    Returns:
        list: Processed list
    """
    if value is None or value == "":
        return []
    elif isinstance(value, str):
        return [item.strip() for item in value.split(separator) if item.strip()]
    elif isinstance(value, list):
        return value
    return []


def check_ffmpeg_installed():
    ffmpeg_installed = False
    try:
        # Execute ffmpeg -version command and capture output
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,  # Throw exception if return code is non-zero
        )
        # Check if output contains version information (optional)
        output = result.stdout + result.stderr
        if "ffmpeg version" in output.lower():
            ffmpeg_installed = True
        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Command execution failed or not found
        ffmpeg_installed = False
    if not ffmpeg_installed:
        error_msg = "Your computer has not correctly installed ffmpeg\n"
        error_msg += "\nWe recommend:\n"
        error_msg += "1. Follow the project installation documentation to correctly enter conda environment\n"
        error_msg += "2. Check installation documentation on how to install ffmpeg in conda environment\n"
        raise ValueError(error_msg)


def extract_json_from_string(input_string):
    """Extract JSON part from string"""
    pattern = r"(\{.*\})"
    match = re.search(pattern, input_string, re.DOTALL)  # Add re.DOTALL
    if match:
        return match.group(1)  # Return extracted JSON string
    return None


def audio_to_data_stream(audio_file_path, is_opus=True, callback: Callable[[Any], Any]=None) -> None:
    # Get file extension
    file_type = os.path.splitext(audio_file_path)[1]
    if file_type:
        file_type = file_type.lstrip(".")
    # Read audio file, -nostdin parameter: do not read data from standard input, otherwise FFmpeg will block
    audio = AudioSegment.from_file(
        audio_file_path, format=file_type, parameters=["-nostdin"]
    )

    # Convert to mono/16kHz sample rate/16-bit little-endian encoding (ensure compatibility with encoder)
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    # Get raw PCM data (16-bit little-endian)
    raw_data = audio.raw_data
    pcm_to_data_stream(raw_data, is_opus, callback)

def audio_to_data(audio_file_path: str, is_opus: bool = True) -> list[bytes]:
    """
    Convert audio file to Opus/PCM encoded frame list
    Args:
        audio_file_path: Audio file path
        is_opus: Whether to perform Opus encoding
    """
    # Get file extension
    file_type = os.path.splitext(audio_file_path)[1]
    if file_type:
        file_type = file_type.lstrip(".")
    # Read audio file, -nostdin parameter: do not read data from standard input, otherwise FFmpeg will block
    audio = AudioSegment.from_file(
        audio_file_path, format=file_type, parameters=["-nostdin"]
    )

    # Convert to mono/16kHz sample rate/16-bit little-endian encoding (ensure compatibility with encoder)
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    # Get raw PCM data (16-bit little-endian)
    raw_data = audio.raw_data

    # Initialize Opus encoder
    encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

    # Encoding parameters
    frame_duration = 60  # 60ms per frame
    frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

    datas = []
    # Process all audio data frame by frame (including last frame which may be zero-padded)
    for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
        # Get current frame binary data
        chunk = raw_data[i : i + frame_size * 2]

        # If last frame is insufficient, pad with zeros
        if len(chunk) < frame_size * 2:
            chunk += b"\x00" * (frame_size * 2 - len(chunk))

        if is_opus:
            # Convert to numpy array for processing
            np_frame = np.frombuffer(chunk, dtype=np.int16)
            # Encode Opus data
            frame_data = encoder.encode(np_frame.tobytes(), frame_size)
        else:
            frame_data = chunk if isinstance(chunk, bytes) else bytes(chunk)

        datas.append(frame_data)

    return datas

def audio_bytes_to_data_stream(audio_bytes, file_type, is_opus, callback: Callable[[Any], Any]) -> None:
    """
    Directly convert audio binary data to opus/pcm data, supports wav, mp3, p3
    """
    if file_type == "p3":
        # Directly decode with p3
        return p3.decode_opus_from_bytes_stream(audio_bytes, callback)
    else:
        # Other formats use pydub
        audio = AudioSegment.from_file(
            BytesIO(audio_bytes), format=file_type, parameters=["-nostdin"]
        )
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        raw_data = audio.raw_data
        pcm_to_data_stream(raw_data, is_opus, callback)


def pcm_to_data_stream(raw_data, is_opus=True, callback: Callable[[Any], Any] = None):
    # Initialize Opus encoder
    encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

    # Encoding parameters
    frame_duration = 60  # 60ms per frame
    frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

    # Process all audio data frame by frame (including last frame which may be zero-padded)
    for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
        # Get current frame binary data
        chunk = raw_data[i : i + frame_size * 2]

        # If last frame is insufficient, pad with zeros
        if len(chunk) < frame_size * 2:
            chunk += b"\x00" * (frame_size * 2 - len(chunk))

        if is_opus:
            # Convert to numpy array for processing
            np_frame = np.frombuffer(chunk, dtype=np.int16)
            # Encode Opus data
            frame_data = encoder.encode(np_frame.tobytes(), frame_size)
            callback(frame_data)
        else:
            frame_data = chunk if isinstance(chunk, bytes) else bytes(chunk)
            callback(frame_data)

def opus_datas_to_wav_bytes(opus_datas, sample_rate=16000, channels=1):
    """
    Decode opus frame list to wav byte stream
    """
    decoder = opuslib_next.Decoder(sample_rate, channels)
    pcm_datas = []

    frame_duration = 60  # ms
    frame_size = int(sample_rate * frame_duration / 1000)  # 960

    for opus_frame in opus_datas:
        # Decode to PCM (returns bytes, 2 bytes/sample)
        pcm = decoder.decode(opus_frame, frame_size)
        pcm_datas.append(pcm)

    pcm_bytes = b"".join(pcm_datas)

    # Write wav byte stream
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return wav_buffer.getvalue()

def check_vad_update(before_config, new_config):
    if (
        new_config.get("selected_module") is None
        or new_config["selected_module"].get("VAD") is None
    ):
        return False
    update_vad = False
    current_vad_module = before_config["selected_module"]["VAD"]
    new_vad_module = new_config["selected_module"]["VAD"]
    current_vad_type = (
        current_vad_module
        if "type" not in before_config["VAD"][current_vad_module]
        else before_config["VAD"][current_vad_module]["type"]
    )
    new_vad_type = (
        new_vad_module
        if "type" not in new_config["VAD"][new_vad_module]
        else new_config["VAD"][new_vad_module]["type"]
    )
    update_vad = current_vad_type != new_vad_type
    return update_vad


def check_asr_update(before_config, new_config):
    if (
        new_config.get("selected_module") is None
        or new_config["selected_module"].get("ASR") is None
    ):
        return False
    update_asr = False
    current_asr_module = before_config["selected_module"]["ASR"]
    new_asr_module = new_config["selected_module"]["ASR"]
    current_asr_type = (
        current_asr_module
        if "type" not in before_config["ASR"][current_asr_module]
        else before_config["ASR"][current_asr_module]["type"]
    )
    new_asr_type = (
        new_asr_module
        if "type" not in new_config["ASR"][new_asr_module]
        else new_config["ASR"][new_asr_module]["type"]
    )
    update_asr = current_asr_type != new_asr_type
    return update_asr


def filter_sensitive_info(config: dict) -> dict:
    """
    Filter sensitive information from configuration
    Args:
        config: Original configuration dictionary
    Returns:
        Filtered configuration dictionary
    """
    sensitive_keys = [
        "api_key",
        "personal_access_token",
        "access_token",
        "token",
        "secret",
        "access_key_secret",
        "secret_key",
    ]

    def _filter_dict(d: dict) -> dict:
        filtered = {}
        for k, v in d.items():
            if any(sensitive in k.lower() for sensitive in sensitive_keys):
                filtered[k] = "***"
            elif isinstance(v, dict):
                filtered[k] = _filter_dict(v)
            elif isinstance(v, list):
                filtered[k] = [_filter_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                filtered[k] = v
        return filtered

    return _filter_dict(copy.deepcopy(config))


def get_vision_url(config: dict) -> str:
    """Get vision URL

    Args:
        config: Configuration dictionary

    Returns:
        str: vision URL
    """
    server_config = config["server"]
    vision_explain = server_config.get("vision_explain", "")
    if "your" in vision_explain:
        local_ip = get_local_ip()
        port = int(server_config.get("http_port", 8003))
        vision_explain = f"http://{local_ip}:{port}/mcp/vision/explain"
    return vision_explain


def is_valid_image_file(file_data: bytes) -> bool:
    """
    Check if file data is valid image format

    Args:
        file_data: Binary data of the file

    Returns:
        bool: Returns True if valid image format, False otherwise
    """
    # Magic numbers (file headers) for common image formats
    image_signatures = {
        b"\xff\xd8\xff": "JPEG",
        b"\x89PNG\r\n\x1a\n": "PNG",
        b"GIF87a": "GIF",
        b"GIF89a": "GIF",
        b"BM": "BMP",
        b"II*\x00": "TIFF",
        b"MM\x00*": "TIFF",
        b"RIFF": "WEBP",
    }

    # Check if file header matches any known image format
    for signature in image_signatures:
        if file_data.startswith(signature):
            return True

    return False


def sanitize_tool_name(name: str) -> str:
    """Sanitize tool names for OpenAI compatibility."""
    # Support letters, numbers, underscores and hyphens
    return re.sub(r"[^a-zA-Z0-9_\-]", "_", name)


def validate_mcp_endpoint(mcp_endpoint: str) -> bool:
    """
    Validate MCP endpoint format

    Args:
        mcp_endpoint: MCP endpoint string

    Returns:
        bool: Whether valid
    """
    # 1. Check if starts with ws
    if not mcp_endpoint.startswith("ws"):
        return False

    # 2. Check if contains key, call keywords
    if "key" in mcp_endpoint.lower() or "call" in mcp_endpoint.lower():
        return False

    # 3. Check if contains /mcp/ keyword
    if "/mcp/" not in mcp_endpoint:
        return False

    return True
