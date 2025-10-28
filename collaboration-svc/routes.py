import asyncio
from contextlib import asynccontextmanager
from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)
from controllers.room_controller import create_listener
from models.WebSocketManager import WebSocketManager
from services.redis_event_queue import connect_to_redis_event_queue
from services.redis_room_service import connect_to_redis_room_service
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from utils.logger import log
from utils.utils import sever_connection, get_envvar

FRONT_END_URL = get_envvar("FRONT_END_URL")

ADMIN_ROLE = "admin"
USER_ROLE = "user"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the collaboration service.
    """
    app.state.event_queue_connection = connect_to_redis_event_queue()
    app.state.room_connection = connect_to_redis_room_service()
    app.state.websocket_manager = WebSocketManager() 

    stop_event = asyncio.Event()
    listener = asyncio.create_task(create_listener(app.state.event_queue_connection, app.state.room_connection, stop_event))

    register_self_as_service(app)
    hc_task = register_heartbeat()
    yield
    # This is the shut down procedure when the collaboration service stops.
    stop_event.set()

    if (listener and not listener.done()):
        await listener

    await sever_connection(app.state.event_queue_connection)
    await sever_connection(app.state.room_connection)

    log.info("Collaboration service shutting down.")
    hc_task.cancel()

app = FastAPI(title="PeerPrep Collaboration Service", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "working"}
