from redis import Redis
from datetime import datetime
from utils.logger import log
from utils.utils import get_envvar

ENV_REDIS_HOST_KEY = "REDIS_HOST"
ENV_REDIS_PORT_KEY = "REDIS_PORT"

def connect_to_redis_room_service() -> Redis:
    """
    Establishes a connection with redis room service.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses

    redis =  Redis(host=host, port=redis_port, decode_responses=True, db=0)
    # Configure redis so that expired keys will be sent as a event within redis
    # redis.config_set('notify-keyspace-events', 'Ex')
    return redis

def connect_to_redis_event_queue() -> Redis:
    """
    Establishes a connection with the event queue.
    """
    redis_port = get_envvar(ENV_REDIS_PORT_KEY)
    host = get_envvar(ENV_REDIS_HOST_KEY)
    # decode_responses = True is to allow redis to automatically decode responses
    return Redis(host=host, port=redis_port, decode_responses=True, db=1)

def main():
    log.info("Listener is up")

    room_service = connect_to_redis_room_service()
    message_queue = connect_to_redis_event_queue()

    # Create a Pub/Sub object
    pubsub = room_service.pubsub()
    # Subscribe to expiry event channel
    pubsub.psubscribe('__keyevent@0__:expired')

    while True:
        try:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message:
                message_queue.xadd("expired_ttl", {
                    "key": message["data"],
                    "event": "expired",
                    "timestamp": str(datetime.now())
                })
                print("Event sent")
            else:
                continue
        except KeyboardInterrupt:
            print("\n Stopping listener...")
            break

if __name__ == "__main__":
    main()
