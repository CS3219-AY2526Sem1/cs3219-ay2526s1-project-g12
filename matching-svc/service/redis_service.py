from redis import Redis
from utils.utils import get_envvar

ENV_REDIS_PORT_KEY = "REDIS_PORT"

# Establish a connection with redis using localhost
def connect_to_redis() -> Redis:
    """
    Establish a connection with redis using localhost.
    """
    # decode_responses = True is to allow redis to automatically decode responses
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    return Redis(host='localhost', port=redis_port, decode_responses=True)