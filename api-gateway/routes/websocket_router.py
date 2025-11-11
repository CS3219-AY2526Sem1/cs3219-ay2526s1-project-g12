import json

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer

from controllers.websocket_manager import WebSocketManager
from routes.dynamic_router import auth_user
from service.redis_settings import get_redis
from utils.logger import log

router = APIRouter()
security = HTTPBearer(auto_error=False)
manager = WebSocketManager()


@router.websocket("/ws/collab")
async def collab_websocket_endpoint(
    websocket: WebSocket, redis: aioredis.Redis = Depends(get_redis)
):
    """WebSocket endpoint for Collab service to connect"""
    connection_id = "collab"  # Can change to use instance ID if needed
    log.info(
        f"Attempting to connect Collab service from: {websocket.client.host}:{websocket.client.port}"
    )

    # Store connection info in Redis
    client_url = f"{websocket.client.host}:{websocket.client.port}"
    await redis.hset(
        f"websocket:{connection_id}",
        mapping={
            "url": client_url,
            "type": "collab",
        },
    )
    log.debug(
        f"Redis: Stored connection info for {connection_id}: url={client_url}, type=collab"
    )

    await manager.connect(websocket, connection_id)
    log.info(f"Collab service connected from: {client_url}")

    try:
        while True:
            # Receive message from Collab
            data = await websocket.receive_text()
            log.info(f"Received from Collab: {data}")

            # Parse message
            try:
                message_data = json.loads(data)
                user_id = message_data.get("user_id")  # Target user
                match_id = message_data.get("match_id", "")
                message_content = message_data.get("message", "")

                # Forward to FE - send full message structure
                message_to_send = json.dumps(
                    {
                        "user_id": user_id or "",
                        "match_id": match_id,
                        "message": message_content,
                    }
                )

                if user_id:
                    await manager.send_to_fe(user_id, message_to_send)
                else:
                    await manager.broadcast_to_all_fe(message_to_send)

            except json.JSONDecodeError:
                log.error(f"Invalid JSON received from Collab: {data}")
                # If not valid JSON, log error and continue
                continue

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        await redis.delete(f"websocket:{connection_id}")
        log.info("Collab service disconnected")


@router.websocket("/ws/fe")
async def fe_websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
    redis: aioredis.Redis = Depends(get_redis),
):
    """WebSocket endpoint for Frontend clients to connect"""
    log.info(f"Token received from FE: {token}")
    user_id = token
    connection_id = f"fe:{user_id}"

    # Store connection info in Redis
    client_url = f"{websocket.client.host}:{websocket.client.port}"
    log.info(f"Attempting to connect FE client {user_id} from: f{client_url}")

    await manager.connect(websocket, connection_id)
    log.info(f"FE client {user_id} connected from: {client_url}")
    await redis.hset(
        f"websocket:{connection_id}",
        mapping={
            "url": client_url,
            "type": "fe",
            "user_id": user_id,
        },
    )

    try:
        while True:
            # Receive message from FE
            data = await websocket.receive_text()
            log.info(f"Received from FE {user_id}: {data}")

            # Parse and validate message structure
            try:
                message_data = json.loads(data)

                # Extract fields (user_id should already be from cookie via auth_user)
                match_id = message_data.get("match_id", "")
                message_content = message_data.get("message", "")

                # Forward to Collab
                message_to_collab = json.dumps(
                    {
                        "user_id": user_id,
                        "match_id": match_id,
                        "message": message_content,
                    }
                )
                await manager.send_to_collab(message_to_collab)

            except json.JSONDecodeError:
                log.error(f"Invalid JSON received from FE {user_id}: {data}")
                continue

    except WebSocketDisconnect:
        manager.disconnect(connection_id)
        await redis.delete(f"websocket:{connection_id}")
        log.info(f"FE client {user_id} disconnected")


@router.get("/ws/status")
async def websocket_status(redis: aioredis.Redis = Depends(get_redis)):
    """Get status of all WebSocket connections"""
    keys = await redis.keys("websocket:*")
    connections = {}

    for key in keys:
        conn_data = await redis.hgetall(key)
        connections[key] = conn_data

    return {
        "active_connections_count": len(manager.connections),
        "active_connection": connections,
    }
