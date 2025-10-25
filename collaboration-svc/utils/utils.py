from dotenv import load_dotenv
import os
from redis.asyncio import Redis
from redis.asyncio.lock import Lock

def get_envvar(var_name: str) -> str:
    load_dotenv()
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set.")
    return value

async def sever_connection(redis_connection: Redis):
    """
    Closes the connection with redis.
    """
    await redis_connection.close()

async def ping_redis_server(redis_connection: Redis) -> bool:
    """
    Pings the redis server to check if it is responding.
    """
    return await redis_connection.ping()

async def acquire_lock(key: str, redis_connection: Redis) -> Lock:
    """
    Attempts to acquire the lock and will be blocked it is being used by someone else.
    """
    lock = Lock(redis_connection, key, timeout=10) # Timeout to prevent deadlocks
    await  lock.acquire()

    return lock

async def release_lock(lock: Lock) -> None:
    """
    Releases the acquired lock.
    """
    await lock.release()

def format_room_key(match_id: str) -> str:
    """
    Formats the room key given the match_id.
    """
    key = f"room:{match_id}"
    return key
