import pytest
from controllers.matching_controller import (
    check_redis_connection,
    find_match
)
from models.api_models import (
    MatchRequest
)
from unittest.mock import patch, AsyncMock

class TestOtherFunctions:
    """
    Tests all other helper function or utility functions.
    """
    @patch("controllers.matching_controller.ping_redis_server", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_check_redis_connection_success(self, mock_ping):
        mock_ping.return_value = True
        redis_connection_mock = AsyncMock()

        result = await check_redis_connection(redis_connection_mock)
        assert result == {"status": "success", "redis": "responding"}

    @patch("controllers.matching_controller.ping_redis_server", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_check_redis_connection_failure(self, mock_ping):
        mock_ping.return_value = False
        redis_connection_mock = AsyncMock()

        result = await check_redis_connection(redis_connection_mock)
        assert result == {"status": "success", "redis": "not responding"}


class TestMatchFinding:
    """
    Tests all functions that are related to finding a match.
    """
    @pytest.fixture(scope="function", autouse=True)
    async def setup_user_objects(self):
        self.user_one_request = MatchRequest(
            user_id = "1",
            difficulty = "Easy",
            category = "Array"
        )
        
        self.user_two_requests = MatchRequest(
            user_id = "2",
            difficulty = "Easy",
            category = "Array"
        )

    @pytest.mark.asyncio
    @patch("controllers.matching_controller.wait_for_match", new_callable=AsyncMock)
    @patch("controllers.matching_controller.release_lock", new_callable=AsyncMock)
    @patch("controllers.matching_controller.acquire_lock", new_callable=AsyncMock)
    @patch("controllers.matching_controller.check_user_in_any_queue", new_callable=AsyncMock)
    @patch("controllers.matching_controller.terminate_previous_match_request", new_callable=AsyncMock)
    @patch("controllers.matching_controller.add_user_queue_details", new_callable=AsyncMock)
    @patch("controllers.matching_controller.find_partner", new_callable=AsyncMock)
    @patch("controllers.matching_controller.enqueue_user", new_callable=AsyncMock)
    @patch("controllers.matching_controller.format_lock_key")
    @patch("controllers.matching_controller.format_queue_key")
    @patch("controllers.matching_controller.format_in_queue_key")
    async def test_find_match_first_user(
        self,
        mock_format_in_queue_key,
        mock_format_queue_key,
        mock_format_lock_key,
        mock_enqueue_user,
        mock_find_partner,
        mock_add_user_queue_details,
        mock_terminate_previous_match_request,
        mock_check_user_in_any_queue,
        mock_acquire_lock,
        mock_release_lock,
        mock_wait_for_match,
    ):
        """
        Tests the find match function when the first user enters the queue.
        """
        mock_matchmaking_conn = AsyncMock()
        mock_message_conn = AsyncMock()
        mock_confirmation_conn = AsyncMock()
        mock_lock_object = AsyncMock()

        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_request.user_id}"
        mock_format_queue_key.return_value = f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"
        mock_format_lock_key .return_value = f"lock:{self.user_one_request.user_id}"

        mock_check_user_in_any_queue.return_value = False
        mock_acquire_lock.return_value = mock_lock_object
        mock_find_partner.return_value = ""
        
        await find_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn, mock_confirmation_conn)

        mock_terminate_previous_match_request.assert_not_called()
        mock_add_user_queue_details.assert_called_once_with(f"inqueue:{self.user_one_request.user_id}", self.user_one_request.difficulty, self.user_one_request.category, mock_matchmaking_conn)
        mock_enqueue_user.assert_called_once_with(self.user_one_request.user_id, f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}", mock_matchmaking_conn)
        mock_release_lock.assert_awaited_once_with(mock_lock_object)
        mock_wait_for_match.assert_awaited_once_with(self.user_one_request, mock_matchmaking_conn, mock_message_conn)
        
