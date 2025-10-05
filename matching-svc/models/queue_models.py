import asyncio
from asyncio import Lock, Task
from models.websocket_models import WebsocketConnectionManager
from redis import Redis
from service.redis_service import (
    add_match,
    check_queue_length,
    dequeue_next_user, 
    enqueue_user,
    remove_match,
    remove_user_to_queue_tracker
)
from utils.utils import format_redis_queue_key

class QueueManager ():
    """
    Manages the workers who will be checking the queues.
    """
    def __init__(self):
        self.active_workers: dict[str, Task] = {}
        self.lock = Lock()
        self.check_timeout = 10
        self.confirmation_timeout = 12
    
    async def spawn_new_worker(self, difficulty: str, category: str, redis_connection: Redis, websocket_manager: WebsocketConnectionManager):
        """
        Spawns a new worker to track the queue if there isnt one.
        """
        async with self.lock:
            queue_key = format_redis_queue_key(difficulty, category)
            if queue_key not in self.active_workers:
                self.active_workers[queue_key] = asyncio.create_task(self._loop(difficulty, category, redis_connection, websocket_manager))
    
    async def _loop(self, difficulty: str, category: str, redis_connection: Redis, websocket_manager: WebsocketConnectionManager):
        """
        Continously checks the queue until there is no one inside the queue.
        """
        while True:
            # Don't need to repetedly check, just check at each interval.
            await asyncio.sleep(self.check_timeout)

            queue_length = check_queue_length(difficulty, category, redis_connection)

            if (queue_length >= 2):
                user_one = dequeue_next_user(difficulty, category, redis_connection)
                user_two = dequeue_next_user(difficulty, category, redis_connection)
                asyncio.create_task(self._wait_confirmation(user_one, user_two, difficulty, category, redis_connection, websocket_manager))
            elif (queue_length == 0):
                # No one in the queue thus we don't need to continue checking
                async with self.lock:
                    queue_key = format_redis_queue_key(difficulty, category)
                    self.active_workers.pop(queue_key, None)
                break
    
    async def _wait_confirmation(self, user_one: tuple, user_two: tuple, difficulty: str, category: str, redis_connection: Redis, websocket_manager: WebsocketConnectionManager):
        """
        Waits for both users to respond.\n
        If any user does not respond then remove them from the queue
        """
        # Create a match to record their response
        match_id = add_match(user_one, user_two, difficulty, category, redis_connection)
        await websocket_manager.broadcast(match_id, user_one,  user_two)

        # Give them time to respond
        print("Waiting confirmation")
        await asyncio.sleep(self.confirmation_timeout)

        match_details = remove_match(match_id, redis_connection)
        if (match_details["user_one_confirmation"] and match_details["user_two_confirmation"]):
            # TODO: Set up the a collaboration room then use the websocket to
            remove_user_to_queue_tracker(user_one[0], redis_connection)
            remove_user_to_queue_tracker(user_two[0], redis_connection)

            pass
        elif (not match_details["user_one_confirmation"] and not match_details["user_two_confirmation"]):
            # Both users failed to accept
            await self._unqueue_user(user_one, websocket_manager)
            await self._unqueue_user(user_two, websocket_manager)
        elif (match_details["user_one_confirmation"]): # The remaining 2 conditions is when either one accepts while the other rejects
            await self._requeue_user(user_one, difficulty, category, redis_connection, websocket_manager)
            await self._unqueue_user(user_two, redis_connection, websocket_manager)
        else:
            await  self._requeue_user(user_two, difficulty, category, redis_connection, websocket_manager)
            await self._unqueue_user(user_one, redis_connection, websocket_manager)

    async def _requeue_user(self, user: tuple, difficulty: str, category: str, redis_connection: Redis, websocket_manager: WebsocketConnectionManager):
        """
        Adds the user back to the queue if they accepted and their opponent did not.
        """
        enqueue_user(user[0], difficulty, category, redis_connection, user[1])

        # Incase while waiting for the comfirmation the worker stops, thus we need to re create the worker.
        await self.spawn_new_worker(difficulty, category, redis_connection, websocket_manager)
    
    async def _unqueue_user(self, user: tuple, redis_connection: Redis, websocket_manager: WebsocketConnectionManager):
        """
        Removes the user from the queue if they did not accept and also sever the websocket connection.
        """
        remove_user_to_queue_tracker(user[0], redis_connection)
        await websocket_manager.send_message_to_user(user[0], "Failed to accept match")
        await websocket_manager.disconnect(user[0])