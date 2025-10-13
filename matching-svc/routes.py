from contextlib import asynccontextmanager
from controllers.matching_controller import find_match, check_redis_connection
from fastapi import FastAPI
from models.api_models import MatchRequest
from service.redis_message_service import connect_to_redis_message_queue
from service.redis_queue_service import connect_to_redis_queue
from utils.logger import log
from utils.utils import sever_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the matching service.
    """
    app.state.redis_queue = connect_to_redis_queue()
    app.state.redis_message_queue = connect_to_redis_message_queue()
    log.info("Matching service is Up.")
    yield
    # This is the shut down procedure when the matching service stops.
    log.info("Matching service shutting down.")
    await sever_connection(app.state.redis_queue)
    await sever_connection(app.state.redis_message_queue)
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "success"}

@app.get("/check_connection/queue")
async def check_connection():
    return check_redis_connection(app.state.redis_queue)

@app.get("/check_connection/message_queue")
async def check_connection():
    return check_redis_connection(app.state.redis_message_queue)

@app.post("/find_match")
async def match(match_request: MatchRequest):
    return  await find_match(match_request, app.state.redis_queue, app.state.redis_message_queue )