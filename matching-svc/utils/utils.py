from dotenv import load_dotenv
import os
from redis.asyncio import Redis

def get_envvar(var_name: str) -> str:
    load_dotenv()
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value

async def sever_connection(redis_connection: Redis):
    """
    Closes a connection with redis.
    """
    await redis_connection.close()

async def ping_redis_server(redis_connection: Redis) -> bool:
    """
    Pings the redis server to check if it is responding.
    """
    return await redis_connection.ping()

def format_queue_key(difficulty:str, category:str) -> str:
    """
    Formats the difficulty and category into a key to be used in the queue.
    """
    key = f"queue:{difficulty}:{category}"
    return key

def format_lock_key(difficulty:str, category:str) -> str:
    """
    Formats the difficulty and category into a key to be used as a lock.
    """
    key = f"lock:{difficulty}:{category}"
    return key

def format_match_found_key(user_id: str) -> str:
    """
    Formats the message key when a match is found.
    """
    key = f"match:{user_id}"
    return key