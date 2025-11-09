from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

async def connect_to_redis_matchmaking_service() -> Redis:
    """
    Establishes a connection with redis queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    try:
        client = Redis(
            host=host,
            port=int(redis_port),
            decode_responses=True,
            db=0,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30
        )
        
        await client.ping()
        log.info("Connected to redis Match Making service.")
        return client
    except Exception as e:
        log.error(f"Failed to connect to Redis Match Making: {e}")
        raise
    
async def add_user_queue_details(key: str, difficulty: str, category: str, matchmaking_conn: Redis) -> None:
    """
    Adds the user into the set of queued users.\n
    """
    mapping = {
        "difficulty": difficulty,
        "category": category,
        "match_found": 0
    }

    await matchmaking_conn.hset(key, mapping=mapping)

async def check_user_in_any_queue(key: str, matchmaking_conn: Redis) -> bool:
    """
    Checks if the user is in any of the queues.\n
    """
    does_exist = await matchmaking_conn.exists(key)

    if (does_exist == 1):
        return True
    else:
        return False

async def check_user_found_match(key: str, matchmaking_conn: Redis) -> bool:
    """
    Checks if the user has currently found a match.\n
    """
    has_found_match = await matchmaking_conn.hget(key, "match_found")

    if (has_found_match == "1"):
        return True
    else:
        return False

async def update_user_match_found_status(key: str, matchmaking_conn: Redis) -> None:
    """
    Updates the users status to be that they have found a match.
    """
    await matchmaking_conn.hset(key, mapping={"match_found": 1})

async def remove_user_queue_details(key: str, matchmaking_conn: Redis) -> None:
    """
    Removes the user from the set of queued users.\n
    """
    await matchmaking_conn.delete(key)

async def find_user_in_queue(user_id: str, key:str,  matchmaking_conn: Redis) -> int:
    """
    Finds the user in the queue based on the key and return the index. If the user is no in the queue \n
    return none.
    """
    index = await  matchmaking_conn.lpos(key, user_id)
    return index

async def get_user_queue_details(key: str, matchmaking_conn: Redis) -> dict:
    """
    Retrieves the queue details of the user.
    """
    return  await matchmaking_conn.hgetall(key)

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
    user_id = await matchmaking_conn.lpop(key)
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
