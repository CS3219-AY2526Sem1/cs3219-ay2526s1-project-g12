import asyncio
from asyncio.exceptions import TimeoutError
from asyncio import Event
from controllers.websocket_controller import WebSocketManager
from fastapi import HTTPException
from models.api_models import MatchData
from redis.asyncio import Redis
from services.redis_event_queue import (
    get_match_confirmation_event,
    get_match_confirmation_event_data,
    remove_match_confirmation_event,
    create_group, retrieve_stream_data,
    acknowlwedge_event
)

from services.redis_room_service import (
    create_room,
    get_partner,
    get_room_information,
    is_user_alive, cleanup,
    add_room_cleanup,
    get_room_id,
    check_room_cleanup,
    delete_user_ttl,
    send_room_for_review,
    remove_room_cleanup,
    update_user_ttl,
    get_room_question,
    get_partner_name
)
from utils.logger import log
from utils.utils import (
    acquire_lock, 
    release_lock,
    get_envvar,
    format_user_room_key,
    extract_information_from_event,
    format_heartbeat_key,
    format_cleanup_key,
    does_key_exist,
    format_lock_key,
)

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

        room_id = await get_match_confirmation_event(event_queue_connection)

        await release_lock(lock)

        if (room_id):
            match_details = await get_match_confirmation_event_data(room_id, event_queue_connection)
            log.info(f"INFO: Room ID : {room_id}, match details : {match_details}")
            await create_room(match_details, room_connection)
            await remove_match_confirmation_event(event_queue_connection)

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

            await check_empty_room (user_id, room_connection, websocket_manager)
            
            await acknowlwedge_event(event_queue_connection, stream_key, group_key, event_id)
            log.info(f"Collaboration service, {service_id} has completed handling event {event_id}")    

async def alert_partner_left(user_id: str, room_id: str,  websocket_manager: WebSocketManager) -> None:
    """
    Sends a message to the user altering them that their partner has left.
    """
    await websocket_manager.send_message(user_id, room_id, f"partner_left")
    log.info(f"Sent a notification to {user_id} that their parter has left the mattch")

async def alert_partner_rejoined(user_id: str, room_id: str,  websocket_manager: WebSocketManager) -> None:
    """
    Sends a message to the partner that the user has rejoined the room.
    """
    await websocket_manager.send_message(user_id, room_id, f"partner_join")
    log.info(f"Sent a notification to {user_id} that their parter has joined the room")

async def remove_user(user_id: str, room_connection: Redis, websocket_manager: WebSocketManager) -> None:
    """
    Removes the user from the room.
    """
    heartbeat_key = format_heartbeat_key(user_id)

    if (not await does_key_exist(heartbeat_key, room_connection)):
        raise HTTPException(
                status_code=400,
                detail="Cannot leave the match as the user is currently not in a room"
            )

    await delete_user_ttl(heartbeat_key, room_connection)
    await check_empty_room(user_id, room_connection, websocket_manager)
    log.info(f"{user_id} has been removed from their room")

async def check_empty_room(user_id: str, room_connection: Redis, websocket_manager: WebSocketManager) -> None:
    """
    Checks if the room is empty. If it is then initate the wait for cleanup.
    """ 
    room_key = format_user_room_key(user_id)

    room_id = await get_room_id(room_key, room_connection)
    partner = await get_partner(user_id, room_key, room_connection)
    partner_heartbeat_key = format_heartbeat_key(partner)

    if (await is_user_alive(partner_heartbeat_key, room_connection)):
        await alert_partner_left(partner, room_id, websocket_manager)
    else:
        # Fire and foeget this task to check again in 5 minutes if any user joins back
        asyncio.create_task(start_room_hold_timer(room_id, user_id, room_connection))

