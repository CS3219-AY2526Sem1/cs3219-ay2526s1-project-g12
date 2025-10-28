import datetime
from unittest.mock import MagicMock, patch

import pytest

from controllers.history_controller import (
    fetch_question_history_details_by_user_id,
    submit_question_attempt,
)
from models.api_models import SubmitQuestionAttemptModel
from models.db_models import AttemptFeedback, QuestionAttempt, UserAttempt
from models.models import convert_question_attempt_orm_to_py_model


class TestFetchQuestionHistoryDetailsByUserId:
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
        self.test_users = ["TestUser", "TestUser2"]
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
        for u in self.test_users:
            await UserAttempt.create(user_id=u, question_attempt=self.qa)
        await AttemptFeedback.create(
            feedback=self.test_feedback, question_attempt=self.qa
        )

        await self.qa.fetch_related("attempt_feedback")

    async def test_fetch_question_history_details_by_user_id(self):
        expected_qns_list = [convert_question_attempt_orm_to_py_model(self.qa)]

        actual_qns_list = await fetch_question_history_details_by_user_id(
            self.test_users[0]
        )

        assert expected_qns_list == actual_qns_list


class TestSubmitQuestionAttempt:
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
        self.test_users = ["TestUser", "TestUser2"]

    @patch(
        "controllers.history_controller.run_evalation_question_attempt",
        new_callable=MagicMock,
    )
    async def test_submit_question_attempt_success(
        self, mock_run_evalation_question_attempt
    ):
        sqam = SubmitQuestionAttemptModel(
            title=self.test_title,
            description=self.test_description,
            code_template=self.test_code_template,
            solution_sample=self.test_solution_sample,
            difficulty=self.test_difficulty,
            category=self.test_category,
            time_elapsed=self.test_time_elapsed,
            submitted_solution=self.test_submitted_solution,
            users=self.test_users,
        )

        await submit_question_attempt(sqam)

        qa_db = await QuestionAttempt.filter(title=self.test_title).first()
        assert mock_run_evalation_question_attempt.delay.called
        assert qa_db is not None
        ua_db = await UserAttempt.filter(question_attempt=qa_db)
        assert len(ua_db) == len(self.test_users)
