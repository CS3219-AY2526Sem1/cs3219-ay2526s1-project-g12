from datetime import datetime
from redis.asyncio import Redis
import requests
from utils.logger import log
from utils.utils import get_envvar, format_room_key, format_heartbeat_key

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

ENV_QN_SVC_POOL_ENDPOINT = "QUESTION_SERVICE_POOL_URL"

TTL = 5 # We give them 2 minutes to respond

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
    room_key = format_room_key(match_data["match_id"])

    response = requests.get(f"{get_envvar(ENV_QN_SVC_POOL_ENDPOINT)}/{match_data["category"]}/{match_data["difficulty"]}")
    data = response.json()

    # Question data is already in a dictionary so append the rest of the details there
    for key, value in match_data.items():
        data[key] = value
    
    del data["categories"]

    match_id = match_data["match_id"]

    user_one_id = match_data["user_one"]
    user_one_heartbeat_key = format_heartbeat_key(user_one_id, match_id)
    user_two_id = match_data["user_two"]
    user_two_heartbeat_key = format_heartbeat_key(user_two_id, match_id)

    # Set up heartbeat for user 1 and 2
    await room_connection.set(user_one_heartbeat_key, str(datetime.now()), TTL)
    await room_connection.set(user_two_heartbeat_key, str(datetime.now()), 10)

    await room_connection.hset(room_key, mapping= data)
    log.info(f"Room has been created for match ID, {match_data["match_id"]}")

async def get_partner(user_id: str, room_key: str, room_connection: Redis) -> bool:
    """
    Retrieves the user's partner user id for that room.
    """
    if (await room_connection.hget(room_key, "user_one") == user_id):
        return await room_connection.hget(room_key, "user_two")
    else:
        return await room_connection.hget(room_key, "user_one")

async def is_user_alive(heartbeat_key: str, room_connection: Redis) -> bool:
    """
    Checks if the user's heartbeat is still active if not return false.
    """
    is_alive = await room_connection.exists(heartbeat_key)
    if is_alive:
        return True
    else:
        return False
