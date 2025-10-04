from models.api_models import MatchRequest
from models.websocket_models import WebsocketConnectionManager
from redis import Redis
from service.redis_service import check_redis_availability, check_queue, enqueue_user, dequeue_user
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

def add_user(user: MatchRequest, redis_connection: Redis, manager: WebsocketConnectionManager) -> dict:
    """
    Checks if there is a person queueing with the same topic, otherwise add them to the queue.
    """
    enqueue_user(user.user_id, user.difficulty, user.category, redis_connection)

def remove_user(user: MatchRequest, redis_connection: Redis, manager: WebsocketConnectionManager) -> None:
    """
    Removes the user from the queue that they are in.
    """
    dequeue_user(user.user_id, user.difficulty, user.category, redis_connection)
    manager.disconnect(user.user_id)

def alert_user(user_id: str, manager: WebsocketConnectionManager):
    """
    Send a message to the user through the websocket connection that a match has been found.
    """
    manager.send_to_player(user_id, "A match has been found")