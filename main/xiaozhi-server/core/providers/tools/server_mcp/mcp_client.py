"""Server-side MCP client."""

from __future__ import annotations

from datetime import timedelta
import asyncio
import os
import shutil
import concurrent.futures
from contextlib import AsyncExitStack
from typing import Optional, List, Dict, Any

from mcp import ClientSession, StdioServerParameters, Implementation
from mcp.client.session import SamplingFnT, ElicitationFnT, ListRootsFnT, LoggingFnT, MessageHandlerFnT
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.session import ProgressFnT

from config.logger import setup_logging
from core.utils.util import sanitize_tool_name

TAG = __name__


class ServerMCPClient:
    """Server-side MCP client used to connect to and manage MCP services."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the server-side MCP client.

        Args:
            config: MCP service configuration dictionary.
        """
        self.logger = setup_logging()
        self.config = config

        self._worker_task: Optional[asyncio.Task] = None
        self._ready_evt = asyncio.Event()
        self._shutdown_evt = asyncio.Event()

        self.session: Optional[ClientSession] = None
        self.tools: List = []  # Raw tool objects.
        self.tools_dict: Dict[str, Any] = {}
        self.name_mapping: Dict[str, str] = {}

    async def initialize(self, read_timeout_seconds: timedelta | None = None,
             sampling_callback: SamplingFnT | None = None,
             elicitation_callback: ElicitationFnT | None = None,
             list_roots_callback: ListRootsFnT | None = None,
             logging_callback: LoggingFnT | None = None,
             message_handler: MessageHandlerFnT | None = None,
             client_info: Implementation | None = None):
        """Initialize the MCP client connection."""
        if self._worker_task:
            return

        self._worker_task = asyncio.create_task(
            self._worker(read_timeout_seconds=read_timeout_seconds,
                        sampling_callback=sampling_callback,
                        elicitation_callback=elicitation_callback,
                        list_roots_callback=list_roots_callback,
                        logging_callback=logging_callback,
                        message_handler=message_handler,
                        client_info=client_info), name="ServerMCPClientWorker"
        )
        await self._ready_evt.wait()

        self.logger.bind(tag=TAG).info(
            f"Server-side MCP client connected. Available tools: {[name for name in self.name_mapping.values()]}"
        )

    async def cleanup(self):
        """Clean up MCP client resources."""
        if not self._worker_task:
            return

        self._shutdown_evt.set()
        try:
            await asyncio.wait_for(self._worker_task, timeout=20)
        except (asyncio.TimeoutError, Exception) as e:
            self.logger.bind(tag=TAG).error(
                f"Error while closing server-side MCP client: {e}"
            )
        finally:
            self._worker_task = None

    def has_tool(self, name: str) -> bool:
        """Check whether a specific tool is available.

        Args:
            name: Tool name.

        Returns:
            bool: Whether the tool exists.
        """
        return name in self.tools_dict

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get definitions for all available tools.

        Returns:
            List[Dict[str, Any]]: Tool definition list.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for name, tool in self.tools_dict.items()
        ]

    async def call_tool(self, name: str, arguments: dict, read_timeout_seconds: timedelta | None = None, progress_callback: ProgressFnT | None = None, *, meta: dict[str, Any] | None = None) -> Any:
        """Call a specific tool.

        Args:
            name: Tool name.
            arguments: Tool arguments.
            read_timeout_seconds:
            progress_callback: Progress callback.
            meta:

        Returns:
            Any: Tool execution result.

        Raises:
            RuntimeError: Raised when the client is not initialized.
        """
        if not self.session:
            raise RuntimeError("Server-side MCP client is not initialized")

        real_name = self.name_mapping.get(name, name)
        loop = self._worker_task.get_loop()
        coro = self.session.call_tool(real_name, arguments=arguments, read_timeout_seconds=read_timeout_seconds, progress_callback=progress_callback, meta=meta)

        if loop is asyncio.get_running_loop():
            return await coro

        fut: concurrent.futures.Future = asyncio.run_coroutine_threadsafe(coro, loop)
        return await asyncio.wrap_future(fut)

    def is_connected(self) -> bool:
        """Check whether the MCP client connection is healthy.

        Returns:
            bool: `True` when the client is connected and working properly.
        """
        # Check that the worker task exists.
        if self._worker_task is None:
            return False

        # Check that the worker task has not completed or been cancelled.
        if self._worker_task.done():
            return False

        # Check that a session exists.
        if self.session is None:
            return False

        # All checks passed, so the connection is healthy.
        return True

    async def _worker(self, read_timeout_seconds: timedelta | None = None,
             sampling_callback: SamplingFnT | None = None,
             elicitation_callback: ElicitationFnT | None = None,
             list_roots_callback: ListRootsFnT | None = None,
             logging_callback: LoggingFnT | None = None,
             message_handler: MessageHandlerFnT | None = None,
             client_info: Implementation | None = None):
        """MCP client worker coroutine."""
        async with AsyncExitStack() as stack:
            try:
                # Create a stdio client when `command` is configured.
                if "command" in self.config:
                    cmd = (
                        shutil.which("npx")
                        if self.config["command"] == "npx"
                        else self.config["command"]
                    )
                    env = {**os.environ, **self.config.get("env", {})}
                    params = StdioServerParameters(
                        command=cmd,
                        args=self.config.get("args", []),
                        env=env,
                    )
                    stdio_r, stdio_w = await stack.enter_async_context(
                        stdio_client(params)
                    )
                    read_stream, write_stream = stdio_r, stdio_w

                # Create an HTTP/SSE client when `url` is configured.
                elif "url" in self.config:
                    headers = dict(self.config.get("headers", {}))
                    # TODO: keep compatibility with older config versions.
                    if "API_ACCESS_TOKEN" in self.config:
                        headers["Authorization"] = f"Bearer {self.config['API_ACCESS_TOKEN']}"
                        self.logger.bind(tag=TAG).warning(
                            "You are using the deprecated API_ACCESS_TOKEN setting. Put it directly in .mcp_server_settings.json headers instead, for example: 'Authorization': 'Bearer API_ACCESS_TOKEN'"
                        )
                   
                    # Choose the transport implementation, defaulting to SSE.
                    transport_type = self.config.get("transport", "sse")

                    if transport_type == "streamable-http" or transport_type == "http":
                        # Use Streamable HTTP transport.
                        http_r, http_w, get_session_id = await stack.enter_async_context(
                            streamablehttp_client(
                                url=self.config["url"],
                                headers=headers,
                                timeout=self.config.get("timeout", 30),
                                sse_read_timeout=self.config.get("sse_read_timeout", 60 * 5),
                                terminate_on_close=self.config.get("terminate_on_close", True)
                            )
                        )
                        read_stream, write_stream = http_r, http_w
                    else:
                        # Use traditional SSE transport.
                        sse_r, sse_w = await stack.enter_async_context(
                            sse_client(
                                url=self.config["url"],
                                headers=headers,
                                timeout=self.config.get("timeout", 5),
                                sse_read_timeout=self.config.get("sse_read_timeout", 60 * 5)
                            )
                        )
                        read_stream, write_stream = sse_r, sse_w

                else:
                    raise ValueError(
                        "MCP client configuration must include either 'command' or 'url'"
                    )

                self.session = await stack.enter_async_context(
                    ClientSession(
                        read_stream=read_stream,
                        write_stream=write_stream,
                        read_timeout_seconds=read_timeout_seconds,
                        sampling_callback=sampling_callback,
                        elicitation_callback=elicitation_callback,
                        list_roots_callback=list_roots_callback,
                        logging_callback=logging_callback,
                        message_handler=message_handler,
                        client_info=client_info
                    )
                )
                await self.session.initialize()

                # Fetch the tool list.
                self.tools = (await self.session.list_tools()).tools
                for t in self.tools:
                    sanitized = sanitize_tool_name(t.name)
                    self.tools_dict[sanitized] = t
                    self.name_mapping[sanitized] = t.name

                self._ready_evt.set()

                # Wait until shutdown is requested.
                await self._shutdown_evt.wait()

            except Exception as e:
                self.logger.bind(tag=TAG).error(
                    f"Server-side MCP client worker failed: {e}"
                )
                self._ready_evt.set()
                raise
