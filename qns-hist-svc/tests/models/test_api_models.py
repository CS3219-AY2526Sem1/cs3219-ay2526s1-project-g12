import pytest
from pydantic import ValidationError

from models.api_models import SubmitQuestionAttemptModel


class TestSubmitQuestionAttemptModel:
    @classmethod
    def setup_class(cls):
        cls.test_title = "Test Question"
        cls.test_description = "Test Description"
        cls.test_difficulty = "Test Diff"
        cls.test_code_template = "Code"
        cls.test_solution_sample = "Soln"
        cls.test_category = "Test Cat"
        cls.test_time_elapsed = 10
        cls.test_submitted_solution = "Submitted"
        cls.test_users = ["Test User", "Test User 2"]

    def test_valid_question_attempt_success(self):
        try:
            SubmitQuestionAttemptModel(
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
        except ValidationError:
            pytest.fail()

    def test_empty_title_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title="",
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_empty_description_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description="",
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_empty_code_template_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template="",
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_empty_solution_sample_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample="",
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_empty_difficulty_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty="",
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_empty_category_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category="",
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_time_elapsed_zero_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=0,
                submitted_solution=self.test_submitted_solution,
                users=self.test_users,
            )

    def test_empty_submitted_solution_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution="",
                users=self.test_users,
            )

    def test_empty_users_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=[],
            )

    def test_single_users_failure(self):
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=[self.test_users[0]],
            )

    def test_too_many_users_failure(self):
        more_users = ["Test User 3"]
        more_users.extend(self.test_users)
        with pytest.raises(ValidationError):
            SubmitQuestionAttemptModel(
                title=self.test_title,
                description=self.test_description,
                code_template=self.test_code_template,
                solution_sample=self.test_solution_sample,
                difficulty=self.test_difficulty,
                category=self.test_category,
                time_elapsed=self.test_time_elapsed,
                submitted_solution=self.test_submitted_solution,
                users=more_users,
            )
