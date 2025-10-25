from redis.asyncio import Redis
import requests
from utils.logger import log
from utils.utils import get_envvar, format_room_key

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

ENV_QN_SVC_POOL_ENDPOINT = "QUESTION_SERVICE_POOL_URL"

def connect_to_redis_room_service() -> Redis:
    """
    Establishes a connection with redis room service.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to the event queue")
    return Redis(host=host, port=redis_port, decode_responses=True, db=0)

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

    await room_connection.hset(room_key, mapping= data)
    log.info(f"Room has been created for match ID, {match_data["match_id"]}")
