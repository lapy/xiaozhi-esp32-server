import os, json, uuid
from types import SimpleNamespace
from typing import Any, Dict, List

import requests
from google import generativeai as genai
from google.generativeai import types, GenerationConfig

from core.providers.llm.base import LLMProviderBase
from core.utils.util import check_model_key
from config.logger import setup_logging
from google.generativeai.types import GenerateContentResponse
from requests import RequestException

log = setup_logging()
TAG = __name__


def test_proxy(proxy_url: str, test_url: str) -> bool:
    try:
        resp = requests.get(test_url, proxies={"http": proxy_url, "https": proxy_url})
        return 200 <= resp.status_code < 400
    except RequestException:
        return False


def setup_proxy_env(http_proxy: str | None, https_proxy: str | None):
    """
    Test HTTP and HTTPS proxy availability separately and set environment variables.
    If HTTPS proxy is unavailable but HTTP is available, HTTPS_PROXY will also point to HTTP.
    """
    test_http_url = "http://www.google.com"
    test_https_url = "https://www.google.com"

    ok_http = ok_https = False

    if http_proxy:
        ok_http = test_proxy(http_proxy, test_http_url)
        if ok_http:
            os.environ["HTTP_PROXY"] = http_proxy
            log.bind(tag=TAG).info(f"Configured Gemini HTTP proxy connectivity successful: {http_proxy}")
        else:
            log.bind(tag=TAG).warning(f"Configured Gemini HTTP proxy unavailable: {http_proxy}")

    if https_proxy:
        ok_https = test_proxy(https_proxy, test_https_url)
        if ok_https:
            os.environ["HTTPS_PROXY"] = https_proxy
            log.bind(tag=TAG).info(f"Configured Gemini HTTPS proxy connectivity successful: {https_proxy}")
        else:
            log.bind(tag=TAG).warning(
                f"Configured Gemini HTTPS proxy unavailable: {https_proxy}"
            )

    # If https_proxy is unavailable but http_proxy is available and can access https, reuse http_proxy as https_proxy
    if ok_http and not ok_https:
        if test_proxy(http_proxy, test_https_url):
            os.environ["HTTPS_PROXY"] = http_proxy
            ok_https = True
            log.bind(tag=TAG).info(f"Reusing HTTP proxy as HTTPS proxy: {http_proxy}")

    if not ok_http and not ok_https:
        log.bind(tag=TAG).error(
            f"Gemini proxy setup failed: Both HTTP and HTTPS proxies are unavailable, please check configuration"
        )
        raise RuntimeError("Both HTTP and HTTPS proxies are unavailable, please check configuration")


