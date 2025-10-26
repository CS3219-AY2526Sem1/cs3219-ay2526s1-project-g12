from models.api_models import SubmitQuestionAttemptModel
from models.db_models import QuestionAttempt, UserAttempt
from utils.logger import log


async def fetch_question_history_details_by_user_id(
    user_id: str,
) -> list[QuestionAttempt]:
    log.info(f"Fetching question history details for user_id: {user_id}")
    qa_db = await QuestionAttempt.filter(user_attempts__user_id=user_id)
    log.debug(qa_db)
    return qa_db


async def submit_question_attempt(sqam: SubmitQuestionAttemptModel) -> dict:
    log.info(f"Submitting question attempt for user_id: {sqam.users}")
    qa_db = await QuestionAttempt.create(
        title=sqam.title,
        description=sqam.description,
        code_template=sqam.code_template,
        solution_sample=sqam.solution_sample,
        difficulty=sqam.difficulty,
        category=sqam.category,
        submitted_solution=sqam.submitted_solution,
    )
    for user_id in sqam.users:
        await UserAttempt.create(user_id=user_id, question_attempt=qa_db)

    return {"status": "success", "message": "Attempt successfully logged"}
