import asyncio
from fastapi import HTTPException
from models.api_models import MatchRequest, MatchComfirmRequest
from redis.asyncio import Redis
from service.redis_message_service import send_match_found_message, send_match_finalised_message
from service.redis_queue_service import (
    add_to_queued_users_set,
    find_partner, enqueue_user,
    remove_from_queued_users_set, 
    dequeue_user,
    acquire_lock,
    release_lock,
    check_match_exist,
    check_match_user,
    setup_match_comfirmation,
    update_user_comfirmation,
    get_match_partner,
    delete_match_record,
    is_match_comfirmed,
    get_match_details
)
from utils.logger import log
from utils.utils import (
    format_lock_key,
    format_queue_key,
    ping_redis_server,
    format_match_found_key,
    format_match_accepted_key,
    format_match_ley
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

async def find_match(match_request: MatchRequest, queue_connection: Redis,  message_queue_connection: Redis) -> dict:
    """
    Finds a match based on the user topic and difficulty.
    """
    # Check if the user is already in the queue if they are then we don't continue.
    if (not await add_to_queued_users_set(match_request.user_id, queue_connection)):
        raise HTTPException(status_code=400, detail="User is already in the queue.")
    
    queue_key = format_queue_key(match_request.difficulty, match_request.category)
    lock_key = format_lock_key(queue_key)

    # Ensure that at any time only 1 request is updating the redis queue
    lock = await  acquire_lock(match_request.user_id, lock_key, queue_connection)
    try:
        # Check if a match can be made
        partner = await find_partner(queue_key, queue_connection)

        if (partner == ""): # No partner found then add the user to the queue
            log.info(f"User id, {match_request.user_id} could not find a partner. Adding the user into the queue.")
            await enqueue_user(match_request.user_id, queue_key, queue_connection)
        else:
            # Create a unique match ID
            match_id = "a"
           # match_id = str(uuid5(NAMESPACE_DNS, match_request.user_id + partner))

            # Create a table to store information on who has comfirm the match and who has not.
            await setup_match_comfirmation(match_id, partner, match_request.user_id, match_request.difficulty, match_request.category, queue_connection)

            # Alert the other user through the message queue
            await send_match_found_message(partner, match_id, message_queue_connection)

            log.info(f"{match_request.user_id} has found a match.")
            return {"match_id" : match_id, "message" : "match has been found"}
    finally:
        # Redis Lock class handles if the lock is expired it will not release another person's lock
        await release_lock(match_request.user_id,  lock)
    
    # Then we will constantly poll until a match has been found
    return await wait_for_match(match_request, queue_connection, message_queue_connection)

async def wait_for_match(match_request: MatchRequest, queue_connection: Redis, message_queue_connection: Redis) -> dict:
    """
    Waits for a match found message from the message queue for a period of time before returning.\n
    If no match is found then remove the user from the queue.
    """
    key = format_match_found_key(match_request.user_id)
    message =  await message_queue_connection.blpop(key, timeout=180) # Timeout 3 Minutes

    try:
        if message is None:    
            log.info(f"User id,{match_request.user_id} could not find a match within the allocated time period. Removing user from the queue.")
            return {"message" : "could not find a match after 10 minutes"}
        else:
            match_id = message[1] # Index 0 is the key where the value is popped from

            log.info(f"{match_request.user_id} has found a match.")
            return {"match_id" : match_id, "message" : "match has been found"}
    finally:
        # Cleaning up no matter what is the result of the match making
        # We will always remove the user from the queue status
        queue_key = format_queue_key(match_request.difficulty, match_request.category)
        lock_key = format_lock_key(queue_key)

        lock = await acquire_lock(match_request.user_id, lock_key, queue_connection)

        await dequeue_user(match_request.user_id, queue_key, queue_connection)

        await release_lock(match_request.user_id, lock)

async def confirm_match(match_id: str, comfirm_request: MatchComfirmRequest, queue_connection: Redis, message_queue_connection:Redis) -> dict:
    """
    Acknowledges the user's comfirmation with the given match id.\n
    If the user is the second person who is accepting the match, they will initate the room creating in the collaboration service.
    """
    match_key = format_match_ley(match_id)
    if (not await check_match_exist(match_key, queue_connection)):
        raise HTTPException(status_code=400, detail="invalid match id.")

    if (not await check_match_user(comfirm_request.user_id, match_key, queue_connection)):
        raise HTTPException(status_code=400, detail="user does not have access to this match.")

    lock_key = format_lock_key(match_key)
    lock = await acquire_lock(comfirm_request.user_id,lock_key, queue_connection)

    try:
        await update_user_comfirmation(match_key, comfirm_request.user_id, queue_connection)
        # The other user has accepted
        if (await is_match_comfirmed(match_key, queue_connection)):
            
            # TODO: Signal the collaboration service to create a room
            collab_svc_data = "Data from collaboration service"

            partner = await get_match_partner(comfirm_request.user_id, match_key, queue_connection)
            await send_match_finalised_message(partner, collab_svc_data, message_queue_connection)

            return {"match_details": collab_svc_data, "message": "both parties accepted the match"}
    finally:
        await release_lock(comfirm_request.user_id, lock)

    return await wait_for_comfirmation(match_key, comfirm_request, queue_connection, message_queue_connection)

async def wait_for_comfirmation(match_key: str, comfirm_request: MatchComfirmRequest, queue_connection: Redis, message_queue_connection: Redis) -> dict:
    """
    Waits for the other user to comfirm their match.
    """
    key = format_match_accepted_key(comfirm_request.user_id)
    message =  await message_queue_connection.blpop(key)

    try:
        if message is None:
            log.info(f"The partner for user id, {comfirm_request.user_id} has failed to accept the match")
            return {"message" : "partner failed to accept the match"}
        else:
            match_details = message[1] # Index 0 is the key where the value is popped from
            return {"match_details": match_details, "message": "both parties accepted the match"}
    finally:
        # No matter the outcome we need to clean up the record in the  match comfirmation and queue server
        lock_key = format_lock_key(match_key)
        lock = await acquire_lock(comfirm_request.user_id,lock_key, queue_connection)

        match_details = await get_match_details(match_key, queue_connection)

        await remove_from_queued_users_set(match_details["user_one"], queue_connection)
        await remove_from_queued_users_set(match_details["user_two"], queue_connection)

        await delete_match_record(match_key, queue_connection)

        await release_lock(comfirm_request.user_id, lock)

async def match_lookout(match_key: str, queue_connection):
    """
    
    """
    asyncio.sleep(12)

    # This means that one user did not accept or no user has accepted
    if (await check_match_exist(match_key, queue_connection)):

        # No matter the outcome we need to clean up the record in the  match comfirmation and queue server
        lock_key = format_lock_key(match_key)
        lock = await acquire_lock("matching-svc",lock_key, queue_connection)

        match_details = await get_match_details(match_key, queue_connection)

        await remove_from_queued_users_set(match_details["user_one"], queue_connection)
        await remove_from_queued_users_set(match_details["user_two"], queue_connection)

        await delete_match_record(match_key, queue_connection)

        await release_lock("matching-svc", lock)
