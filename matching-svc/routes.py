from contextlib import asynccontextmanager
from controllers.matching_controller import ping_redis_server, fetch_fastapi_websocket_url,  add_user, confirm_match
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models.api_models import MatchRequest
from models.queue_models import  QueueManager
from models.websocket_models import WebsocketConnectionManager
from service.redis_service import connect_to_redis, sever_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the matching service.
    """
    app.state.redis_connection = connect_to_redis()
    app.state.websocket_manager = WebsocketConnectionManager()
    app.state.queue_manager = QueueManager()
    yield
    # This is the shut down procedure when the matching service stops.
    sever_connection(app.state.redis_connection)
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "success"}

@app.get("/check_connection")
async def check_connection():
    """
    Check if the redis server is up and responding.
    """
    return ping_redis_server(app.state.redis_connection)

@app.get("/get_ws_url")
async def get_ws_url():
    """
    Fetches the websocket URL for the user.
    """
    return fetch_fastapi_websocket_url()

@app.post("/enter_matchmaking")
async def enter(request: MatchRequest):
    """
    Adds the user into the queue based on the user's citeria.
    """
    return await add_user(request, app.state.redis_connection, app.state.websocket_manager, app.state.queue_manager)

@app.post("/confirm_match/{match_id}/{user_id}")
async def comfirm(match_id: str, user_id: str):
    """
    Comfirms the match.
    """
    return confirm_match(match_id, user_id, app.state.redis_connection)

@app.websocket("/ws/{user_id}")
async def establish_websocket(websocket: WebSocket, user_id: str):
    """
    Upgrades the HTTP request to a websocket.
    """
    manager = app.state.websocket_manager
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text() 
    except WebSocketDisconnect:
        # If the websocket disconnects midway through then we will remove it from our manager
        manager.disconnect(user_id)