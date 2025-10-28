from redis.asyncio import Redis
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

MATCH_CONFIRMATION_EVENT_KEY = "create_room"

def connect_to_redis_event_queue() -> Redis:
    """
    Establishes a connection with the event queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    return Redis(host=host, port=redis_port, decode_responses=True, db=1)

async def get_match_confirmation_event(event_queue_connection: Redis) -> dict:
    """
    Retrieves a match confirmation event from the event queue.
    """
    return await event_queue_connection.hgetall(MATCH_CONFIRMATION_EVENT_KEY)

async def remove_match_confirmation_event(event_queue_connection: Redis) -> None:
    """
    Removes the match confirmation event log from the event queue.
    """
    await event_queue_connection.delete(MATCH_CONFIRMATION_EVENT_KEY)

async def create_group(event_queue_connection: Redis, stream_key: str, group_key: str) -> None:
    """
    Creates a group within redis streams given the stream key.
    """
    try:
    # Subscribe to this stream
        await event_queue_connection.xgroup_create(stream_key, group_key, id="$", mkstream=True)
    except Exception as e:
        # If any other error occur happens just raise an exception
        if "BUSYGROUP" not in str(e):
            raise e

async def retrieve_stream_data(event_queue_connection: Redis, stream_key: str, group_key: str, service_id: str) -> list:
    """
    Returns a event from the stream given the stream key. If there is no message it will return a empty list.
    """
    return await event_queue_connection.xreadgroup(group_key, service_id, {stream_key: ">"}, count=1)

async def acknowlwedge_event(event_queue_connection: Redis, stream_key: str, group_key: str, event_key: str) -> None:
    """
    Acknowledges that the event has been handled.
    """
    await event_queue_connection.xack(stream_key, group_key, event_key)
