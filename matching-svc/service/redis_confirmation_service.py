from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis_confirmation_service() -> Redis:
    """
    Establishes a connection with redis message queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to redis messaging server.")
    return Redis(host=host, port=redis_port, decode_responses=True, db=2)

async def setup_match_confirmation(match_key: str, user_one: str, user_two: str, difficulty: str, category: str, confirmation_conn: Redis) -> None:
    """
    Creates a match confirmation table in redis to keep track on who has and has not comfirm their match.
    """
    mapping = {
        "user_one_confirmation": 0,
        "user_two_confirmation": 0,
        "user_one": user_one,
        "user_two": user_two,
        "difficulty": difficulty,
        "category": category,
    }

    await confirmation_conn.hset(match_key, mapping = mapping)

async def check_match_exist(match_key: str, confirmation_conn: Redis) -> bool:
    """
    Checks if a match with the corrosponding match id exists.
    """
    return await confirmation_conn.exists(match_key)

async def check_match_user(user_id: str, match_key: str, confirmation_conn: Redis) -> bool:
    """
    Checks if the user belongs to this corrosponding match.
    """
    is_user_one = await confirmation_conn.hget(match_key, "user_one") == user_id
    is_user_two = await confirmation_conn.hget(match_key, "user_two") == user_id
    if (is_user_one or is_user_two ):
        return True
    else:
        return False

async def get_match_details(match_key: str, confirmation_conn: Redis) -> dict:
    """
    Retrieves the information of the match.
    """
    return await confirmation_conn.hgetall(match_key)

async def get_match_partner(user_id: str, match_key: str, confirmation_conn: Redis) -> bool:
    """
    Retrieves the user's partner user id for that match.
    """
    if (await confirmation_conn.hget(match_key, "user_one") == user_id):
        return await confirmation_conn.hget(match_key, "user_two")
    else:
        return await confirmation_conn.hget(match_key, "user_one")

async def update_user_confirmation(match_key: str, user_id: str, confirmation_conn: Redis) -> None:
    """
    Updates the comfirmation status of the user based on the given match id.
    """
    
    if (await confirmation_conn.hget(match_key, "user_one") == user_id):
        await confirmation_conn.hset(match_key,  mapping={"user_one_confirmation": 1})
    else:
        await confirmation_conn.hset(match_key,  mapping={"user_two_confirmation": 1})

    log.info(f"User id, {user_id} has comfirm {match_key}.")
    
async def delete_match_record(match_key: str, confirmation_conn: Redis) -> None:
    """
    Removes the match record from the redis server.
    """    
    await confirmation_conn.delete(match_key)

async def is_match_confirmed(match_key: str, confirmation_conn: Redis) -> bool:
    """
    Checks if both users have accepted the match.
    """
    has_user_one_comfirm = await confirmation_conn.hget(match_key, "user_one_confirmation") == "1"
    has_user_two_comfirm = await confirmation_conn.hget(match_key, "user_two_confirmation") == "1"

    if ( has_user_one_comfirm and has_user_two_comfirm):
        return True
    else:
        return False
