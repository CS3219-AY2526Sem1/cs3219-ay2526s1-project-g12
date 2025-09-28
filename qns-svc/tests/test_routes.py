from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from models.api_models import CreateQuestionModel, UpdateQuestionModel
from routes import app


class TestRoutes:
    @classmethod
    def setup_class(cls):
        cls.valid_id = 1
        cls.valid_title = "Test Question"
        cls.valid_description = "Test Description"
        cls.valid_difficulty = "Test"
        cls.valid_categories = ["Test"]

    @patch("routes.fetch_all_questions", new_callable=AsyncMock)
    async def test_get_all_questions_success(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/questions/")

        mock_fetch.assert_called_once()

    @patch("routes.fetch_all_questions", new_callable=AsyncMock)
    async def test_get_all_questions_with_start_end_params_success(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/questions/?start=1&end=10")

        mock_fetch.assert_called_once_with(1, 10)

    @patch("routes.fetch_question_details", new_callable=AsyncMock)
    async def test_get_question_with_valid_id_success(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/questions/1")
        mock_fetch.assert_called_once_with(1)

    @patch("routes.fetch_question_details", new_callable=AsyncMock)
    async def test_get_question_with_invalid_id_failure(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/questions/invalid")
        mock_fetch.assert_not_called()

    @patch("routes.create_question_details", new_callable=AsyncMock)
    async def test_post_create_question_valid_payload_success(self, mock_fetch):
        mock_fetch.return_value = {}
        json_payload = {
            "title": self.valid_title,
            "description": self.valid_description,
            "categories": self.valid_categories,
            "difficulty": self.valid_difficulty,
        }
        expected_qns = CreateQuestionModel(**json_payload)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.post("/questions/", json=json_payload)
        mock_fetch.assert_called_once_with(expected_qns)

    @patch("routes.create_question_details", new_callable=AsyncMock)
    async def test_post_create_question_invalid_payload_failure(self, mock_fetch):
        mock_fetch.return_value = {}
        json_payload = {}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.post("/questions/", json=json_payload)
        mock_fetch.assert_not_called()

    @patch("routes.update_question_details", new_callable=AsyncMock)
    async def test_put_update_question_valid_payload_success(self, mock_fetch):
        mock_fetch.return_value = {}
        json_payload = {}
        uqm = UpdateQuestionModel()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.put("/questions/1", json=json_payload)
        mock_fetch.assert_called_once_with(1, uqm)

    @patch("routes.update_question_details", new_callable=AsyncMock)
    async def test_put_update_question_invalid_payload_failure(self, mock_fetch):
        mock_fetch.return_value = {}
        json_payload = {"categories": []}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.put("/questions/1", json=json_payload)
        mock_fetch.assert_not_called()

    @patch("routes.delete_question_details", new_callable=AsyncMock)
    async def test_delete_delete_question(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.delete("/questions/1")
        mock_fetch.assert_called_once_with(1)

    @patch("routes.fetch_categories", new_callable=AsyncMock)
    async def test_get_categories(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/category/")
        mock_fetch.assert_called_once()

    @patch("routes.fetch_difficulty_levels", new_callable=AsyncMock)
    async def test_get_difficulty_levels(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/difficulty/")
        mock_fetch.assert_called_once()

    @patch("routes.fetch_question_bank_categories", new_callable=AsyncMock)
    async def test_get_question_pool_categories(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get("/pool/category/")
        mock_fetch.assert_called_once()

    @patch(
        "routes.fetch_question_bank_category_difficulty_levels", new_callable=AsyncMock
    )
    async def test_get_question_pool_category_difficulty_levels(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get(f"/pool/{self.valid_categories[0]}/difficulty/")
        mock_fetch.assert_called_once_with(self.valid_categories[0])

    @patch("routes.fetch_single_question_from_bank", new_callable=AsyncMock)
    async def test_get_single_question_from_bank(self, mock_fetch):
        mock_fetch.return_value = {}
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.get(f"/pool/{self.valid_categories[0]}/{self.valid_difficulty}/")
        mock_fetch.assert_called_once_with(
            self.valid_categories[0], self.valid_difficulty
        )
