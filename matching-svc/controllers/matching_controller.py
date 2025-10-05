from models.api_models import MatchRequest
from models.queue_models import QueueManager
from models.websocket_models import WebsocketConnectionManager
from redis import Redis
from service.redis_service import check_redis_availability, enqueue_user, update_match_response
from utils.utils import get_envvar

ENV_FASTAPI_PORT_KEY = "FASTAPI_PORT"

def ping_redis_server(redis_connection: Redis) -> dict:
    """
    Ping the redis server and check if it is responding.
    """
    response: bool = check_redis_availability(redis_connection)
    if (response):
        return {"redis_status": "up"}
    else:
        return {"redis_status": "down"}

def fetch_fastapi_websocket_url() -> dict:
    """
    Returns the websocket_url.
    """
    fastapi_port = get_envvar(ENV_FASTAPI_PORT_KEY)
    # TODO: Change localhost to the actual IP address of the matching service during deployment
    ws_url = f"ws://localhost:{fastapi_port}/ws"
    return  {"ws_url": ws_url}

async def add_user(user: MatchRequest, redis_connection: Redis, websocket_manager: WebsocketConnectionManager, queue_manager: QueueManager) -> dict:
    """
    Adds the user into the queue based on their difficulty and category.
    """
    response = enqueue_user(user.user_id, user.difficulty, user.category, redis_connection)
    await queue_manager.spawn_new_worker(user.difficulty, user.category, redis_connection, websocket_manager)
    return response

def confirm_match(match_id: str, user_id: str, redis_connection: Redis) -> dict:
    """
    Adds the user into the queue based on their.
    """
    update_match_response(match_id, user_id, redis_connection)
    return {"status": "success"}
    