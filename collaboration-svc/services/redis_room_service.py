from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_PORT"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis_room_service() -> Redis:
    """
    Establishes a connection with redis room service.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to the event queue")
    return Redis(host=host, port=redis_port, decode_responses=True, db=0)
