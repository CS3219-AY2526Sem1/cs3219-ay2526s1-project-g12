from contextlib import asynccontextmanager
from controllers.matching_controller import find_match, check_redis_connection, confirm_match, terminate_match
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.api_models import MatchRequest, MatchConfirmRequest
from service.redis_confirmation_service import connect_to_redis_confirmation_service
from service.redis_message_service import connect_to_redis_message_service
from service.redis_matchmaking_service import connect_to_redis_matchmaking_service
from utils.logger import log
from utils.utils import sever_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the matching service.
    """
    app.state.redis_matchmaking_service = connect_to_redis_matchmaking_service()
    app.state.redis_message_service = connect_to_redis_message_service()
    app.state.redis_confirmation_service = connect_to_redis_confirmation_service()
    log.info("Matching service is Up.")
    yield
    # This is the shut down procedure when the matching service stops.
    log.info("Matching service shutting down.")
    await sever_connection(app.state.redis_matchmaking_service)
    await sever_connection(app.state.redis_message_service)
    await sever_connection(app.state.redis_confirmation_service)
    
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return  await find_match(match_request, app.state.redis_matchmaking_service, app.state.redis_message_service, app.state.redis_confirmation_service)

@app.delete("/terminate_match")
async def terminate(cancle_request: MatchRequest):
    return await terminate_match(cancle_request, app.state.redis_matchmaking_service, app.state.redis_message_service)

@app.post("/confirm_match/{match_id}")
async def confirm_user_match(match_id: str, confirm_request: MatchConfirmRequest):
    return await confirm_match(match_id, confirm_request, app.state.redis_matchmaking_service, app.state.redis_message_service,  app.state.redis_confirmation_service)
