from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header

from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)
from controllers.history_controller import (
    fetch_question_history_details_by_user_id,
    submit_question_attempt,
)
from models.api_models import SubmitQuestionAttemptModel
from service.database_svc import register_database
from utils.logger import log


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    register_self_as_service(app)
    hc_task = register_heartbeat()

    yield

    hc_task.cancel()


app = FastAPI(
    title="PeerPrep Question History Service",
    lifespan=lifespan,
)

register_database(app)

ADMIN_ROLE = "admin"
USER_ROLE = "user"


@app.get("/")
async def root():
    return {"status": "working"}


@app.get("/attempts", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def get_fetch_question_history_details(
    x_user_id: Annotated[str, Header()],
):
    log.info(f"Fetching question history details for user {x_user_id}")
    return await fetch_question_history_details_by_user_id(x_user_id)


@app.post("/attempts", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def post_submit_question_attempt(attempt: SubmitQuestionAttemptModel):
    log.info(
        f"Submitting question attempt:\nQuestion: {attempt.title}\nUser: {attempt.users}"
    )
    return await submit_question_attempt(attempt)
