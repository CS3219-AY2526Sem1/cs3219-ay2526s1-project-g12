from redis.asyncio import Redis
from services.redis_event_queue import get_match_confirmation_event, create_room


async def create_listener(event_queue_connection: Redis, room_connection: Redis):
    """
    Spawns a worker to periodically check if there are any new match confirm events.
    """
    match_details = await get_match_confirmation_event(event_queue_connection)

    if (match_details):
        create_room(match_details, room_connection)
