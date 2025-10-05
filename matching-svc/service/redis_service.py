from datetime import datetime
from redis import Redis
from utils.utils import get_envvar, format_redis_queue_key
from uuid import uuid5, NAMESPACE_DNS

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis() -> Redis:
    """
    Establishes a connection with redis using localhost.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    return Redis(host=host, port=redis_port, decode_responses=True)

def sever_connection(redis_connection: Redis):
    """
    Closes a connection with redis.
    """
    redis_connection.close()

def check_redis_availability(redis_connection: Redis) -> bool:
    """
    Checks if the redis server is up and responding.
    """
    return redis_connection.ping()

def add_user_to_queue_tracker(user_id: str, redis_connection: Redis) -> None:
    """
    Adds the user into a queued state.
    """
    redis_connection.sadd("queued_users", user_id)

def remove_user_to_queue_tracker(user_id: str, redis_connection: Redis) -> None:
    """
    Removes the user from the queued state.
    """
    redis_connection.srem("queued_users", user_id)

def check_user_in_queue(user_id: str, redis_connection: Redis) -> bool:
    """
    Checks if the user is in any queue and if they are not add them into a queue people set.
    """
    is_in =  redis_connection.sismember("queued_users", user_id)

    if (is_in):
        return True
    else:
        return False

def check_queue_length(difficulty: str, category: str, redis_connection: Redis) -> int:
    """
    Retrieves the queue length based on the dificulty and category.
    """
    queue_key = format_redis_queue_key(difficulty, category)
    queue_length = redis_connection.zcard(queue_key)

    return queue_length

def enqueue_user(user_id: str, difficulty: str, category: str, redis_connection: Redis, timetamp: float = None) -> dict:
    """
    Equeues the user based on their difficulty and category.
    """
    if (not check_user_in_queue(user_id, redis_connection)):
        add_user_to_queue_tracker(user_id, redis_connection)
        queue_key = format_redis_queue_key(difficulty, category)
        # This date time will act as the priority for the user
        if (timetamp):
            redis_connection.zadd(queue_key, {user_id: timetamp})
        else:
            redis_connection.zadd(queue_key, {user_id: datetime.now().timestamp()})
        
        return {"status": "success", "message": "user has joined the queue"}
    else:
        return {"status": "failure", "message": "user is already in the queue"}

def dequeue_next_user(difficulty: str, category: str, redis_connection: Redis) -> tuple:
    """
    Dequeues the user based on their difficulty and category.
    """
    queue_key = format_redis_queue_key(difficulty, category)
    # It will remove the earilest user in terms of the time stamp they joined.
    # This function returns a list of tuples so just return tuple[0]
    user = redis_connection.zpopmin(queue_key, count=1)
    return user[0]

def add_match(user_one: tuple, user_two: tuple, difficulty: str, category: str, redis_connection: Redis) -> str:
    """
    Adds match details to a hashset for comfirmation.
    """
    # Generate a unique match ID
    match_id = str(uuid5(NAMESPACE_DNS, user_one[0] + user_two[0]))
    match_id = 1
    # Create a match entry in the hashset using redis
    match_details = {
        "user_one_id": user_one[0],
        "user_two_id": user_two[0],
        "difficulty": difficulty,
        "category": category,
        "user_one_confirmation": "",
        "user_two_confirmation": ""
    }

    redis_connection.hset(match_id, mapping=match_details)

    return match_id

def remove_match(match_id: str, redis_connection: Redis) -> dict:
    """
    Removes and returns the match details based on the match id.
    """
    match_details = redis_connection.hgetall(match_id)

    return match_details

def update_match_response(match_id: str, user_id: str, redis_connection: Redis) -> None:
    """
    Updates the response for the match for the user.
    """
    if (redis_connection.hget(match_id, "user_one_id") == user_id):
        redis_connection.hset(match_id, "user_one_confirmation", "accepted")
    elif (redis_connection.hget(match_id, "user_two_id") == user_id):
        redis_connection.hset(match_id, "user_two_confirmation", "accepted")