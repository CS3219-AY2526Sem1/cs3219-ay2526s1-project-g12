from  aioredis.lock import Lock
from redis.asyncio import Redis
from services.redis_event_queue import get_match_confirmation_event, remove_match_confirmation_event

LOCK_KEY = "event_manager_lock"
LOCK_TIMEOUT = 10  # In seconds and is to prevent deadlocks

async def create_listener(event_queue_connection: Redis, room_connection: Redis):
    """
    Spawns a worker to periodically check if there are any new match confirm events.\n
    Uses a distributed lock to ensure only one service handles each event.
    """
    lock = Lock(
        event_queue_connection,
        LOCK_KEY,
        LOCK_TIMEOUT
    )

    match_details = await get_match_confirmation_event(event_queue_connection)

    if (match_details):
        pass
        #create_room(match_details, room_connection)
    
    await remove_match_confirmation_event(event_queue_connection)

    lock.release()
