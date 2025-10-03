from models.api_models import MatchRequest
from redis import Redis
from service.redis_service import check_redis_availability, enqueue_user

def ping_redis_server(redis_connection: Redis) -> dict:
    """
    Ping the redis server and check if it is responding.
    """
    response: bool = check_redis_availability(redis_connection)
    if (response):
        return {"redis_status": "up"}
    else:
        return {"redis_status": "down"}

def find_match(user: MatchRequest, redis_connection: Redis):
    enqueue_user(user.user_id, user.difficulty, user.category, redis_connection)
