from datetime import datetime

from pydantic import BaseModel

from models.db_models import QuestionAttempt

FEEDBACK_NOT_AVAILABLE_YET = "AI feedback is still under processing"


class QuestionAttemptModel(BaseModel):
    id: int
    title: str
    description: str
    code_template: str
    solution_sample: str
    difficulty: str
    category: str
    submitted_solution: str
    attmpted_at: datetime
    feedback: str


def convert_question_attempt_orm_to_py_model(attempt: QuestionAttempt):
    feedback = FEEDBACK_NOT_AVAILABLE_YET

    if attempt.attempt_feedback:
        feedback = attempt.attempt_feedback[0].feedback

    return QuestionAttemptModel(
        id=attempt.id,
        title=attempt.title,
        description=attempt.description,
        code_template=attempt.code_template,
        solution_sample=attempt.solution_sample,
        difficulty=attempt.difficulty,
        category=attempt.category,
        submitted_solution=attempt.submitted_solution,
        attmpted_at=attempt.attmpted_at,
        feedback=feedback,
    )


class EvaluationOutput(BaseModel):
    feedback: str
