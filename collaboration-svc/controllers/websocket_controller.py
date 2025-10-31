import json
from utils.utils import get_envvar
from utils.logger import log
import websockets
from websockets.exceptions import ConnectionClosed
from websockets import ClientConnection

ENV_API_WEBSOCKET_URL = "GATEWAY_WEBSOCKET_URL"

class WebSocketManager:
    def __init__(self):
        self.active_connection = None

    def get_websocket_connection(self) -> ClientConnection:
        """
        Retrieves the WebSocket connection object.
        """
        return self.active_connection

    async def connect(self) -> None:
        """
        Establishes a WebSocket connection with the API gateway.
        """
        try:
            self.active_connection = await websockets.connect(get_envvar(ENV_API_WEBSOCKET_URL))
        except Exception:
            log.info(f"Unable to establish a WebSocket connection with API gateway {get_envvar(ENV_API_WEBSOCKET_URL)}")
            raise

    async def disconnect(self) -> None:
        """
        Disconnects the WebSocket connection.
        """
        if self.active_connection:
            await self.active_connection.close()
            self.active_connection = None

    async def send_message(self, receiver: str, room_id: str, body: str) -> None:
        """
        Sends a message though the WebSocket to the API gateway.
        """

        message = {
            "user_id": receiver,
            "room_id": room_id,
            "event": body
        }

        if self.active_connection:
            await self.active_connection.send(json.dumps(message))

    async def receive_message(self) -> dict | None:
        """
        Receives a message from the WebSocket and parses it into a JSON and return a dictionary.
        """
        if not self.active_connection:
            raise ConnectionError("No active WebSocket connection")

        websocket_connection = self.get_websocket_connection()

        try:
            data = await websocket_connection.recv()
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                log.warning(f"Received non-JSON message: {data}")
                return None
        except ConnectionClosed:
            log.error("WebSocket connection is closed.")
            raise
