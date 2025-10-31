import datetime

import pytest
from pydantic import ValidationError

from models.db_models import AttemptFeedback, QuestionAttempt
from models.models import (
    FEEDBACK_NOT_AVAILABLE_YET,
    QuestionAttemptModel,
    convert_question_attempt_orm_to_py_model,
)


async def test_convert_question_attempt_orm_to_py_model(init_test_db):
    test_id = 1
    test_title = "Test Question"
    test_description = "Test Description"
    test_difficulty = "Test Diff"
    test_code_template = "Code"
    test_solution_sample = "Soln"
    test_category = "Test Cat"
    test_time_elapsed = 10
    test_submitted_solution = "Submitted"
    test_attempted_at = datetime.datetime(
        2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
    )
    test_feedback = "Test Feedback"

    qa_db = QuestionAttempt(
        title=test_title,
        description=test_description,
        code_template=test_code_template,
        solution_sample=test_solution_sample,
        difficulty=test_difficulty,
        category=test_category,
        time_elapsed=test_time_elapsed,
        submitted_solution=test_submitted_solution,
        attempted_at=test_attempted_at,
    )
    await qa_db.save()
    await qa_db.fetch_related("attempt_feedback")

    test_qa = convert_question_attempt_orm_to_py_model(qa_db)
    excpected_qa = QuestionAttemptModel(
        id=test_id,
        title=test_title,
        description=test_description,
        code_template=test_code_template,
        solution_sample=test_solution_sample,
        difficulty=test_difficulty,
        category=test_category,
        time_elapsed=test_time_elapsed,
        submitted_solution=test_submitted_solution,
        attempted_at=test_attempted_at,
        feedback=FEEDBACK_NOT_AVAILABLE_YET,
    )

    assert test_qa == excpected_qa

    af_db = AttemptFeedback(feedback=test_feedback, question_attempt=qa_db)
    await af_db.save()
    await qa_db.fetch_related("attempt_feedback")

    test_qa = convert_question_attempt_orm_to_py_model(qa_db)
    excpected_qa = QuestionAttemptModel(
        id=test_id,
        title=test_title,
        description=test_description,
        code_template=test_code_template,
        solution_sample=test_solution_sample,
        difficulty=test_difficulty,
        category=test_category,
        time_elapsed=test_time_elapsed,
        submitted_solution=test_submitted_solution,
        attempted_at=test_attempted_at,
        feedback=test_feedback,
    )

    assert test_qa == excpected_qa


class TestQuestionAttemptModel:
    @classmethod
    def setup_class(cls):
        cls.test_id = 1
        cls.test_title = "Test Question"
        cls.test_description = "Test Description"
        cls.test_difficulty = "Test Diff"
        cls.test_code_template = "Code"
        cls.test_solution_sample = "Soln"
        cls.test_category = "Test Cat"
        cls.test_time_elapsed = 10
        cls.test_submitted_solution = "Submitted"
        cls.test_attempted_at = datetime.datetime(
            2025, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc
        )
        cls.test_feedback = "Test Feedback"

    def test_valid_question_attempt_success(self):
        try:
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )
        except ValidationError:
            pytest.fail()

    def test_valid_question_attempt_id_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=None,  # type: ignore
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_title_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=None,  # type: ignore
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_description_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=None,  # type: ignore
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_code_template_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=None,  # type: ignore
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_solution_sample_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=None,  # type: ignore
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_difficulty_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=None,  # type: ignore
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_category_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=None,  # type: ignore
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_time_elapsed_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=None,  # type: ignore
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_submitted_solution_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=None,  # type: ignore
                attempted_at=self.test_attempted_at,
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_attempted_at_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=None,  # type: ignore
                feedback=self.test_feedback,
            )

    def test_valid_question_attempt_feedback_failure(self):
        with pytest.raises(ValidationError):
            QuestionAttemptModel(
                id=self.test_id,
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                attempted_at=self.test_attempted_at,
                feedback=None,  # type: ignore
            )