async def start_room_hold_timer(room_id: str, user_id: str, room_connection: Redis) -> None:
    """
    Initates a 2 minute timer to check if anyone has retunred before cleaning up.
    """
    clean_up_key = format_cleanup_key(room_id)
    await add_room_cleanup (clean_up_key, user_id, room_connection)
    log.info(f"Holding room, {room_id} for 5 minutes due to both players leaving")
    retries = 0

    while (retries < 300):
        await asyncio.sleep(1)
        if (not await check_room_cleanup(clean_up_key, room_connection)):
            log.info(f"Clean up for {room_id} has been terminated")
            return
        retries += 1

    await cleanup(clean_up_key, room_connection)
    log.info(f"Data for {room_id} is cleared due to inactivity")

async def create_heartbeat_listener(room_connection: Redis, websocket_manager: WebSocketManager, stop_event: Event):
    """
    Spawns a worker to periodically check for any heartbeat update request from the user through the websocket.
    """ 
    while True:
        if (stop_event.is_set()):
            break
        
        # This is here because receive_message is blocking. So on shutdown it will not be able to because of this blocking task
        # So I will let it block for 10 seconds before retrying again
        try:
            message = await asyncio.wait_for(websocket_manager.receive_message(), timeout=10)
        except TimeoutError:
            message = None

        if (message):
            user_id = message["user_id"]
            command = message["message"]
            match (command):
                case "heartbeat":
                    heartbeat_key = format_heartbeat_key(user_id)
                    await update_user_ttl(heartbeat_key, room_connection)
                    log.info(f"User, {user_id} has refreshed their time to live")
                case _:
                    log.warning(f"Disregarding invalid command, {command}")

async def reconnect_user(user_id: str, room_connection: Redis, websocket_manager: WebSocketManager) -> None:
    """
    Reconnects the user to their assigned match.
    """
    room_key = format_user_room_key(user_id)

    if (not await does_key_exist(room_key)):
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

    partner = get_partner(user_id, room_key, room_connection)
    partner_heartbeat_key = format_heartbeat_key(partner)
    is_partner_in_room = await does_key_exist(partner_heartbeat_key)

    if (is_partner_in_room):
        await alert_partner_rejoined(partner, room_id, websocket_manager)

async def terminate_match(user_id: str, room_id: str, match_data: MatchData, room_connection: Redis, websocket_manager: WebSocketManager):
    """
    Terminates the match for both parties.
    """
    room_key = format_user_room_key(user_id)
    user_heartbeat_key = format_heartbeat_key(user_id)

    # Check if user is a valid user with a alive heartbeat
    has_valid_heartbeat = await does_key_exist(user_heartbeat_key, room_connection)
    has_valid_room = await does_key_exist(room_key, room_connection)

    if (has_valid_heartbeat and has_valid_room and await get_room_id(room_key, room_connection) == room_id):
        room_informaion = await get_room_information(room_key, room_connection)
        partner = await get_partner(user_id, room_key, room_connection)

        await websocket_manager.send_message(partner, room_id, "match_terminate")

        cleanup_key = format_cleanup_key(room_id)
        await cleanup(cleanup_key, room_connection)
        partner_heartbeat_key = format_heartbeat_key(partner)

        await delete_user_ttl(user_heartbeat_key, room_connection)
        await delete_user_ttl(partner_heartbeat_key, room_connection)
        send_room_for_review(user_id, partner, match_data.data, room_informaion)
        log.info(f"User, {user_id} has terminated room, {room_id}")
    else:
        log.info(f"WARNING: Invalid request to terminate match, {user_id}, {room_id}")
        raise HTTPException(
                status_code=400,
                detail="Cannot terminate match as user or room id is invalid"
            )

async def connect_user(user_id: str, room_id: str, room_connection: Redis) -> dict:
    """
    Connects the user to the room and returns the question assigned to them.
    """
    room_key = format_user_room_key(user_id)

    if (not await does_key_exist(room_key, room_connection) or await get_room_id(room_key, room_connection) != room_id):
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a room or the room does not exist"
        )
    
    lock_key = format_lock_key(room_id)
    lock = await acquire_lock(lock_key, room_connection)

    question = await get_room_question(room_key, user_id, room_connection)
    await release_lock(lock)
    partner_name = await get_partner_name(room_key, user_id, room_connection)

    return {"question" : question, "partner_name": partner_name}
