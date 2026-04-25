import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.connection import ConnectionHandler
from core.handle.textMessageHandlerRegistry import TextMessageHandlerRegistry

TAG = __name__


class TextMessageProcessor:
    """Main text message processor."""

    def __init__(self, registry: TextMessageHandlerRegistry):
        self.registry = registry

    async def process_message(self, conn: "ConnectionHandler", message: str) -> None:
        """Primary entry point for processing inbound text messages."""
        try:
            # Parse the message as JSON first.
            msg_json = json.loads(message)

            # Handle structured JSON messages.
            if isinstance(msg_json, dict):
                message_type = msg_json.get("type")

                # Log the received message before dispatch.
                conn.logger.bind(tag=TAG).info(
                    f"Received {message_type} message: {message}"
                )

                # Look up and execute the registered handler.
                handler = self.registry.get_handler(message_type)
                if handler:
                    await handler.handle(conn, msg_json)
                else:
                    conn.logger.bind(tag=TAG).error(
                        f"Received unknown message type: {message}"
                    )
            # Handle plain numeric messages.
            elif isinstance(msg_json, int):
                conn.logger.bind(tag=TAG).info(f"Received numeric message: {message}")
                await conn.websocket.send(message)

        except json.JSONDecodeError:
            # Forward non-JSON payloads directly after logging them.
            conn.logger.bind(tag=TAG).error(f"Parsed invalid message payload: {message}")
            await conn.websocket.send(message)
