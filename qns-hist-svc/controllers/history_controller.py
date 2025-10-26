from models.api_models import SubmitQuestionAttemptModel
from models.db_models import QuestionAttempt, UserAttempt
from models.models import QuestionAttemptModel, convert_question_attempt_orm_to_py_model
from service.feedback_ai_svc import evalation_question_attempt
from utils.logger import log


async def fetch_question_history_details_by_user_id(
    user_id: str,
) -> list[QuestionAttemptModel]:
    log.info(f"Fetching question history details for user_id: {user_id}")

    qa_db = await QuestionAttempt.filter(
        user_attempts__user_id=user_id
    ).prefetch_related("attempt_feedback")

    qam_list = [convert_question_attempt_orm_to_py_model(qa) for qa in qa_db]
    log.debug(qam_list)
    return qam_list


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

    await evalation_question_attempt(qa_db.id)  # type: ignore

    return {"status": "success", "message": "Attempt successfully logged"}
