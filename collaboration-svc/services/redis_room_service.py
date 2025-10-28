from datetime import datetime
from redis.asyncio import Redis
import requests
from utils.logger import log
from utils.utils import get_envvar, format_user_room_key, format_heartbeat_key

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

ENV_QN_SVC_POOL_ENDPOINT = "QUESTION_SERVICE_POOL_URL"

TTL = 10 # We give them 2 minutes to respond

async def connect_to_redis_room_service() -> Redis:
    """
    Establishes a connection with redis room service.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses

    redis =  Redis(host=host, port=redis_port, decode_responses=True, db=0)
    # Configure redis so that expired keys will be sent as a event within redis
    await redis.config_set('notify-keyspace-events', 'Ex')
    return redis

async def create_room(match_data: dict, room_connection: Redis) -> None:
    """
    Creates a room given the match data received.
    """
    response = requests.get(f"{get_envvar(ENV_QN_SVC_POOL_ENDPOINT)}/{match_data["category"]}/{match_data["difficulty"]}")
    data = response.json()

    # Question data is already in a dictionary so append the rest of the details there
    for key, value in match_data.items():
        data[key] = value
    
    del data["categories"]

    user_one_id = match_data["user_one"]
    user_one_key = format_user_room_key(user_one_id)
    user_one_heartbeat_key = format_heartbeat_key(user_one_id)

    user_two_id = match_data["user_two"]
    user_two_key = format_user_room_key(user_two_id)
    user_two_heartbeat_key = format_heartbeat_key(user_two_id)

    # Set up heartbeat for user 1 and 2
    await room_connection.set(user_one_heartbeat_key, str(datetime.now()), TTL)
    await room_connection.set(user_two_heartbeat_key, str(datetime.now()), TTL)

    await room_connection.hset(user_one_key, mapping= data)
    await room_connection.hset(user_two_key, mapping= data)

    log.info(f"Room has been created for match ID, {match_data["match_id"]}")

async def get_partner(user_id: str, room_key: str, room_connection: Redis) -> bool:
    """
    Retrieves the user's partner user id for that room.
    """
    if (await room_connection.hget(room_key, "user_one") == user_id):
        return await room_connection.hget(room_key, "user_two")
    else:
        return await room_connection.hget(room_key, "user_one")

async def get_room_id(room_key: str, room_connection: Redis) -> bool:
    """
    Retrieves the user's partner user id for that room.
    """
    return await room_connection.hget(room_key, "match_id")

async def is_user_alive(heartbeat_key: str, room_connection: Redis) -> bool:
    """
    Checks if the user's heartbeat is still active if not return false.
    """
    is_alive = await room_connection.exists(heartbeat_key)
    if is_alive:
        return True
    else:
        return False

async def update_user_ttl(heartbeat_key: str, room_connection: Redis) -> None:
    """
    Refreshes the time to live for the user.
    """
    await room_connection.set(heartbeat_key, str(datetime.now()), TTL)

async def add_room_cleanup(clean_up_key: str, user_id: str, room_connection: Redis) -> None:
    """
    Adds a room cleanup item inside redis which is to be checked for clean up.
    """
    await room_connection.set(clean_up_key, user_id)

async def remove_room_cleanup(clean_up_key: str, room_connection: Redis) -> None:
    """
    Remoeves the room cleanup item inside redis.
    """
    await room_connection.delete(clean_up_key)

async def check_room_cleanup(clean_up_key: str, room_connection: Redis) -> bool:
    """
    Adds if the room needs to be cleaned up.
    """
    result =  await room_connection.exists(clean_up_key)

    if (result == 1):
        return True
    else:
        return False

async def cleanup(clean_up_key: str, room_connection: Redis ) -> None:
    """
    Cleans up redis of all the room data based on the room id.
    """
    user_id = await room_connection.get(clean_up_key)
    user_room_key = format_user_room_key(user_id)

    partner_id = await get_partner(user_id, user_room_key, room_connection)
    partner_room_key = format_user_room_key(partner_id)

    pipe =  room_connection.pipeline()
    pipe.delete(user_room_key)
    pipe.delete(partner_room_key)
    pipe.delete(clean_up_key)
    await pipe.execute()
