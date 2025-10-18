import pytest
from pydantic import ValidationError

from models.api_models import CreateQuestionModel, UpdateQuestionModel


class TestCreateQuestionModel:
    @classmethod
    def setup_class(cls):
        cls.valid_title = "Test Question"
        cls.valid_description = "Test Description"
        cls.valid_difficulty = "Test"
        cls.valid_code_template = "Code"
        cls.valid_solution_sample = "Soln"
        cls.valid_categories = ["Test"]

    def test_valid_question_success(self):
        try:
            CreateQuestionModel(
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )
        except ValidationError:
            pytest.fail()

    def test_empty_title_failure(self):
        with pytest.raises(ValidationError):
            CreateQuestionModel(
                title="",
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_empty_description_failure(self):
        with pytest.raises(ValidationError):
            CreateQuestionModel(
                title=self.valid_title,
                description="",
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_empty_difficulty_failure(self):
        with pytest.raises(ValidationError):
            CreateQuestionModel(
                title=self.valid_title,
                description=self.valid_description,
                difficulty="",
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_empty_code_template_failure(self):
        with pytest.raises(ValidationError):
            CreateQuestionModel(
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template="",
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_empty_solution_sample_failure(self):
        with pytest.raises(ValidationError):
            CreateQuestionModel(
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample="",
                categories=self.valid_categories,
            )

    def test_empty_categories_failure(self):
        with pytest.raises(ValidationError):
            CreateQuestionModel(
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=[],
            )


class TestUpdateQuestionModel:
    @classmethod
    def setup_class(cls):
        cls.valid_title = "Test Question"
        cls.valid_description = "Test Description"
        cls.valid_difficulty = "Test"
        cls.valid_code_template = "Code"
        cls.valid_solution_sample = "Soln"
        cls.valid_categories = ["Test"]

    def test_valid_filled_success(self):
        try:
            UpdateQuestionModel(
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )
        except ValidationError:
            pytest.fail()

    def test_valid_no_detail_success(self):
        try:
            UpdateQuestionModel(
                title=None,
                description=None,
                difficulty=None,
                code_template=None,
                solution_sample=None,
                categories=None,
            )
        except ValidationError:
            pytest.fail()

    def test_empty_title_failure(self):
        with pytest.raises(ValidationError):
            UpdateQuestionModel(title="")

    def test_empty_description_failure(self):
        with pytest.raises(ValidationError):
            UpdateQuestionModel(description="")

    def test_empty_difficulty_failure(self):
        with pytest.raises(ValidationError):
            UpdateQuestionModel(difficulty="")

    def test_empty_code_template_failure(self):
        with pytest.raises(ValidationError):
            UpdateQuestionModel(code_template="")

    def test_empty_solution_sample_failure(self):
        with pytest.raises(ValidationError):
            UpdateQuestionModel(solution_sample="")

    def test_empty_categories_failure(self):
        with pytest.raises(ValidationError):
            UpdateQuestionModel(categories=[])
