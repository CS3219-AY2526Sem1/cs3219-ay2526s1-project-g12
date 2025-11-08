import asyncio
from datetime import datetime
import json
from redis.asyncio import Redis
import requests
from utils.logger import log
from utils.utils import get_envvar, format_user_room_key, format_heartbeat_key
import aiohttp 

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

ENV_QN_SVC_POOL_ENDPOINT = "QUESTION_SERVICE_POOL_URL"
ENV_QN_SVC_HISTORY_ENDPOINT = "QUESTION_SERVICE_HISTORY_URL"

TTL = 120 # We give them 2 minutes to respond

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
    # url = f"{get_envvar(ENV_QN_SVC_POOL_ENDPOINT)}/{match_data['category']}/{match_data['difficulty']}"

    # log.info(f"INFO: Sending request to {url}")

    # try:
    #     async with aiohttp.ClientSession(
    #         limit=100,
    #         limit_per_host=30,
    #         ttl_dns_cache=300,
    #         force_close=False,
    #         enable_cleanup_closed=True
    #     ) as session:
    #         async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as response:
    #             data = await response.text()
    # except Exception as e:
    #         log.info(f"ERROR: {e}")

    # try:
    #     response = requests.get(url, timeout=10)
    #     data = response.text
    # except Exception as e:
    #     log.info(f"ERROR: {e}")

    # try:
    #     data = json.loads(data)
    #     log.info(data)
    # except Exception as e:
    #     log.info("ERROR: Cannot convert to JSON")

    # Question data is already in a dictionary so append the rest of the details there
    # for key, value in match_data.items():
    #     data[key] = value

    match_data["start_time"] = str(datetime.now())
    # del(data["categories"])

    user_one_id = match_data["user_one"]
    user_one_key = format_user_room_key(user_one_id)
    user_one_heartbeat_key = format_heartbeat_key(user_one_id)

    user_two_id = match_data["user_two"]
    user_two_key = format_user_room_key(user_two_id)
    user_two_heartbeat_key = format_heartbeat_key(user_two_id)

    # Set up heartbeat for user 1 and 2
    await room_connection.set(user_one_heartbeat_key, str(datetime.now()), TTL)
    await room_connection.set(user_two_heartbeat_key, str(datetime.now()), TTL)

    await room_connection.hset(user_one_key, mapping= match_data)
    await room_connection.hset(user_two_key, mapping= match_data)

    log.info(f"Room has been created for match ID, {match_data["match_id"]}")

async def get_partner(user_id: str, room_key: str, room_connection: Redis) -> str:
    """
    Retrieves the user's partner user id for that room.
    """
    if (await room_connection.hget(room_key, "user_one") == user_id):
        return await room_connection.hget(room_key, "user_two")
    else:
        return await room_connection.hget(room_key, "user_one")

async def get_room_information(room_key: str, room_connection: Redis) -> dict:
    """
    Retrieves the room information.
    """
    return await room_connection.hgetall(room_key)

async def get_room_id(room_key: str, room_connection: Redis) -> str:
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

async def delete_user_ttl(heartbeat_key: str, room_connection: Redis) -> None:
    """
    Removes the time to live entry for the user.
    """
    await room_connection.delete(heartbeat_key)

async def add_room_cleanup(clean_up_key: str, user_id: str, room_connection: Redis) -> None:
    """
    Adds a room cleanup item inside redis which is to be checked for clean up.
    """
    await room_connection.set(clean_up_key, user_id)

async def remove_room_cleanup(cleanup_key: str, room_connection: Redis) -> None:
    """
    Remoeves the room cleanup item inside redis.
    """
    await room_connection.delete(cleanup_key)

async def check_room_cleanup(cleanup_key: str, room_connection: Redis) -> bool:
    """
    Adds if the room needs to be cleaned up.
    """
    result =  await room_connection.exists(cleanup_key)

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

def send_room_for_review(user_one: str, user_two: str, submitted_solution: str, room_infoamtion: dict) -> None:
        """
        Sends the room data to the question history service to be reviewed.
        """
        start_time = datetime.fromisoformat(room_infoamtion["start_time"])
        end_time = datetime.now()
        elapsed_seconds = int((end_time - start_time).total_seconds())

        # Formar the body for the HTTP request
        body = {
            "title" : room_infoamtion["title"],
            "description": room_infoamtion["description"],
            "code_template": room_infoamtion["code_template"],
            "solution_sample": room_infoamtion["solution_sample"],
            "difficulty": room_infoamtion["difficulty"],
            "category": room_infoamtion["category"],
            "time_elapsed": elapsed_seconds,
            "submitted_solution": submitted_solution,
            "users": [user_one, user_two]
        }

        r = requests.post(f"{get_envvar(ENV_QN_SVC_HISTORY_ENDPOINT)}", json= body)
        log.info("INFO: Match attempt sent to question history")

async def get_partner_name(room_key: str, user_id: str, room_connection: Redis) -> str:
    """
    Retrieves the question assigned to this room.
    """
    
    if (await room_connection.hget(room_key, "user_one") == user_id):
        return await room_connection.hget(room_key, "user_two_name")
    else:
        return await room_connection.hget(room_key, "user_one_name")

async def get_room_question(room_key: str, user_id: str, room_connection: Redis) -> dict:
    """
    Retrieves the question assigned to this room.
    """

    # The question has not been assigned yet
    if (not await room_connection.hexists(room_key, "id")):
        difficulty = await room_connection.hget(room_key, "difficulty")
        category = await room_connection.hget(room_key, "category")

        url = f"{get_envvar(ENV_QN_SVC_POOL_ENDPOINT)}/{category}/{difficulty}"
        log.info(f"INFO: Sending request to {url}")
        response = requests.get(url, timeout=10)

        data = response.json()
        log.info(f"INFO: Data received from question service, {data}")
        del(data["categories"])
        await room_connection.hset(room_key, mapping= data)

        #Set the question for the partner also
        partner = await get_partner(user_id, room_key, room_connection)
        partner_room_key = format_user_room_key(partner)
        await room_connection.hset(partner_room_key, mapping= data)

    question_data = {
        "title" : await room_connection.hget(room_key, "title"),
        "description": await room_connection.hget(room_key, "description"),
        "code_template": await room_connection.hget(room_key, "code_template"),
        "solution_sample": await room_connection.hget(room_key, "solution_sample"),
        "difficulty": await room_connection.hget(room_key, "difficulty"),
        "category": await room_connection.hget(room_key, "category")
    }

    return question_data
