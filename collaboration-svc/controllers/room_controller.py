from asyncio import Event
from redis.asyncio import Redis
from services.redis_event_queue import get_match_confirmation_event, remove_match_confirmation_event
from services.redis_room_service import create_room
from utils.utils import acquire_lock, release_lock

LOCK_KEY = "event_manager_lock"

async def create_listener(event_queue_connection: Redis, room_connection: Redis, stop_event: Event):
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
