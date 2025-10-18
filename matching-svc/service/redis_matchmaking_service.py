from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

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

async def add_to_queued_users_set(user_id: str, matchmaking_conn: Redis) -> bool:
    """
    Adds the user into the set of queued users.\n
    Returns true if the user has been added and false if they are already in the set.
    """
    is_added = await matchmaking_conn.sadd(QUEUED_STATUS_SET_KEY, user_id)

    if (is_added == 1):
        log.info(f"User id, {user_id} queued status has been added.")
        return True
    else:
        return False

async def check_in_queued_users_set(user_id: str, matchmaking_conn: Redis) -> bool:
    """
    Checks if the user is in any of the queues.\n
    """
    does_exist = await matchmaking_conn.sismember(QUEUED_STATUS_SET_KEY, user_id)

    if (does_exist == 1):
        return True
    else:
        return False

async def remove_from_queued_users_set(user_id: str, matchmaking_conn: Redis) -> None:
    """
    Removes the user from the set of queued users.\n
    """
    await matchmaking_conn.srem(QUEUED_STATUS_SET_KEY, user_id)
    log.info(f"User id, {user_id} queue status has been removed.")

async def find_user_in_queue(user_id: str, key:str,  matchmaking_conn: Redis) -> int:
    """
    Finds the user in the queue based on the key and return the index. If the user is no in the queue \n
    return none.
    """
    index = await  matchmaking_conn.lpos(key, user_id)
    return index

async def enqueue_user(user_id: str, key:str,  matchmaking_conn: Redis) -> None:
    """
    Adds the user into the queue based on the key.
    """
    await matchmaking_conn.rpush(key, user_id)
    log.info(f"User id, {user_id} has been added into the queue with the key: {key}.")

async def dequeue_user(user_id: str, key:str,  matchmaking_conn: Redis) -> None:
    """
    Removes the user from the queue based on the key.
    """
    await matchmaking_conn.lrem(key, 1, user_id)
    log.info(f"User id, {user_id} has been removed from the queue: {key}.")

async def get_next_user(key:str, matchmaking_conn: Redis) -> str:
    """
    Retrieves the next person in the queue based on the key.
    """
    user_id = await matchmaking_conn.lpop(key);
    log.info(f"User id, {user_id} has been removed from the queue: {key}.")
    return user_id

async def find_partner(key:str, matchmaking_conn: Redis) -> str:
    """
    Based on the difficulty and category fetch the next person in the queue.\n
    """
    length = await matchmaking_conn.llen(key) 
    if (length > 0):
        user_id = await get_next_user(key, matchmaking_conn)
        return user_id
    else:
        # Means there is no one in the queue
        return ""