class LLMProvider(LLMProviderBase):
    def __init__(self, cfg: Dict[str, Any]):
        self.model_name = cfg.get("model_name", "gemini-2.0-flash")
        self.api_key = cfg["api_key"]
        http_proxy = cfg.get("http_proxy")
        https_proxy = cfg.get("https_proxy")

        model_key_msg = check_model_key("LLM", self.api_key)
        if model_key_msg:
            log.bind(tag=TAG).error(model_key_msg)

        if http_proxy or https_proxy:
            log.bind(tag=TAG).info(
                f"Detected Gemini proxy configuration, starting proxy connectivity test and proxy environment setup..."
            )
            setup_proxy_env(http_proxy, https_proxy)
            log.bind(tag=TAG).info(
                f"Gemini proxy setup successful - HTTP: {http_proxy}, HTTPS: {https_proxy}"
            )
        # Configure API key
        genai.configure(api_key=self.api_key)

        # Note: timeout parameter is not supported in current google-generativeai version

        # Create model instance
        self.model = genai.GenerativeModel(self.model_name)

        self.gen_cfg = GenerationConfig(
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            max_output_tokens=2048,
        )

        log.debug(
            f"Intent recognition parameters initialized: {self.gen_cfg.temperature}, {self.gen_cfg.max_output_tokens}, {self.gen_cfg.top_p}, {self.gen_cfg.top_k}"
        )

    @staticmethod
    def _build_tools(funcs: List[Dict[str, Any]] | None):
        if not funcs:
            return None
        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=f["function"]["name"],
                        description=f["function"]["description"],
                        parameters=f["function"]["parameters"],
                    )
                    for f in funcs
                ]
            )
        ]

    # Gemini documentation mentions no need to maintain session-id, directly concatenate with dialogue
    def response(self, session_id, dialogue, **kwargs):
        log.bind(tag=TAG).debug(f"Sending request to Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
        try:
            yield from self._generate(dialogue, None)
        except Exception as e:
            log.bind(tag=TAG).error(f"Error in Gemini response generation: {e}")
            yield f"【Gemini service response exception: {e}】"

    def response_with_functions(self, session_id, dialogue, functions=None):
        log.bind(tag=TAG).debug(f"Sending function request to Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
        try:
            yield from self._generate(dialogue, self._build_tools(functions))
        except Exception as e:
            log.bind(tag=TAG).error(f"Error in Gemini function call streaming: {e}")
            yield f"【Gemini service response exception: {e}】", None

    def _generate(self, dialogue, tools):
        role_map = {"assistant": "model", "user": "user"}
        contents: list = []
        # Concatenate dialogue
        for m in dialogue:
            r = m["role"]

            if r == "assistant" and "tool_calls" in m:
                tc = m["tool_calls"][0]
                contents.append(
                    {
                        "role": "model",
                        "parts": [
                            {
                                "function_call": {
                                    "name": tc["function"]["name"],
                                    "args": json.loads(tc["function"]["arguments"]),
                                }
                            }
                        ],
                    }
                )
                continue

            if r == "tool":
                contents.append(
                    {
                        "role": "model",
                        "parts": [{"text": str(m.get("content", ""))}],
                    }
                )
                continue

            contents.append(
                {
                    "role": role_map.get(r, "user"),
                    "parts": [{"text": str(m.get("content", ""))}],
                }
            )

        log.bind(tag=TAG).debug(f"Generated content request for Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
        
        stream: GenerateContentResponse = self.model.generate_content(
            contents=contents,
            generation_config=self.gen_cfg,
            tools=tools,
            stream=True,
        )

        log.bind(tag=TAG).debug(f"Received response from Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")

        try:
            for chunk in stream:
                log.bind(tag=TAG).debug(f"Received chunk from Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
                cand = chunk.candidates[0]
                log.bind(tag=TAG).debug(f"Processing candidate from Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
                for part in cand.content.parts:
                    # a) Function call - usually the last part is the function call
                    if getattr(part, "function_call", None):
                        fc = part.function_call
                        log.bind(tag=TAG).debug(f"Received function call from Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
                        yield None, [
                            SimpleNamespace(
                                id=uuid.uuid4().hex,
                                type="function",
                                function=SimpleNamespace(
                                    name=fc.name,
                                    arguments=json.dumps(
                                        dict(fc.args), ensure_ascii=False
                                    ),
                                ),
                            )
                        ]
                        return
                    # b) Plain text
                    if getattr(part, "text", None):
                        log.bind(tag=TAG).debug(f"Received text content from Gemini with model: {self.model_name}, dialogue length: {len(dialogue)}")
                        yield part.text if tools is None else (part.text, None)

        except Exception as e:
            log.bind(tag=TAG).error(f"Error in Gemini _generate method: {e}")
            raise
        finally:
            if tools is not None:
                yield None, None  # function-mode ends, return dummy packet

    # Close stream, reserve method for interrupting conversation functionality, official docs recommend closing previous stream when interrupting conversation to effectively reduce quota billing and resource usage
    @staticmethod
    def _safe_finish_stream(stream: GenerateContentResponse):
        if hasattr(stream, "resolve"):
            stream.resolve()  # Gemini SDK version ≥ 0.5.0
        elif hasattr(stream, "close"):
            stream.close()  # Gemini SDK version < 0.5.0
        else:
            for _ in stream:  # Fallback depletion
                pass
