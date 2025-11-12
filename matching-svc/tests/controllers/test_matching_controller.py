from controllers.matching_controller import (
    check_redis_connection,
    find_match,
    wait_for_match,
    terminate_previous_match_request
)
from fastapi import HTTPException
from models.api_models import (
    MatchRequest
)
import pytest
from unittest import mock
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import UUID

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
        self.match_id = UUID("12345678-1234-5678-1234-567812345678")

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
    async def test_find_match_no_partner(
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
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        mock_confirmation_conn = MagicMock()
        mock_lock_object = MagicMock()

        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_request.user_id}"
        mock_format_queue_key.return_value = f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"
        mock_format_lock_key .return_value = f"lock:queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"

        mock_check_user_in_any_queue.return_value = False
        mock_acquire_lock.return_value = mock_lock_object
        mock_find_partner.return_value = ""
        
        await find_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn, mock_confirmation_conn)

        mock_terminate_previous_match_request.assert_not_called()
        mock_add_user_queue_details.assert_awaited_once_with(f"inqueue:{self.user_one_request.user_id}", self.user_one_request.difficulty, self.user_one_request.category, mock_matchmaking_conn)
        mock_enqueue_user.assert_awaited_once_with(self.user_one_request.user_id, f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}", mock_matchmaking_conn)
        mock_release_lock.assert_awaited_once_with(mock_lock_object)
        mock_wait_for_match.assert_awaited_once_with(self.user_one_request, mock_matchmaking_conn, mock_message_conn)

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
    @patch("controllers.matching_controller.format_match_key")
    @patch("controllers.matching_controller.format_match_found_key")
    @patch("controllers.matching_controller.uuid5")
    @patch("controllers.matching_controller.send_match_found_message", new_callable=AsyncMock)
    @patch("controllers.matching_controller.update_user_match_found_status", new_callable=AsyncMock)
    async def test_find_match_found_partner(
        self,
        mock_update_user_match_found_status,
        mock_send_match_found_message,
        mock_uuid5,
        mock_format_match_found_key,
        mock_format_match_key,
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

        mock_format_in_queue_key.side_effect = [f"inqueue:{self.user_two_requests.user_id}", f"inqueue:{self.user_one_request.user_id}"]
        mock_format_queue_key.return_value = f"queue:{self.user_two_requests.difficulty}:{self.user_two_requests.category}"
        mock_format_lock_key .return_value = f"lock:queue:{self.user_two_requests.difficulty}:{self.user_two_requests.category}"
        mock_format_match_key.return_value = f"match:{self.match_id}"
        mock_format_match_found_key.return_value = f"match_found:{self.user_one_request.user_id}"

        mock_check_user_in_any_queue.return_value = False
        mock_acquire_lock.return_value = mock_lock_object
        mock_find_partner.return_value = f"{self.user_one_request.user_id}"

        mock_uuid5.return_value = self.match_id
        
        await find_match(self.user_two_requests, mock_matchmaking_conn, mock_message_conn, mock_confirmation_conn)

        mock_terminate_previous_match_request.assert_not_called()
        mock_add_user_queue_details.assert_awaited_once_with(f"inqueue:{self.user_two_requests.user_id}", self.user_two_requests.difficulty, self.user_two_requests.category, mock_matchmaking_conn)
        mock_enqueue_user.assert_not_called()
        mock_send_match_found_message.assert_awaited_once_with(f"match_found:{self.user_one_request.user_id}", str(self.match_id), mock_message_conn)
        mock_update_user_match_found_status.assert_has_awaits([
            mock.call(f"inqueue:{self.user_two_requests.user_id}", mock_matchmaking_conn),
            mock.call(f"inqueue:{self.user_one_request.user_id}", mock_matchmaking_conn),
        ])
        mock_release_lock.assert_awaited_once_with(mock_lock_object)
        mock_wait_for_match.assert_not_called()

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
    async def test_find_match_new_request_success(
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
        Tests when a new request is found.
        """
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        mock_confirmation_conn = MagicMock()
        mock_lock_object = MagicMock()

        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_request.user_id}"
        mock_format_queue_key.return_value = f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"
        mock_format_lock_key .return_value = f"lock:queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"

        mock_check_user_in_any_queue.return_value = True
        mock_terminate_previous_match_request.return_value = True
        mock_acquire_lock.return_value = mock_lock_object
        mock_find_partner.return_value = ""
        
        try:
            await find_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn, mock_confirmation_conn)
        except HTTPException as e:
            pytest.fail(f"HTTPException was raised unexpectedly: {e}")
        
        # Then ensure that the rest of the code runs accordingly
        mock_add_user_queue_details.assert_awaited_once_with(f"inqueue:{self.user_one_request.user_id}", self.user_one_request.difficulty, self.user_one_request.category, mock_matchmaking_conn)
        mock_enqueue_user.assert_awaited_once_with(self.user_one_request.user_id, f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}", mock_matchmaking_conn)
        mock_release_lock.assert_awaited_once_with(mock_lock_object)
        mock_wait_for_match.assert_awaited_once_with(self.user_one_request, mock_matchmaking_conn, mock_message_conn)


    @pytest.mark.asyncio
    @patch("controllers.matching_controller.check_user_in_any_queue", new_callable=AsyncMock)
    @patch("controllers.matching_controller.terminate_previous_match_request", new_callable=AsyncMock)
    @patch("controllers.matching_controller.format_lock_key")
    @patch("controllers.matching_controller.format_queue_key")
    @patch("controllers.matching_controller.format_in_queue_key")
    async def test_find_match_new_request_failure(
        self,
        mock_format_in_queue_key,
        mock_format_queue_key,
        mock_format_lock_key,
        mock_terminate_previous_match_request,
        mock_check_user_in_any_queue,
    ):
        """
        Tests when a new request is found.
        """
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        mock_confirmation_conn = MagicMock()

        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_request.user_id}"
        mock_format_queue_key.return_value = f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"
        mock_format_lock_key .return_value = f"lock:{self.user_one_request.user_id}"

        mock_check_user_in_any_queue.return_value = True
        mock_terminate_previous_match_request.return_value = False
        
        with pytest.raises(HTTPException):
            await find_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn, mock_confirmation_conn)

class TestWaitForMatch:
    """
    Tests all functions that are related to waiting for a match.
    """
    @pytest.fixture(scope="function", autouse=True)
    async def setup_user_objects(self):
        self.user_one_request = MatchRequest(
            user_id = "1",
            difficulty = "Easy",
            category = "Array"
        )
    
    @pytest.mark.asyncio
    @patch("controllers.matching_controller.format_match_found_key")
    @patch("controllers.matching_controller.format_in_queue_key")
    @patch("controllers.matching_controller.format_queue_key")
    @patch("controllers.matching_controller.format_lock_key")
    @patch("controllers.matching_controller.release_lock", new_callable=AsyncMock)
    @patch("controllers.matching_controller.acquire_lock", new_callable=AsyncMock)
    @patch("controllers.matching_controller.wait_for_message", new_callable= AsyncMock)
    @patch("controllers.matching_controller.dequeue_user", new_callable=AsyncMock)
    @patch("controllers.matching_controller.remove_user_queue_details", new_callable=AsyncMock)
    async def test_wait_for_match_timeout(
        self,
        mock_remove_user_queue_details,
        mock_dequeue_user,
        mock_wait_for_message,
        mock_acquire_lock,
        mock_release_lock,
        mock_format_lock_key,
        mock_format_queue_key,
        mock_format_in_queue_key,
        mock_format_match_found_key
    ):
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        
        mock_lock_object = MagicMock()
        mock_acquire_lock.return_value = mock_lock_object
        
        mock_format_match_found_key.return_value = f"match_found:{self.user_one_request.user_id}"
        mock_format_queue_key.return_value =f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"
        mock_format_lock_key .return_value = f"lock:queue:{self.user_one_request.difficulty}:{self.user_one_request.category}"
        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_request.user_id}"

        mock_wait_for_message.return_value = None

        response = await wait_for_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn)

        mock_remove_user_queue_details.assert_awaited_once_with(f"inqueue:{self.user_one_request.user_id}", mock_matchmaking_conn)
        mock_dequeue_user.assert_awaited_once_with(self.user_one_request.user_id, f"queue:{self.user_one_request.difficulty}:{self.user_one_request.category}", mock_matchmaking_conn)
        mock_release_lock.assert_awaited_once_with(mock_lock_object)
        assert response ==  {"message": "could not find a match after 3 minutes"}

    @pytest.mark.asyncio
    @patch("controllers.matching_controller.format_match_found_key")
    @patch("controllers.matching_controller.wait_for_message", new_callable= AsyncMock)
    async def test_wait_for_match_terminate(
        self,
        mock_wait_for_message,
        mock_format_match_found_key
    ):
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        
        mock_format_match_found_key.return_value = f"match_found:{self.user_one_request.user_id}"

        mock_wait_for_message.return_value = ["key", "terminate"]

        response = await wait_for_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn)

        assert response ==  {"message": "matchmaking has been terminated"}

    @pytest.mark.asyncio
    @patch("controllers.matching_controller.format_match_found_key")
    @patch("controllers.matching_controller.wait_for_message", new_callable= AsyncMock)
    async def test_wait_for_match_new_request(
        self,
        mock_wait_for_message,
        mock_format_match_found_key
    ):
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        
        mock_format_match_found_key.return_value = f"match_found:{self.user_one_request.user_id}"

        mock_wait_for_message.return_value = ["key", "new request made"]

        with pytest.raises(HTTPException):
            await wait_for_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn)

    @pytest.mark.asyncio
    @patch("controllers.matching_controller.format_match_found_key")
    @patch("controllers.matching_controller.wait_for_message", new_callable= AsyncMock)
    async def test_wait_for_match_found_match(
        self,
        mock_wait_for_message,
        mock_format_match_found_key
    ):
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        
        mock_format_match_found_key.return_value = f"match_found:{self.user_one_request.user_id}"

        mock_wait_for_message.return_value = ["key", "1"] # Just a random number since it returns the room id

        response = await wait_for_match(self.user_one_request, mock_matchmaking_conn, mock_message_conn)

        assert response ==  {"match_id": "1", "message": "match has been found"}

class TestTerminateMatchRequest:
    """
    Tests all functions that are related to terminating a match request.
    """
    @pytest.fixture(scope="function", autouse=True)
    async def setup_user_objects(self):
        self.user_one_id = "1"

    @pytest.mark.asyncio
    @patch("controllers.matching_controller.format_in_queue_key")
    @patch("controllers.matching_controller.get_user_queue_details", new_callable= AsyncMock)
    @patch("controllers.matching_controller.check_user_found_match", new_callable= AsyncMock)
    @patch("controllers.matching_controller.terminate_match", new_callable= AsyncMock)
    async def test_terminate_previous_match_request_success(
        self,
        mock_terminate_match,
        mock_check_user_found_match,
        mock_get_user_queue_details,
        mock_format_in_queue_key
    ):
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        
        user_one_old_queue_details= {
            "difficulty": "Medium",
            "category": "Graphs",
            "match_found": 0
        }

        user_one_old_request = MatchRequest(
            user_id = "1",
            difficulty = "Medium",
            category = "Graphs"
        )

        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_id}"
        mock_get_user_queue_details.return_value = user_one_old_queue_details
        mock_check_user_found_match.return_value =False

        response = await terminate_previous_match_request(self.user_one_id, mock_matchmaking_conn, mock_message_conn)

        mock_terminate_match.assert_awaited_once_with(user_one_old_request, mock_matchmaking_conn, mock_message_conn, is_new_request = True)
        assert response is True

    @pytest.mark.asyncio
    @patch("controllers.matching_controller.format_in_queue_key")
    @patch("controllers.matching_controller.get_user_queue_details", new_callable= AsyncMock)
    @patch("controllers.matching_controller.check_user_found_match", new_callable= AsyncMock)
    async def test_terminate_previous_match_request_failure(
        self,
        mock_check_user_found_match,
        mock_get_user_queue_details,
        mock_format_in_queue_key
    ):
        mock_matchmaking_conn = MagicMock()
        mock_message_conn = MagicMock()
        
        user_one_old_queue_details= {
            "difficulty": "Medium",
            "category": "Graphs",
            "match_found": 0
        }

        mock_format_in_queue_key.return_value = f"inqueue:{self.user_one_id}"
        mock_get_user_queue_details.return_value = user_one_old_queue_details
        mock_check_user_found_match.return_value =True

        response = await terminate_previous_match_request(self.user_one_id, mock_matchmaking_conn, mock_message_conn)

        assert response is False
