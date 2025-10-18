import random

from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from models.api_models import (
    CreateDeleteCategoryModel,
    CreateDeleteDifficultyModel,
    CreateQuestionModel,
    UpdateCategoryModel,
    UpdateDifficultyModel,
    UpdateQuestionModel,
)
from models.db_models import (
    Category,
    Difficulty,
    Question,
    QuestionCategory,
)
from models.models import (
    convert_question_orm_to_py_model,
)
from utils.logger import log


async def _validate_categories(categories: list[str]) -> None:
    for cat in categories:
        is_valid_category = await Category.filter(name=cat).exists()
        if not is_valid_category:
            raise HTTPException(
                status_code=400, detail=f"Invalid Category '{cat}' provided"
            )


async def _validate_difficulty(difficulty: str) -> None:
    is_valid_difficulty = await Difficulty.filter(level=difficulty).exists()
    if not is_valid_difficulty:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Difficulty '{difficulty}' provided",
        )


async def _validate_question(question_id: int) -> None:
    is_valid_question = await Question.filter(id=question_id).exists()
    if not is_valid_question:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Question ID '{question_id}' provided",
        )


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


async def create_question_details(question: CreateQuestionModel) -> dict:
    log.info(f"Creating question details with title {question.title}")

    await _validate_categories(question.categories)
    await _validate_difficulty(question.difficulty)

    qns = await Question.create(
        title=question.title,
        description=question.description,
        difficulty_id=question.difficulty,
    )
    for category in question.categories:
        await QuestionCategory.create(question_id=qns.id, category_id=category)
    return {"message": "Question added successfully"}


async def update_question_details(
    question_id: int, updated_qns_details: UpdateQuestionModel
) -> dict:
    log.info(f"Updating question details with id {question_id}")
    await _validate_question(question_id)

    qns_update_dict = {}
    if updated_qns_details.title:
        qns_update_dict["title"] = updated_qns_details.title
    if updated_qns_details.description:
        qns_update_dict["description"] = updated_qns_details.description
    if updated_qns_details.difficulty:
        await _validate_difficulty(updated_qns_details.difficulty)
        qns_update_dict["difficulty_id"] = updated_qns_details.difficulty

    if qns_update_dict:
        qns = await Question.get(id=question_id)
        log.info(f"Updating Question of id {question_id} using: {qns_update_dict}")
        upd_qns = qns.update_from_dict(qns_update_dict)
        await upd_qns.save()

    if updated_qns_details.categories:
        await _validate_categories(updated_qns_details.categories)
        await QuestionCategory.filter(question_id=question_id).delete()
        await QuestionCategory.bulk_create([
            QuestionCategory(question_id=question_id, category_id=cat)
            for cat in updated_qns_details.categories
        ])

    return {"message": "Question updated successfully"}


async def delete_question_details(question_id: int) -> dict:
    log.info(f"Deleting question details with id {question_id}")
    await _validate_question(question_id)

    await QuestionCategory.filter(question_id=question_id).delete()
    await Question.filter(id=question_id).delete()
    return {"message": "Question deleted successfully"}


async def fetch_categories() -> dict:
    log.info("Fetching all categories")

    categories_db = await Category.all()

    categories_list = [cat.name for cat in categories_db]
    return {"categories": categories_list}


async def create_category(category: CreateDeleteCategoryModel) -> dict:
    does_category_exist = await Category.filter(name__iexact=category.name).exists()
    if does_category_exist:
        raise HTTPException(
            status_code=400, detail=f"Category {category.name} already exists"
        )

    await Category.create(name=category.name)

    return {"message": f"Category {category.name} created successfully"}


async def update_category(update_category: UpdateCategoryModel) -> dict:
    await _validate_categories([update_category.name])
    does_new_category_exist = await Category.filter(
        name__iexact=update_category.new_name
    ).exists()
    if does_new_category_exist:
        raise HTTPException(
            status_code=400,
            detail=f"Category {update_category.new_name} already exists",
        )

    await Category.create(name=update_category.new_name)
    await QuestionCategory.filter(category_id=update_category.name).update(
        category_id=update_category.new_name
    )
    await Category.filter(name=update_category.name).delete()

    return {
        "message": f"Category {update_category.name} updated to {update_category.new_name} successfully"
    }


async def delete_category(category: CreateDeleteCategoryModel) -> dict:
    await _validate_categories([category.name])

    is_category_in_use = await QuestionCategory.filter(
        category_id=category.name
    ).exists()
    if is_category_in_use:
        raise HTTPException(
            status_code=400,
            detail=f"Category {category.name} is currently in use. Unable to delete",
        )

    await Category.filter(name=category.name).delete()
    return {"message": f"Category {category.name} deleted successfully"}


async def fetch_difficulty_levels() -> dict:
    log.info("Fetching all difficulty levels")

    difficulty_db = await Difficulty.all()

    difficulties_list = [diff.level for diff in difficulty_db]
    return {"difficulties": difficulties_list}


async def create_difficulty_level(difficulty: CreateDeleteDifficultyModel) -> dict:
    does_difficulty_exist = await Difficulty.filter(
        level__iexact=difficulty.level
    ).exists()
    if does_difficulty_exist:
        raise HTTPException(
            status_code=400,
            detail=f"Difficulty level {difficulty.level} already exists",
        )

    await Difficulty.create(level=difficulty.level)

    return {"message": f"Difficulty level {difficulty.level} created successfully"}


async def update_difficulty_level(update_difficulty: UpdateDifficultyModel) -> dict:
    await _validate_difficulty(update_difficulty.level)
    does_new_difficulty_exist = await Difficulty.filter(
        level__iexact=update_difficulty.new_level
    ).exists()
    if does_new_difficulty_exist:
        raise HTTPException(
            status_code=400,
            detail=f"Difficulty level {update_difficulty.new_level} already exists",
        )

    await Difficulty.create(level=update_difficulty.new_level)
    await Question.filter(difficulty_id=update_difficulty.level).update(
        difficulty_id=update_difficulty.new_level
    )
    await Difficulty.filter(level=update_difficulty.level).delete()
    return {
        "message": f"Difficulty {update_difficulty.level} updated to {update_difficulty.new_level} successfully"
    }


async def delete_difficulty_level(difficulty: CreateDeleteDifficultyModel) -> dict:
    await _validate_difficulty(difficulty.level)

    is_difficulty_in_use = await Question.filter(
        difficulty_id=difficulty.level
    ).exists()
    if is_difficulty_in_use:
        raise HTTPException(
            status_code=400, detail=f"Difficulty level {difficulty.level} is in use"
        )

    await Difficulty.filter(level=difficulty.level).delete()
    return {"message": f"Difficulty {difficulty.level} deleted successfully"}


async def fetch_all_questions(start: int | None = None, end: int | None = None) -> dict:
    log.info("Fetching all questions")
    if start is not None and end is not None:
        qns_db_list = (
            await Question.all()
            .offset(start - 1)
            .limit(end - start + 1)
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
