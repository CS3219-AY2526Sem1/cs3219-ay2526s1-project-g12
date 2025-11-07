from asyncio import log
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)
from controllers.question_controller import (
    create_category,
    create_difficulty_level,
    create_question_details,
    delete_category,
    delete_difficulty_level,
    delete_question_details,
    fetch_all_questions,
    fetch_categories,
    fetch_difficulty_levels,
    fetch_question_bank_categories,
    fetch_question_bank_category_difficulty_levels,
    fetch_question_details,
    fetch_single_question_from_bank,
    update_category,
    update_difficulty_level,
    update_question_details,
)
from models.api_models import (
    CreateDeleteCategoryModel,
    CreateDeleteDifficultyModel,
    CreateQuestionModel,
    UpdateCategoryModel,
    UpdateDifficultyModel,
    UpdateQuestionModel,
)
from service.database_svc import register_database

@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    register_self_as_service(app)
    hc_task = register_heartbeat()

    yield

    hc_task.cancel()


app = FastAPI(
    title="PeerPrep Question Service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_database(app)

ADMIN_ROLE = "admin"
USER_ROLE = "user"


@app.get("/")
async def root():
    return {"status": "working"}


@app.get("/questions/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def get_all_questions(start: int | None = None, end: int | None = None):
    return await fetch_all_questions(start, end)


@app.get("/questions/{question_id}", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def get_question(question_id: int):
    return await fetch_question_details(question_id)


@app.post("/questions/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def post_create_question(question: CreateQuestionModel):
    return await create_question_details(question)


@app.put("/questions/{question_id}", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def put_update_question(
    question_id: int, updated_qns_details: UpdateQuestionModel
):
    return await update_question_details(question_id, updated_qns_details)


@app.delete("/questions/{question_id}", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def delete_delete_question(question_id: int):
    return await delete_question_details(question_id)


@app.get("/category/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def get_categories():
    return await fetch_categories()


@app.post("/category/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def post_create_category(category: CreateDeleteCategoryModel):
    return await create_category(category)


@app.put("/category/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def put_update_category(category: UpdateCategoryModel):
    return await update_category(category)


@app.delete("/category/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def delete_delete_category(category: CreateDeleteCategoryModel):
    return await delete_category(category)


@app.get("/difficulty/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def get_difficulty_levels():
    return await fetch_difficulty_levels()


@app.post("/difficulty/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def post_create_difficulty_level(difficulty: CreateDeleteDifficultyModel):
    return await create_difficulty_level(difficulty)


@app.put("/difficulty/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def put_update_difficulty_level(difficulty: UpdateDifficultyModel):
    return await update_difficulty_level(difficulty)


@app.delete("/difficulty/", openapi_extra={"x-roles": [ADMIN_ROLE]})
async def delete_delete_difficulty_level(difficulty: CreateDeleteDifficultyModel):
    return await delete_difficulty_level(difficulty)


@app.get("/pool/category/", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def get_question_pool_categories():
    return await fetch_question_bank_categories()


@app.get(
    "/pool/{category}/difficulty/", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]}
)
async def get_question_pool_category_difficulty_levels(category: str):
    return await fetch_question_bank_category_difficulty_levels(category)


@app.get(
    "/pool/{category}/{difficulty}/", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]}
)
async def get_single_question_from_pool(category: str, difficulty: str):
    return  await fetch_single_question_from_bank(category, difficulty)
