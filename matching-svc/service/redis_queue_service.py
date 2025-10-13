from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

QUEUED_STATUS_SET_KEY = "queued-users"

def connect_to_redis_queue() -> Redis:
    """
    Establishes a connection with redis queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to redis queue server.")
    return Redis(host=host, port=redis_port, decode_responses=True, db=0)

async def add_to_queued_users_set(user_id: str, queue_connection: Redis) -> bool:
    """
    Adds the user into the set of queued users.\n
    Returns true if the user has been added and false if they are already in the set.
    """
    is_added = await queue_connection.sadd(QUEUED_STATUS_SET_KEY, user_id)

    if (is_added == 1):
        log.info(f"User id, {user_id} queued status has been added.")
        return True
    else:
        log.info(f"User id, {user_id} is already in the queue.")
        return False

async def acquire_lock(user_id:str, key:str, queue_connection:Redis) -> Lock:
    """
    Attempts to acquire the lock and will be blocked it is being used by someone else.
    """
    # This lock will be sync accross all match-svc instances as long as the key used is the same
    # timeout = safety fallback, given 2 mins
    lock = Lock(queue_connection, key, timeout=120)
    await  lock.acquire()
    log.info(f"User id, {user_id} has acquired the lock with key: {key}. ")

    return lock

async def release_lock(user_id:str, lock:Lock) -> None:
    """
    Releases the acquired lock.
    """
    key = lock.name
    await lock.release()
    log.info(f"User id, {user_id} has released the lock with key: {key} .")

async def remove_from_queued_users_set(user_id: str, queue_connection: Redis) -> None:
    """
    Removes the user from the set of queued users.\n
    """
    await queue_connection.srem(QUEUED_STATUS_SET_KEY, user_id)
    log.info(f"User id, {user_id} queue status has been removed.")

async def enqueue_user(user_id: str, key:str,  queue_connection: Redis) -> None:
    """
    Adds the user into the queue based on the key.
    """
    await queue_connection.rpush(key, user_id)
    log.info(f"User id, {user_id} has been added into the queue with the key: {key}.")

async def dequeue_user(user_id: str, key:str,  queue_connection: Redis) -> None:
    """
    Removes the user from the queue based on the key.
    """
    await queue_connection.lrem(key, 1, user_id)
    log.info(f"User id, {user_id} has been removed from the queue: {key}.")

async def get_next_user(key:str, queue_connection: Redis) -> str:
    """
    Retrieves the next person in the queue based on the key.
    """
    user_id = await queue_connection.lpop(key);
    log.info(f"User id, {user_id} has been removed from the queue: {key}.")
    return user_id

async def find_partner(key:str, queue_connection: Redis) -> str:
    """
    Based on the difficulty and category fetch the next person in the queue.\n
    """
    length = await queue_connection.llen(key) 
    if (length > 0):
        user_id = await get_next_user(key, queue_connection)
        return user_id
    else:
        # Means there is no one in the queue
        return ""