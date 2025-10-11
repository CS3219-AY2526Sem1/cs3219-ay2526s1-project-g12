from models.api_models import MatchRequest
from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from service.redis_message_service import send_match_found_message
from service.redis_queue_service import add_to_queued_users_set, find_partner, enqueue_user, remove_from_queued_users_set
from utils.utils import format_lock_key, format_queue_key, ping_redis_server, format_match_found_key
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
        return {"status": "failure", "messsage": "user is already in the queue"}
    
    queue_key = format_queue_key(match_request.difficulty, match_request.category)
    lock_key = format_lock_key(match_request.difficulty, match_request.category)
    # This lock will be sync accross all match-svc instances as long as the key used is the same
    # timeout = safety fallback, given 2 mins
    lock = Lock(queue_connection, lock_key, timeout=120) 

    # Ensure that at any time only 1 request is updating the redis queue
    await  lock.acquire()
    try:
        # Check if a match can be made
        partner = await find_partner(queue_key, queue_connection)
        print(partner == "")

        if (partner == ""): # No partner found then add the user to the queue
            await enqueue_user(match_request.user_id, queue_key, queue_connection)
        else:
            # Create a unique match ID
            match_id = str(uuid5(NAMESPACE_DNS, match_request.user_id + partner))

            # First alert the other user through the message queue
            await send_match_found_message(partner, match_id, message_queue_connection)

            # We can return a resposne saying we have found a match
            return {"status" : "match found", "match_id" : match_id, "message" : "match has been found"}

    finally:
        # Redis Lock class handles if the lock is expired it will not release another person's lock
        await lock.release()
    
    # Then we will constantly poll until a match has been found
    return await wait_for_match(match_request, queue_connection, message_queue_connection)

async def wait_for_match(match_request: MatchRequest, queue_connection:Redis, message_queue_connection:Redis) -> dict:
    """
    Waits for a match found message from the message queue for a period of time before returning.\n
    If no match is found then remove the user from the queue.
    """
    key = format_match_found_key(match_request.user_id)
    message =  await message_queue_connection.blpop(key, timeout=180) # Timeout 3 Minutes

    if message is None:
        return {"status" : "match not found", "message" : "could not find a match after 10 minutes"}
    else:
        remove_from_queued_users_set(match_request.user_id, queue_connection)
        match_id = message[1] # Index 0 is the key where the value is popped from
        return {"status" : "match found", "match_id" : match_id, "message" : "match has been found"}