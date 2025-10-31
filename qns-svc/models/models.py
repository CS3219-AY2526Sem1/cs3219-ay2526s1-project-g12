from pydantic import BaseModel

from models.db_models import Question


class QuestionModel(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str
    code_template: str
    solution_sample: str
    categories: list[str]


def convert_question_orm_to_py_model(qns: Question, categories: list) -> QuestionModel:
    return QuestionModel(
        id=qns.id,
        title=qns.title,
        description=qns.description,
        difficulty=qns.difficulty.level,
        code_template=qns.code_template,
        solution_sample=qns.solution_sample,
        categories=categories,
    )
