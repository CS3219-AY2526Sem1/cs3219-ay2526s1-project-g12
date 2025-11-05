from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis_message_service() -> Redis:
    """
    Establishes a connection with redis message queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to redis messaging server.")
    return Redis(host=host, port=redis_port, decode_responses=True, db=1)

async def send_match_found_message(message_key: str, match_id: str, message_conn:Redis) -> None:
    """
    Sends a message to the user that a match as been found with the corrosponding match id.
    """
    await message_conn.rpush(message_key, match_id)

async def send_match_finalised_message(message_key: str, collab_svc_data: str, message_conn:Redis) -> None:
    """
    Sends a message to the user that both parties have accepted the match and it has been finalised.
    """
    await message_conn.rpush(message_key, collab_svc_data)

async def send_match_terminated_message(message_key: str, message_conn:Redis) -> None:
    """
    Sends a message to the user that his match has been successfully terminated.
    """
    await message_conn.rpush(message_key, "terminate")

async def send_new_request_message(message_key: str, message_conn:Redis) -> None:
    """
    Sends a message to the old request that a new request has been made.
    """
    await message_conn.rpush(message_key, "new request made")

async def wait_for_message(message_key: str, message_conn: Redis, timeout: int = 180) -> list:
    """
    Waits for a message to be sent based on the key. If no message is sent after the timeout,
    then return None
    """
    message =  await message_conn.blpop(message_key, timeout= timeout) # Timeout 3 Minutes
    return message
