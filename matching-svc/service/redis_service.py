from redis import Redis
from utils.utils import get_envvar, format_redis_queue_key

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

def check_queue(difficulty: str, category: str, redis_connection: Redis) -> bool:
    """
    Check if there is a person queueing with the given difficulty & category.\n
    Returns true if there is someone inside the queue.
    """
    queue_key = format_redis_queue_key(difficulty, category)
    queue_length = redis_connection.llen(queue_key)

    if (queue_length > 0):
        return True
    else:
        return False

def enqueue_user(user_id: str, difficulty: str, category: str, redis_connection: Redis) -> None:
    """
    Equeue the user based on their difficulty and category.
    """
    queue_key = format_redis_queue_key(difficulty, category)
    redis_connection.rpush(queue_key, user_id)

def dequeue_user(user_id: str, difficulty: str, category: str, redis_connection: Redis) -> None:
    """
    Dequeue the user from the queue they are in.
    """
    queue_key = format_redis_queue_key(difficulty, category)
    redis_connection.lrem(queue_key, 1, user_id)

def get_next_user(difficulty: str, category: str, redis_connection: Redis) -> None:
    """
    Get the next user in the queue based on the difficulty and category.
    """
    queue_key = format_redis_queue_key(difficulty, category)
    return redis_connection.lpop(queue_key)