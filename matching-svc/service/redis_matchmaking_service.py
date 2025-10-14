from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from utils.logger import log
from utils.utils import get_envvar, format_match_ley

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

QUEUED_STATUS_SET_KEY = "queued-users"

def connect_to_redis_matchmaking_service() -> Redis:
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

async def setup_match_comfirmation(match_id: str, user_one: str, user_two: str, difficulty: str, category: str, queue_connection: Redis) -> None:
    """
    Creates a match comfirmation table in redis to keep track on who has and has not comfirm their match.
    """
    mapping = {
        "user_one_comfirmation": 0,
        "user_two_comfirmation": 0,
        "user_one": user_one,
        "user_two": user_two,
        difficulty: difficulty,
        category: category,
    }

    match_key = format_match_ley(match_id)

    await queue_connection.hset(match_key, mapping = mapping)

async def check_match_exist(match_key: str, queue_connection: Redis) -> bool:
    """
    Checks if a match with the corrosponding match id exists.
    """
    return await queue_connection.exists(match_key)

async def check_match_user(user_id: str, match_key: str, queue_connection: Redis) -> bool:
    """
    Checks if the user belongs to this corrosponding match.
    """
    is_user_one = await queue_connection.hget(match_key, "user_one") == user_id
    is_user_two = await queue_connection.hget(match_key, "user_two") == user_id
    if (is_user_one or is_user_two ):
        return True
    else:
        return False

async def get_match_details(match_key: str, queue_connection: Redis) -> dict:
    """
    Retrieves the information of the match.
    """
    return await queue_connection.hgetall(match_key)

async def get_match_partner(user_id: str, match_key: str, queue_connection: Redis) -> bool:
    """
    Retrieves the user's partner user id for that match.
    """
    if (await queue_connection.hget(match_key, "user_one") == user_id):
        return await queue_connection.hget(match_key, "user_two")
    else:
        return await queue_connection.hget(match_key, "user_one")

async def update_user_comfirmation(match_key: str, user_id: str, queue_connection: Redis) -> None:
    """
    Updates the comfirmation status of the user based on the given match id.
    """
    
    if (await queue_connection.hget(match_key, "user_one") == user_id):
        await queue_connection.hset(match_key,  mapping={"user_one_comfirmation": 1})
    else:
        await queue_connection.hset(match_key,  mapping={"user_two_comfirmation": 1})

    log.info(f"User id, {user_id} has comfirm match.")
    
async def delete_match_record(match_key: str, queue_connection: Redis) -> None:
    """
    Removes the match record from the redis server.
    """    
    await queue_connection.delete(match_key)

async def is_match_comfirmed(match_key: str, queue_connection: Redis) -> bool:
    """
    Checks if both users have accepted the match.
    """
    has_user_one_comfirm = await queue_connection.hget(match_key, "user_one_comfirmation") == "1"
    has_user_two_comfirm = await queue_connection.hget(match_key, "user_two_comfirmation") == "1"

    if ( has_user_one_comfirm and has_user_two_comfirm):
        return True
    else:
        return False
