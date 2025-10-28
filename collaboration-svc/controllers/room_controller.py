from asyncio import Event
from models.WebSocketManager import WebSocketManager
from redis.asyncio import Redis
from services.redis_event_queue import (
    get_match_confirmation_event,
    remove_match_confirmation_event,
    create_group, retrieve_stream_data,
    acknowlwedge_event
)
from services.redis_room_service import create_room, get_partner, is_user_alive
from utils.utils import acquire_lock, release_lock, get_envvar, format_room_key, extract_information_from_event, format_heartbeat_key

LOCK_KEY = "event_manager_lock"

ENV_REDIS_STREAM_KEY = "REDIS_STREAM_KEY"
ENV_REDIS_GROUP_KEY = "REDIS_GROUP"

async def create_room_listener(event_queue_connection: Redis, room_connection: Redis, stop_event: Event):
    """
    Spawns a worker to periodically check if there are any new match confirm events.\n
    Uses a distributed lock to ensure only one service handles each event.
    """
    while True:
        if (stop_event.is_set()):
             break

        lock = await acquire_lock(LOCK_KEY, event_queue_connection)

        match_details = await get_match_confirmation_event(event_queue_connection)

        if (match_details):
                await create_room(match_details, room_connection)
        
        await remove_match_confirmation_event(event_queue_connection)

        await release_lock(lock)

async def create_ttl_expire_listener(
    service_id: str,
    event_queue_connection: Redis,
    room_connection: Redis,
    websocket_manager: WebSocketManager,
    stop_event: Event
):
    """
    Spawns a worker to periodically check if any of the users TTL has expired.
    """
    stream_key = get_envvar(ENV_REDIS_STREAM_KEY)
    group_key = get_envvar(ENV_REDIS_GROUP_KEY)

    await create_group (event_queue_connection, stream_key, group_key)

    while True:
        if (stop_event.is_set()):
            break

        message = await retrieve_stream_data(event_queue_connection, stream_key, group_key, service_id)
        if (message):
            # Process the message to get the user id and the match id
            event_id, user_id, match_id = extract_information_from_event(message)
            room_key = format_room_key(match_id)

            partner = await get_partner(user_id, room_key, room_connection)
            partner_heartbeat_key = format_heartbeat_key(partner, match_id)

            if (await is_user_alive(partner_heartbeat_key, room_connection)):
                alert_user(partner, websocket_manager)
            else:
                # Cleanup 
                print("Clean Up")
            
            await acknowlwedge_event(event_queue_connection, stream_key, group_key, event_id)
            print("Event done and acknowledged")

def alert_user(user_id: str, websocket_manager: WebSocketManager) -> None:
    """
    Sends a message to the user altering them that.
    """
    print(f"Send message to  {user_id}")
