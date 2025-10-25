from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

MATCH_CONFIRMATION_EVENT_KEY = "create_room"

def connect_to_redis_event_queue() -> Redis:
    """
    Establishes a connection with redis room service.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to event queue")
    return Redis(host=host, port=redis_port, decode_responses=True, db=1)

async def get_match_confirmation_event(event_queue_connection: Redis) -> dict:
    """
    Retrieves a match confirmation event from the event queue.
    """
    return await event_queue_connection.hgetall(MATCH_CONFIRMATION_EVENT_KEY)

async def remove_match_confirmation_event(event_queue_connection: Redis) -> None:
    """
    Removes the match confirmation event log from the event queue.
    """
    await event_queue_connection.delete(MATCH_CONFIRMATION_EVENT_KEY)
