import random
from fastapi import HTTPException
from utils.logger import log
from models.db_models import (
    Question,
    Category,
    Difficulty,
    QuestionCategory,
)
from models.models import (
    convert_question_orm_to_py_model,
)
from tortoise.exceptions import DoesNotExist


async def fetch_question_details(question_id: int) -> object:
    log.info(f"Fetching question details with id {question_id}")

    try:
        qns_db = await Question.get(id=question_id).prefetch_related("difficulty")
        qns_cat_db = await QuestionCategory.filter(
            question_id=question_id
        ).prefetch_related("category")

        qns_cat = [str(cat.category) for cat in qns_cat_db]
        return convert_question_orm_to_py_model(qns_db, qns_cat)

    except DoesNotExist:
        raise HTTPException(status_code=400, detail="Invalid Question ID supplied")


async def fetch_categories() -> dict:
    log.info("Fetching all categories")

    categories_db = await Category.all()

    categories_list = [cat.name for cat in categories_db]
    return {"categories": categories_list}


async def fetch_difficulty_levels() -> dict:
    log.info("Fetching all difficulty levels")

    difficulty_db = await Difficulty.all()

    difficulties_list = [diff.level for diff in difficulty_db]
    return {"difficulties": difficulties_list}


async def fetch_all_questions(start: int | None = None, end: int | None = None) -> dict:
    log.info("Fetching all questions")
    if start is not None and end is not None:
        qns_db_list = (
            await Question.all()
            .offset(start)
            .limit(end - start)
            .prefetch_related("difficulty")
        )
    else:
        qns_db_list = await Question.all().prefetch_related("difficulty")

    qns_list = []
    for qns in qns_db_list:
        qns_cat_db = await QuestionCategory.filter(question_id=qns.id).prefetch_related(
            "category"
        )
        qns_cat = [str(cat.category) for cat in qns_cat_db]
        qns_list.append(convert_question_orm_to_py_model(qns, qns_cat))

    return {"questions": qns_list}


async def fetch_question_bank_categories() -> dict:
    log.info("Fetching question bank categories")
    bank_cat_db = (
        await QuestionCategory.all()
        .prefetch_related("category")
        .distinct()
        .values("category__name")
    )
    bank_cat = [cat["category__name"] for cat in bank_cat_db]
    return {"categories": bank_cat}


async def fetch_question_bank_category_difficulty_levels(category: str) -> dict:
    log.info(f"Fetching question bank category difficulty levels for {category}")

    bank_cat_diff_db = (
        await QuestionCategory.filter(category__name=category)
        .prefetch_related("question__difficulty")
        .distinct()
        .values("question__difficulty__level")
    )

    bank_diff = [diff["question__difficulty__level"] for diff in bank_cat_diff_db]
    return {"difficulty_levels": bank_diff}


async def fetch_single_question_from_bank(category: str, difficulty: str) -> object:
    log.info(f"Fetching single question from pool for {category} and {difficulty}")

    cat_diff_qns_id = await QuestionCategory.filter(
        category__name=category, question__difficulty__level=difficulty
    ).values("question__id")

    id_list = [qns["question__id"] for qns in cat_diff_qns_id]
    if len(id_list) == 0:
        raise HTTPException(status_code=400, detail="Invalid category or difficulty")
    qns_id = random.choice(id_list)

    return await fetch_question_details(qns_id)
