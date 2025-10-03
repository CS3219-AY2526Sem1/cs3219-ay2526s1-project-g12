from contextlib import asynccontextmanager
from controllers.matching_controller import ping_redis_server, find_match
from fastapi import FastAPI
from models.api_models import MatchRequest
from service.redis_service import connect_to_redis, sever_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the matching service.
    """
    app.state.redis = connect_to_redis()
    yield
    # This is the shut down procedure when the matching service stops.
    sever_connection(app.state.redis)
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "success"}

@app.get("/check/connection")
async def check_connection():
    """
    Check if the redis server is up and responding.
    """
    return ping_redis_server(app.state.redis)

@app.post("/find/match")
async def match(request: MatchRequest):
    """
    Find a match given the citera set. If no match is found then add them into the queue.
    """
    find_match(request, app.state.redis)
    return {"status": "success"}