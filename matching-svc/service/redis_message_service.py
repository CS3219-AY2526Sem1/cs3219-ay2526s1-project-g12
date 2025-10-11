from redis.asyncio import Redis
from utils.logger import log
from utils.utils import get_envvar, format_match_found_key

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis_message_queue() -> Redis:
    """
    Establishes a connection with redis message queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    log.info("Connected to redis messaging server.")
    return Redis(host=host, port=redis_port, decode_responses=True, db=1)

async def send_match_found_message(user_id: str, match_id: str, message_queue_connection:Redis):
    """
    Sends a message to the user that a match as been found with the corrosponding match id.
    """
    message_key = format_match_found_key(user_id)
    log.info(f"Match found message has been sent for user id, {user_id}.")
    await message_queue_connection.rpush(message_key, match_id)
    