from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis_comfirmation_service() -> Redis:
    """
    Establishes a connection with redis message queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to redis messaging server.")
    return Redis(host=host, port=redis_port, decode_responses=True, db=2)
