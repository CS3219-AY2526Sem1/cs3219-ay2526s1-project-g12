import asyncio
from asyncio import Event
from controllers.websocket_controller import WebSocketManager
from redis.asyncio import Redis
from fastapi import HTTPException
from services.redis_event_queue import (
    get_match_confirmation_event,
    remove_match_confirmation_event,
    create_group, retrieve_stream_data,
    acknowlwedge_event
)
from services.redis_room_service import create_room, get_partner, is_user_alive, cleanup, add_room_cleanup, get_room_id, check_room_cleanup, update_user_ttl, remove_room_cleanup
from utils.logger import log
from utils.utils import acquire_lock, release_lock, get_envvar, format_user_room_key, extract_information_from_event, format_heartbeat_key, format_cleanup_key, does_key_exist

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
            event_id, user_id = extract_information_from_event(message)
            log.info(f"Collaboration service, {service_id} is handling event {event_id}")

            room_key = format_user_room_key(user_id)

            room_id = await get_room_id(room_key, room_connection)
            partner = await get_partner(user_id, room_key, room_connection)
            partner_heartbeat_key = format_heartbeat_key(partner)

            if (await is_user_alive(partner_heartbeat_key, room_connection)):
                alert_user(partner, websocket_manager)
            else:
                # Fire and foeget this task to check again in 5 minutes if any user joins back
                asyncio.create_task(start_room_hold_timer(room_id, user_id, room_connection))
            
            await acknowlwedge_event(event_queue_connection, stream_key, group_key, event_id)
            log.info(f"Collaboration service, {service_id} has completed handling event {event_id}")

def alert_user(user_id: str, websocket_manager: WebSocketManager) -> None:
    """
    Sends a message to the user altering them that.
    """
    log.info(f"Sent a notification to {user_id} that their parter has left the mattch")

async def start_room_hold_timer(room_id: str, user_id: str, room_connection: Redis) -> None:
    """
    Initates a 2 minute timer to check if anyone has retunred before cleaning up.
    """
    clean_up_key = format_cleanup_key(room_id)
    await add_room_cleanup (clean_up_key, user_id, room_connection)
    
    retries = 0

    while (retries < 300):

        if (not await check_room_cleanup(clean_up_key, room_connection)):
            log.info(f"Clean up for {room_id} has been terminated")
            return

        retries += 1
        await asyncio.sleep(1)

    await cleanup(clean_up_key, room_connection)
    log.info(f"Data for {room_id} is cleared due to inactivity")

async def create_heartbeat_listner(room_connection: Redis, websocket_manager: WebSocketManager):
    """
    Spawns a worker to periodically check for any heartbeat update request from the user through the websocket.
    """ 

async def reconnect_user(user_id: str, room_connection: Redis, websocket_manager: WebSocketManager) -> None:
    """
    Reconnects the user to their assigned match.
    """
    room_key = format_user_room_key(user_id)

    if (not does_key_exist(room_key)):
        raise HTTPException(
                status_code=400,
                detail="User is not assiged a room or the room has expired",
            )

    # Removes the cleanup countdown if there is 
    room_id = get_room_id(room_key)
    cleanup_key = format_cleanup_key(room_id)
    await remove_room_cleanup(cleanup_key, room_connection)

    heartbeat_key = format_heartbeat_key(user_id)
    await update_user_ttl(heartbeat_key, room_connection)

    log.info(f"User, {user_id} has reconnected to room, {room_id}")

    #TODO : Lastly when collab service has the websocket notify the partner if they are there
