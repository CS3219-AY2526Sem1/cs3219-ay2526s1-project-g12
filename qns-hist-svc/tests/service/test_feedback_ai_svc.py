import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_ai import ModelHTTPError

from models.db_models import AttemptFeedback, QuestionAttempt
from models.models import EvaluationOutput
from service.feedback_ai_svc import (
    evalation_question_attempt,
)


class TestEvaluateQuestionAttempt:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_db_objects(self, init_test_db):
        self.test_id = 1
        self.test_title = "Test Question"
        self.test_description = "Test Description"
        self.test_difficulty = "Test Diff"
        self.test_code_template = "Code"
        self.test_solution_sample = "Soln"
        self.test_category = "Test Cat"
        self.test_time_elapsed = 10
        self.test_submitted_solution = "Submitted"
        self.test_attempted_at = datetime.datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
        )
        self.test_feedback = "Test Feedback"
        self.qa = QuestionAttempt(
            title=self.test_title,
            description=self.test_description,
            code_template=self.test_code_template,
            solution_sample=self.test_solution_sample,
            difficulty=self.test_difficulty,
            category=self.test_category,
            time_elapsed=self.test_time_elapsed,
            submitted_solution=self.test_submitted_solution,
            attempted_at=self.test_attempted_at,
        )
        await self.qa.save()

    @patch(
        "service.feedback_ai_svc.cel",
        new_callable=AsyncMock,
    )
    @patch(
        "service.feedback_ai_svc.Tortoise",
        new_callable=AsyncMock,
    )
    @patch(
        "service.feedback_ai_svc.data_extraction_agent",
        new_callable=AsyncMock,
    )
    async def test_evaluate_question_attempt_success(
        self, mock_agent, mock_tortoise, mock_celery
    ):
        result_mock = MagicMock()
        result_mock.output = EvaluationOutput(feedback=self.test_feedback)
        mock_agent.run.return_value = result_mock

        await evalation_question_attempt(self.test_id)

        mock_agent.run.assert_called_once()
        af_db = await AttemptFeedback.filter(question_attempt_id=self.test_id).first()
        assert af_db.feedback == self.test_feedback

    @patch(
        "service.feedback_ai_svc.cel",
        new_callable=AsyncMock,
    )
    @patch(
        "service.feedback_ai_svc.Tortoise",
        new_callable=AsyncMock,
    )
    @patch(
        "service.feedback_ai_svc.data_extraction_agent",
        new_callable=AsyncMock,
    )
    async def test_evaluate_question_attempt_qa_not_exist(
        self, mock_agent, mock_tortoise, mock_celery
    ):
        await evalation_question_attempt(-1)

        mock_agent.run.assert_not_called()

    @patch(
        "service.feedback_ai_svc.cel",
        new_callable=AsyncMock,
    )
    @patch(
        "service.feedback_ai_svc.Tortoise",
        new_callable=AsyncMock,
    )
    @patch(
        "service.feedback_ai_svc.data_extraction_agent",
        new_callable=AsyncMock,
    )
    async def test_evaluate_question_attempt_agent_error_failure(
        self, mock_agent, mock_tortoise, mock_celery
    ):
        mock_agent.run.side_effect = ModelHTTPError(
            status_code=429, model_name="somename"
        )

        with pytest.raises(ModelHTTPError):
            await evalation_question_attempt(self.test_id)

        mock_agent.run.assert_called_once()
