from fastapi import WebSocket
from pydantic import BaseModel

class Message(BaseModel):
        receiver: str
        content: str

class ConnectionManager:
    def __init__(self):
        self.active_connection: WebSocket

    def get_websocket_connection(self) -> WebSocket:
        return self.active_connection

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection = websocket

    def disconnect(self):
        websocket = self.get_websocket_connection()
        websocket.close()
        self.active_connections = None

    async def send_message(self, message: Message):
        websocket = self.get_websocket_connection()
        await websocket.send_text(message)
