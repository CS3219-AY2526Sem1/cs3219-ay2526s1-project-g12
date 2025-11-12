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

async def acquire_lock(key:str, redis_connection:Redis) -> Lock:
    """
    Attempts to acquire the lock and will be blocked it is being used by someone else.
    """
    # This lock will be sync accross all match-svc instances as long as the key used is the same
    # timeout = safety fallback, given 2 mins
    lock = Lock(redis_connection, key, timeout=60)
    await  lock.acquire()

    return lock

async def release_lock(lock:Lock) -> None:
    """
    Releases the acquired lock.
    """
    await lock.release()

def format_in_queue_key(user_id:str) -> str:
    """
    Formats the user id into a key to be used to identify if the user is in any queue or not.
    """
    key = f"inqueue:{user_id}"
    return key

def format_queue_key(difficulty:str, category:str) -> str:
    """
    Formats the difficulty and category into a key to be used for matchmaking.
    """
    key = f"queue:{difficulty}:{category}"
    return key

def format_lock_key(key: str) -> str:
    """
    Formats the given key into a key to be used as a lock.
    """
    key = f"lock:{key}"
    return key

def format_match_found_key(user_id: str) -> str:
    """
    Formats the message key when a match is found.
    """
    key = f"match_found:{user_id}"
    return key

def format_match_key(match_id: str) -> str:
    """
    Formats the match key for the match details.
    """
    key = f"match:{match_id}"
    return key

def format_match_accepted_key(user_id: str) -> str:
    """
    Formats the message key when the matchmaking has been confirmed by both users.
    """
    key = f"match_confirm:{user_id}"
    return key
