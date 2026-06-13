import json
import time
from typing import Dict, Any

from core.handle.textMessageHandler import TextMessageHandler
from core.handle.textMessageType import TextMessageType

TAG = __name__


class PingMessageHandler(TextMessageHandler):
    """Ping handler used to keep the WebSocket connection alive."""

    @property
    def message_type(self) -> TextMessageType:
        return TextMessageType.PING

    async def handle(self, conn, msg_json: Dict[str, Any]) -> None:
        """
        Handle a PING message and send a PONG response.

        Args:
            conn: WebSocket connection object
            msg_json: JSON payload for the PING message
        """
        # Ignore heartbeat traffic when WebSocket ping handling is disabled.
        enable_websocket_ping = conn.config.get("enable_websocket_ping", False)
        if not enable_websocket_ping:
            conn.logger.debug("WebSocket heartbeat handling is disabled; ignoring PING")
            return

        try:
            conn.logger.debug("Received PING message, sending PONG response")
            conn.last_activity_time = time.time() * 1000
            # Build the PONG response payload.
            pong_message = {
                "type": "pong",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }

            # Send the PONG response.
            await conn.websocket.send(json.dumps(pong_message))

        except Exception as e:
            conn.logger.error(f"Error while handling PING message: {e}")
