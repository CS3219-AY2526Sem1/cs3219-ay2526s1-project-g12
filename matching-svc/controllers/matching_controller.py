import asyncio
from fastapi import HTTPException
from models.api_models import MatchRequest, MatchConfirmRequest
from redis.asyncio import Redis
from service.redis_confirmation_service import (
    setup_match_confirmation,
    check_match_exist,
    check_match_user,
    is_match_confirmed,
    update_user_confirmation,
    get_match_partner,
    get_match_details,
    delete_match_record
)
from service.redis_message_service import (
    send_match_found_message,
    send_match_finalised_message,
    send_match_terminated_message,
    wait_for_message,
)
from service.redis_matchmaking_service import (
    add_to_queued_users_set,
    find_partner,
    enqueue_user,
    remove_from_queued_users_set, 
    dequeue_user,
    check_in_queued_users_set,
    find_user_in_queue
)
from utils.logger import log
from utils.utils import (
    format_lock_key,
    format_queue_key,
    ping_redis_server,
    format_match_found_key,
    format_match_accepted_key,
    format_match_key,
    acquire_lock,
    release_lock
)
from uuid import uuid5, NAMESPACE_DNS

def check_redis_connection(reds_connection: Redis):
    """
    Checks if the connection between redis is up and running.
    """
    response = ping_redis_server(reds_connection)
    if (response):
        return {"status": "success", "redis": "responding"}
    else:
        return {"status": "success", "redis": "not responding"}

async def find_match(match_request: MatchRequest, matchmaking_conn: Redis,  message_conn: Redis, confirmation_conn: Redis) -> dict:
    """
    Finds a match based on the user topic and difficulty.\n
    If no match is made then add the user into the queue
    """
    user_id = match_request.user_id
    difficulty = match_request.difficulty
    category = match_request.category

    # Check if the user is already in the queue.
    if (not await add_to_queued_users_set(user_id, matchmaking_conn)):
        raise HTTPException(status_code=400, detail="User is already in the queue.")

    queue_key = format_queue_key(difficulty, category)
    lock_key = format_lock_key(queue_key)

    # Ensure that at any time only 1 request is updating the redis queue
    lock = await acquire_lock(lock_key, matchmaking_conn)
    log.info(f"User id, {user_id} has acquired the lock with key: {lock_key}.")

    try:
        partner = await find_partner(queue_key, matchmaking_conn)

        if (partner == ""): # No partner found then add the user to the queue
            await enqueue_user(user_id, queue_key, matchmaking_conn)
            log.info(f"Could not find a partner for {user_id}. Adding user to the queue")
        else:
            # Create a unique match ID
            match_id = str(uuid5(NAMESPACE_DNS, user_id + partner))

            # Create a table to store information on who has comfirm the match and who has not.
            match_key = format_match_key(match_id)
            await setup_match_confirmation(match_key, partner, user_id, difficulty, category, confirmation_conn)

            # Alert the other user through the message queue
            message_key = format_match_found_key(partner)
            await send_match_found_message(message_key, match_id, message_conn)
            log.info(f"Notified {partner} that a match has been found.")

            asyncio.create_task(confirmation_lookout(match_key, matchmaking_conn, message_conn, confirmation_conn))

            log.info(f"A match has been made between {user_id} and {partner}.")
            return {"match_id" : match_id, "message" : "match has been found"}
    finally:
        # Redis Lock class handles if the lock is expired it will not release another person's lock
        await release_lock(lock)
        log.info(f"User id, {user_id} has released the lock with key: {lock_key} .")
    
    # Then we will constantly poll until a match has been found
    return await wait_for_match(match_request, matchmaking_conn, message_conn)

async def wait_for_match(match_request: MatchRequest, matchmaking_conn: Redis, message_conn: Redis) -> dict:
    """
    Waits for a match found message from the message queue for a period of time before returning.\n
    If no match is found then remove the user from the queue.
    """
    user_id = match_request.user_id
    difficulty = match_request.difficulty
    category = match_request.category

    message_key = format_match_found_key(user_id)
    message =  await wait_for_message(message_key, message_conn)

    if message is None:
        queue_key = format_queue_key(difficulty, category)
        lock_key = format_lock_key(queue_key)
        lock = await acquire_lock(lock_key, matchmaking_conn)
        log.info(f"User id, {user_id} has acquired the lock with key: {lock_key}.")

        await dequeue_user(user_id, queue_key, matchmaking_conn)

        await release_lock(lock)
        log.info(f"User id, {user_id} has released the lock with key: {lock_key} .")
        log.info(f"Could not find a match for {user_id}, removing them from the queue")
        return {"message" : "could not find a match after 3 minutes"}
    elif message[1]  == "terminate":
        return {"message" : "matchmaking has been terminated"}
    else:
        match_id = message[1] # Index 0 is the key where the value is popped from
        return {"match_id" : match_id, "message" : "match has been found"}

