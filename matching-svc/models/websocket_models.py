from fastapi import WebSocket

class WebsocketConnectionManager ():
    """
    WebSocket connection manager to track persistent connections with users.
    """
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """
        Connect to the websocket.
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: str):
        """
        Disconnect the websocket connection for the given user.
        """
        await self.active_connections[user_id].close()
        self.remove_websocket_connection(user_id)

    def remove_websocket_connection(self, user_id: str):
        """
        Remove the websocket connection with the given user's websocket.
        """
        self.active_connections.pop(user_id, None)

    async def send_message_to_user(self, user_id: str, message: str):
        """
        Send a message to the user through the websocket.
        """
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)