from utils.utils import get_envvar
from utils.logger import log
import websockets

ENV_API_WEBSOCKET_URL = "GATEWAY_WEBSOCKET_URL"

class WebSocketManager:
    def __init__(self):
        self.active_connection = None

    def get_websocket_connection(self):
        return self.active_connection

    async def connect(self):
        try:
            self.active_connection = await websockets.connect(get_envvar(ENV_API_WEBSOCKET_URL))
        except Exception as e:
            log.error("Unable to establish a WebSocket connection with API gateway")
            raise

    async def disconnect(self):
        if self.active_connection:
            await self.active_connection.close()
            self.active_connection = None

    async def send_message(self, message: str):
        if self.active_connection:
            await self.active_connection.send(message)
