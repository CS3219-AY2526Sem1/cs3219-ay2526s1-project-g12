from typing import Dict, Optional

from fastapi import WebSocket

from utils.logger import log

COLLAB = "collab"
class WebSocketManager:
    """Manages WebSocket connections for FE and Collab service"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        # connection_type -> websocket
        # e.g: {"collab": <websocket>, "fe:user123": <websocket>}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """
        Connect and register a websocket with an identifier
        Args:
            websocket: The WebSocket connection
            connection_id: Identifier like "collab" or "fe:user123"
        """
        await websocket.accept()
        self.connections[connection_id] = websocket
        log.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Disconnect and remove a websocket connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            log.info(f"WebSocket disconnected: {connection_id}")
    
    def get_connection(self, connection_id: str) -> Optional[WebSocket]:
        """Get a specific websocket connection by ID"""
        return self.connections.get(connection_id)
    
    def get_collab_connection(self) -> Optional[WebSocket]:
        """Get the Collab service WebSocket connection"""
        return self.connections.get(COLLAB)
    
    def get_fe_connections(self) -> Dict[str, WebSocket]:
        """Get all Frontend WebSocket connections"""
        return {
            conn_id: ws 
            for conn_id, ws in self.connections.items() 
            if conn_id.startswith("fe:")
        }
    
    async def send_to_collab(self, message: str):
        """Send message from FE to Collab service"""
        collab_ws = self.get_collab_connection()
        if collab_ws:
            await collab_ws.send_text(message)
            log.info(f"Sent to Collab: {message}")
        else:
            log.error("Collab service not connected")
            raise Exception("Collab service not available")
    
    async def send_to_fe(self, user_id: str, message: str):
        """Send message from Collab to specific FE client"""
        fe_ws = self.get_connection(f"fe:{user_id}")
        if fe_ws:
            await fe_ws.send_text(message)
            log.info(f"Sent to FE {user_id}: {message}")
        else:
            log.error(f"FE client {user_id} not connected")
            raise Exception(f"FE client {user_id} not available")
    
    async def broadcast_to_all_fe(self, message: str):
        """Broadcast message from Collab to all FE clients"""
        fe_connections = self.get_fe_connections()
        if not fe_connections:
            log.info("Warning: No FE clients connected")
            return
        
        for conn_id, websocket in fe_connections.items():
            try:
                await websocket.send_text(message)
                log.info(f"Broadcast to {conn_id}: {message}")
            except Exception as e:
                log.error(f"Error sending to {conn_id}: {e}")
    
    async def forward_message(self, from_id: str, message: str, to_id: Optional[str] = None):
        """
        Forward message based on sender and receiver
        Args:
            from_id: Sender connection ID (e.g., "collab" or "fe:user123")
            message: The message to forward
            to_id: Optional specific receiver ID
        """
        if from_id == "collab":
            # Message from Collab -> send to FE
            if to_id:
                await self.send_to_fe(to_id, message)
            else:
                # Broadcast to all FE if no specific receiver
                await self.broadcast_to_all_fe(message)
        elif from_id.startswith("fe:"):
            # Message from FE -> send to Collab
            await self.send_to_collab(message)
        else:
            log.info(f"Unknown sender: {from_id}")
