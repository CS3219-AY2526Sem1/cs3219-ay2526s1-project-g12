from fakeredis.aioredis import FakeRedis
import pytest
from utils.utils import (
    format_in_queue_key,
    format_queue_key,
    format_lock_key,
    format_match_found_key,
    format_match_key,
    format_match_accepted_key,
    acquire_lock,
    release_lock,
    ping_redis_server
)
from unittest.mock import patch, AsyncMock, MagicMock

class TestUtilFunctions:
    """
    Tests all other helper function or utility functions.
    """
    @pytest.fixture(scope="function", autouse=True)
    async def set_up_fake_redis(self):
        self.mock_redis_client = await FakeRedis()
        self.user_id = "1"
        self.category = "Array"
        self.difficulty = "Easy"
        self.lock = "some_key"
   
    def test_format_in_queue_key(self):
            key = format_in_queue_key(self.user_id)

            assert key == f"inqueue:{self.user_id}"
    
    def test_format_queue_key(self):
            key = format_queue_key(self.difficulty, self.category)

            assert key == f"queue:{self.difficulty}:{self.category}"
    
    def test_format_lock_key(self):
            key = format_lock_key(self.lock)

            assert key == f"lock:{self.lock}"
    
    def test_format_match_found_key(self):
            key = format_match_found_key(self.user_id)

            assert key == f"match_found:{self.user_id}"

    def test_format_match_key(self):
            key = format_match_key(self.user_id)

            assert key == f"match:{self.user_id}"

    def test_format_match_accepted_key(self):
            key = format_match_accepted_key(self.user_id)

            assert key == f"match_confirm:{self.user_id}"
    
    def test_acquire_lock(self):
            key = format_match_accepted_key(self.user_id)

            assert key == f"match_confirm:{self.user_id}"

    @pytest.mark.asyncio
    @patch("utils.utils.Lock")
    async def test_acquire_lock(self, mock_lock):
        mock_lock_object = AsyncMock()
        mock_lock.return_value = mock_lock_object

        lock = await acquire_lock(self.lock, self.mock_redis_client)

        mock_lock.assert_called_once_with(self.mock_redis_client, self.lock, timeout=60)
        mock_lock_object.acquire.assert_awaited_once()
        assert lock == mock_lock_object

    @pytest.mark.asyncio
    @patch("utils.utils.Lock", new_callable= AsyncMock)
    async def test_release_lock(self, mock_lock):

        await release_lock(mock_lock)
        mock_lock.release.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ping_redis_server(self):
           result = await ping_redis_server(self.mock_redis_client)
           assert result == True
