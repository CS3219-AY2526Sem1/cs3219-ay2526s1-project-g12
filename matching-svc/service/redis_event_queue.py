from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar, sever_connection

ENV_REDIS_HOST_KEY = "REDIS_EVENT_QUEUE_HOST"
ENV_REDIS_PORT_KEY = "REDIS_EVENT_QUEUE_PORT"

def connect_to_redis_event_queue() -> Redis:
    """
    Establishes a connection with redis event queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to event queue")
    return Redis(host=host, port=redis_port, decode_responses=True, db=1)

async def send_match_confirmed_event(match_id : str, user1: str, user1_name: str, user2: str, user2_name: str, difficulty: str, category: str) -> None:
    """
    Sends a event to the event queue to signal the collaboration service to create a room.
    """
    redis_connection = connect_to_redis_event_queue()

    data = {
        "match_id": match_id,
        "user_one": user1,
        "user_one_name": user1_name,
        "user_two": user2,
        "user_two_name": user2_name,
        "difficulty": difficulty,
        "category": category
    }

    await redis_connection.hset("create_room", mapping = data)
    await sever_connection(redis_connection)

    log.info("Match confirmed event has been sent")

