from redis import Redis
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis() -> Redis:
    """
    Establish a connection with redis using localhost.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    return Redis(host=host, port=redis_port, decode_responses=True)

def sever_connection(redis_connection: Redis):
    """
    Close a connection with redis.
    """
    redis_connection.close()

def check_redis_availability(redis_connection: Redis) -> bool:
    """
    Check if the redis server is up and responding.
    """
    return redis_connection.ping()

def enqueue_user(user_id: str, difficulty: str, category: str, redis_connection: Redis):
    """
    Equeue the user based on their difficulty and topic.
    """
    queue_key = f"queue:{difficulty}:{category}"
    redis_connection.rpush(queue_key, user_id)