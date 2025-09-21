from fastapi import FastAPI
from service.database_svc import register_database
from controllers.question_controller import (
    fetch_difficulty_levels,
    fetch_question_bank_categories,
    fetch_question_bank_category_difficulty_levels,
    fetch_question_details,
    fetch_all_questions,
    fetch_categories,
    fetch_single_question_from_bank,
)

app = FastAPI()
register_database(app)


@app.get("/")
async def root():
    return {"status": "working"}


@app.get("/questions/")
async def get_all_questions(start: int | None = None, end: int | None = None):
    return await fetch_all_questions(start, end)


@app.get("/questions/{question_id}")
async def get_question(question_id: int):
    return await fetch_question_details(question_id)


@app.get("/category/")
async def get_categories():
    return await fetch_categories()


@app.get("/difficulty/")
async def get_difficulty_levels():
    return await fetch_difficulty_levels()


@app.get("/pool/category/")
async def get_question_pool_categories():
    return await fetch_question_bank_categories()


@app.get("/pool/{category}/difficulty/")
async def get_question_pool_category_difficulty_levels(category: str):
    return await fetch_question_bank_category_difficulty_levels(category)


@app.get("/pool/{category}/{difficulty}/")
async def get_single_question_from_pool(category: str, difficulty: str):
    return await fetch_single_question_from_bank(category, difficulty)
