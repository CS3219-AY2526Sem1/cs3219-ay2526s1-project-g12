import pytest
from pydantic import ValidationError

from models.db_models import Difficulty, Question
from models.models import QuestionModel, convert_question_orm_to_py_model


async def test_convert_question_orm_to_py_model(init_test_db):
    test_id = 1
    test_title = "Test Question"
    test_description = "Test Description"
    test_difficulty = "Test"
    test_code_template = "Code"
    test_solution_sample = "Soln"
    test_categories = ["Test"]

    diff_db = Difficulty(level=test_difficulty)
    await diff_db.save()

    qns_db = Question(
        title=test_title,
        description=test_description,
        code_template=test_code_template,
        solution_sample=test_solution_sample,
        difficulty=diff_db,
    )
    await qns_db.save()

    test_qns = convert_question_orm_to_py_model(qns_db, test_categories)
    expected_qns = QuestionModel(
        id=test_id,
        title=test_title,
        description=test_description,
        difficulty=test_difficulty,
        code_template=test_code_template,
        solution_sample=test_solution_sample,
        categories=test_categories,
    )

    assert test_qns == expected_qns


class TestQuestionModel:
    @classmethod
    def setup_class(cls):
        cls.valid_id = 1
        cls.valid_title = "Test Question"
        cls.valid_description = "Test Description"
        cls.valid_difficulty = "Test"
        cls.valid_code_template = "Code"
        cls.valid_solution_sample = "Soln"
        cls.valid_categories = ["Test"]

    def test_valid_question_success(self):
        try:
            QuestionModel(
                id=self.valid_id,
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )
        except ValidationError:
            pytest.fail()

    def test_invalid_question_id_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=None,  # type: ignore
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_invalid_question_title_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=self.valid_id,
                title=None,  # type: ignore
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_invalid_question_description_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=self.valid_id,
                title=self.valid_title,
                description=None,  # type: ignore
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_invalid_question_difficulty_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=self.valid_id,
                title=self.valid_title,
                description=self.valid_description,
                difficulty=None,  # type: ignore
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_invalid_question_code_template_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=self.valid_id,
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=None,  # type: ignore
                solution_sample=self.valid_solution_sample,
                categories=self.valid_categories,
            )

    def test_invalid_question_solution_sample_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=self.valid_id,
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=None,  # type: ignore,
                categories=self.valid_categories,
            )

    def test_invalid_question_categories_failure(self):
        with pytest.raises(ValidationError):
            QuestionModel(
                id=self.valid_id,
                title=self.valid_title,
                description=self.valid_description,
                difficulty=self.valid_difficulty,
                code_template=self.valid_code_template,
                solution_sample=self.valid_solution_sample,
                categories=None,  # type: ignore
            )