async def terminate_match(match_request: MatchRequest, matchmaking_conn: Redis, message_conn: Redis) -> None:
    """
    Terminates the match request for the user.
    """
    user_id = match_request.user_id
    difficulty = match_request.difficulty
    category = match_request.category

    # Check if the user is in the queue in the first place
    if (not await check_in_queued_users_set(user_id, matchmaking_conn)):
        raise HTTPException(status_code=400, detail="User is not currently matchmaking")

    queue_key = format_queue_key(difficulty, category)

    if (await find_user_in_queue(user_id, queue_key, matchmaking_conn) is None):
        raise HTTPException(status_code=400, detail=f"User is not queuing for {difficulty} and {category}")

    
    lock_key = format_lock_key(queue_key)

    lock = await acquire_lock(lock_key, matchmaking_conn)
    log.info(f"User id, {user_id} has acquired the lock with key: {lock_key}.")

    try:
        await dequeue_user(user_id, queue_key, matchmaking_conn)
        await remove_from_queued_users_set(user_id, matchmaking_conn)

        message_key = format_match_found_key(user_id)
        await send_match_terminated_message(message_key, message_conn)

        log.info(f"{user_id} has terminated his matching.")
    finally:
        await release_lock(lock)
        log.info(f"User id, {user_id} has released the lock with key: {lock_key} .")


async def confirm_match(match_id: str, confirm_request: MatchConfirmRequest, matchmaking_conn: Redis, message_conn: Redis, confirmation_conn: Redis) -> dict:
    """
    Acknowledges the user's comfirmation with the given match id.\n
    If the user is the second person who is accepting the match, they will initate the room creating in the collaboration service.
    """
    user_id = confirm_request.user_id
    match_key = format_match_key(match_id)

    if (not await check_match_exist(match_key, confirmation_conn)):
        raise HTTPException(status_code=400, detail="invalid match id.")

    if (not await check_match_user(user_id, match_key, confirmation_conn)):
        raise HTTPException(status_code=400, detail="user does not have access to this match.")

    lock_key = format_lock_key(match_key)
    lock = await acquire_lock(lock_key, confirmation_conn)
    log.info(f"User id, {user_id} has acquired the lock with key: {lock_key}.")

    try:
        await update_user_confirmation(match_key, user_id, confirmation_conn)
        # The other user has accepted
        if (await is_match_confirmed(match_key, confirmation_conn)):
            
            # TODO: Signal the collaboration service to create a room
            collab_svc_data = "Data from collaboration service"

            partner = await get_match_partner(user_id, match_key, confirmation_conn)
            message_key = format_match_accepted_key(partner)
            await send_match_finalised_message(message_key, collab_svc_data, message_conn)
            log.info(f"Match comfirm message has been sent for user id, {partner}.")

            return {"match_details": collab_svc_data, "message": "starting match"}
    finally:
        await release_lock(lock)

    return await wait_for_confirmation(match_id, confirm_request, matchmaking_conn, message_conn, confirmation_conn)

async def wait_for_confirmation(match_id: str, confirm_request: MatchConfirmRequest, matchmaking_conn: Redis, message_conn: Redis, confirmation_conn: Redis) -> dict:
    """
    Waits for the other user to confirm their match.
    """
    user_id = confirm_request.user_id
    message_key = format_match_accepted_key(user_id)
    # Set timeout to be 15 seconds in case the redis server goes down it will return a response
    message = await wait_for_message(message_key, message_conn, timeout = 15)
    
    if (message is None or message[1] == ""):
        log.info(f"The partner for user id, {user_id} has failed to accept the match")
        return {"message" : "partner failed to accept the match"}
    else:
        match_details = message[1] # Index 0 is the key where the value is popped from
        match_key = format_match_key(match_id)
        await cleanup(match_key, matchmaking_conn, confirmation_conn)
        return {"match_details": match_details, "message": "starting match"}

async def confirmation_lookout(match_key: str, matchmaking_conn: Redis, message_conn: Redis, confirmation_conn: Redis):
    """
    Checks the match to see if both users has accepted.
    """
    log.info(f"Observer spawned for {match_key}")
    await  asyncio.sleep(12)

    # This means that one user did not accept or no user has accepted
    if (await check_match_exist(match_key, confirmation_conn)):
        match_details = await get_match_details(match_key, confirmation_conn)

        # Inform the other user that 
        if (match_details["user_one_confirmation"] == "1"):
            message_key = format_match_accepted_key(match_details["user_one"])
            await send_match_finalised_message(message_key, "", message_conn)
        elif (match_details["user_two_confirmation"] == "1"):
            message_key = format_match_accepted_key(match_details["user_two"])
            await send_match_finalised_message(message_key, "", message_conn)

        await cleanup(match_key, matchmaking_conn, confirmation_conn)
    
    log.info(f"Observer is killed for {match_key}")

async def cleanup(match_key: str, matchmaking_conn: Redis, confirmation_conn: Redis):
    """
    Cleans up redis services.
    """
    lock_key = format_lock_key(match_key)
    lock = await acquire_lock(lock_key, confirmation_conn)
    log.info(f"Backend matching service has acquired the lock with key: {lock_key} for cleaning up")

    match_details = await get_match_details(match_key, confirmation_conn)

    await remove_from_queued_users_set(match_details["user_one"], matchmaking_conn)
    await remove_from_queued_users_set(match_details["user_two"], matchmaking_conn)

    await delete_match_record(match_key, confirmation_conn)

    await release_lock(lock)
    log.info(f"Backend matching service has release the lock with key: {lock_key} ")

