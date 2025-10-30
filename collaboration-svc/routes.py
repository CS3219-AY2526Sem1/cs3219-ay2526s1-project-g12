import asyncio
from contextlib import asynccontextmanager
from controllers.heartbeat_controller import (
    INSTANCE_ID,
    register_heartbeat,
    register_self_as_service,
)
from controllers.room_controller import create_room_listener, create_ttl_expire_listener, terminate_match, remove_user
from controllers.websocket_controller import WebSocketManager
from fastapi import FastAPI, Header
from models.api_models import MatchData
from services.redis_event_queue import connect_to_redis_event_queue
from services.redis_room_service import connect_to_redis_room_service
from typing import Annotated
from utils.logger import log
from utils.utils import sever_connection, get_envvar

FRONT_END_URL = get_envvar("FRONT_END_URL")

ADMIN_ROLE = "admin"
USER_ROLE = "user"

ENV_REDIS_STREAM_KEY = "REDIS_STREAM_KEY"
ENV_REDIS_GROUP_KEY = "REDIS_GROUP"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the collaboration service.
    """
    app.state.event_queue_connection = connect_to_redis_event_queue()
    app.state.room_connection = await connect_to_redis_room_service()
    app.state.websocket_manager = WebSocketManager() 

    stop_event = asyncio.Event()
    room_listener = asyncio.create_task(create_room_listener(app.state.event_queue_connection, app.state.room_connection, stop_event))
    expired_ttl_listener = asyncio.create_task(create_ttl_expire_listener(INSTANCE_ID, app.state.event_queue_connection, app.state.room_connection, app.state.websocket_manager, stop_event))

    register_self_as_service(app)
    hc_task = register_heartbeat()

    yield
    # This is the shut down procedure when the collaboration service stops.
    stop_event.set()

    if (room_listener and not room_listener.done()):
        await room_listener

    if (expired_ttl_listener and not expired_ttl_listener.done()):
        await expired_ttl_listener

    await sever_connection(app.state.event_queue_connection)
    await sever_connection(app.state.room_connection)

    log.info("Collaboration service shutting down.")
    hc_task.cancel()

app = FastAPI(title="PeerPrep Collaboration Service", lifespan=lifespan)

@app.get("/")
async def root() -> dict:
    return {"status": "working"}

@app.post("/reconnect", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def reconnect_user_to_match(x_user_id: Annotated[str, Header()]) -> dict:
    await reconnect_user(x_user_id, app.state.room_connection, app.state.websocket_manager)
    return {"message": "Reconnecting user"}

@app.post("/exit", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def user_exit_match(x_user_id: Annotated[str, Header()]) -> dict:
    await remove_user(x_user_id, app.state.room_connection, app.state.websocket_manager)
    return {"message": "Exit match"}

@app.post("/terminate/{room_id}", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def terminate_user_match(room_id: str, match_data: MatchData, x_user_id: Annotated[str, Header()]) -> dict:
    await terminate_match(x_user_id, room_id, match_data, app.state.room_connection)
    return {"message": "match has been terminated"}
