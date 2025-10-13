from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from controllers.question_controller import (
    _validate_categories,
    _validate_difficulty,
    _validate_question,
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
from models.db_models import Category, Difficulty, Question, QuestionCategory
from models.models import convert_question_orm_to_py_model


class TestValidateMethods:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_db_objects(self, init_test_db):
        self.valid_title = "Test Question"
        self.valid_description = "Test Description"
        self.valid_difficulty = "Test"
        self.valid_categories = ["Test"]
        cat = await Category.create(name=self.valid_categories[0])
        diff = await Difficulty.create(level=self.valid_difficulty)
        qns = await Question.create(
            title=self.valid_title,
            description=self.valid_description,
            difficulty=diff,
        )
        self.valid_id = qns.id
        await QuestionCategory.create(question=qns, category=cat)

    async def test_validate_categories_valid_category_success(self):
        try:
            await _validate_categories(self.valid_categories)
        except HTTPException:
            pytest.fail()

    async def test_validate_categories_invalid_category_failure(self):
        with pytest.raises(HTTPException):
            await _validate_categories(["Invalid"])

    async def test_validate_difficulty_valid_difficulty_success(self):
        try:
            await _validate_difficulty(self.valid_difficulty)
        except HTTPException:
            pytest.fail()

    async def test_validate_difficulty_invalid_difficulty_failure(self):
        with pytest.raises(HTTPException):
            await _validate_difficulty("Invalid")

    async def test_validate_question_valid_id_success(self):
        try:
            await _validate_question(self.valid_id)
        except HTTPException:
            pytest.fail()

    async def test_validate_question_not_exist_id_failure(self):
        with pytest.raises(HTTPException):
            await _validate_question(0)


class TestQuestionRelatedMethods:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_db_objects(self, init_test_db):
        self.valid_title = "Test Question"
        self.valid_description = "Test Description"
        self.valid_difficulty = "Test"
        self.valid_categories = ["Test"]
        self.cat = await Category.create(name=self.valid_categories[0])
        self.diff = await Difficulty.create(level=self.valid_difficulty)
        self.qns = await Question.create(
            title=self.valid_title,
            description=self.valid_description,
            difficulty=self.diff,
        )
        self.valid_id = self.qns.id
        self.qns_cat = await QuestionCategory.create(
            question=self.qns, category=self.cat
        )

    async def test_fetch_question_details_valid_id_success(self):
        try:
            expected_qns = convert_question_orm_to_py_model(
                self.qns, self.valid_categories
            )
            res = await fetch_question_details(self.valid_id)
            assert res == expected_qns
        except HTTPException:
            pytest.fail()

    async def test_fetch_question_details_not_exist_id_failure(self):
        with pytest.raises(HTTPException):
            await fetch_question_details(0)

    async def test_create_question_details_success(self):
        title = "Test Question New"
        description = "Test Description New"

        cqm = CreateQuestionModel(
            title=title,
            description=description,
            difficulty=self.valid_difficulty,
            categories=self.valid_categories,
        )

        try:
            await create_question_details(cqm)
        except HTTPException:
            pytest.fail()

    async def test_update_question_details_full_detail_success(self):
        title = "Test Question 2"
        description = "Test Description 2"
        difficulty = "Second"
        categories = ["Second"]
        categories.extend(self.valid_categories)
        await Difficulty.create(level=difficulty)
        await Category.create(name=categories[0])

        uqm = UpdateQuestionModel(
            title=title,
            description=description,
            difficulty=difficulty,
            categories=categories,
        )

        try:
            await update_question_details(self.valid_id, uqm)
        except HTTPException:
            pytest.fail()

        qns_db = await Question.get(id=self.valid_id).prefetch_related("difficulty")
        assert qns_db.title == title
        assert qns_db.description == description
        assert qns_db.difficulty.level == difficulty
        qns_cat_db = await QuestionCategory.filter(
            question_id=self.valid_id
        ).prefetch_related("category")
        assert len(qns_cat_db) == 2
        assert qns_cat_db[0].category.name == categories[0]
        assert qns_cat_db[1].category.name == categories[1]

    async def test_update_question_details_no_details_success(self):
        uqm = UpdateQuestionModel()

        try:
            await update_question_details(self.valid_id, uqm)
        except HTTPException:
            pytest.fail()

        qns_db = await Question.get(id=self.valid_id).prefetch_related("difficulty")
        assert qns_db == self.qns
        qns_cat_db = await QuestionCategory.filter(
            question_id=self.valid_id
        ).prefetch_related("category")
        assert len(qns_cat_db) == 1
        assert qns_cat_db[0] == self.qns_cat

    async def test_delete_question_details_success(self):
        await delete_question_details(self.valid_id)

        does_record_exist = await Question.filter(id=self.valid_id).exists()
        assert not does_record_exist

    async def test_fetch_all_questions_success(self):
        res = await fetch_all_questions()
        assert res["questions"] == [
            convert_question_orm_to_py_model(self.qns, self.valid_categories)
        ]
        res = await fetch_all_questions(1, 1)
        assert res["questions"] == [
            convert_question_orm_to_py_model(self.qns, self.valid_categories)
        ]


class TestCategoryRelatedMethods:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_db_objects(self, init_test_db):
        self.valid_categories = ["Test"]
        self.cat = await Category.create(name=self.valid_categories[0])

    async def test_fetch_categories_success(self):
        res = await fetch_categories()
        assert res["categories"] == self.valid_categories

    async def test_create_category_success(self):
        cdcm = CreateDeleteCategoryModel(name="Test2")

        try:
            await create_category(cdcm)
        except HTTPException:
            pytest.fail()

        assert await Category.filter(name="Test2").exists()

    async def test_create_category_already_exist_failure(self):
        cdcm = CreateDeleteCategoryModel(name="Test")

        with pytest.raises(HTTPException):
            await create_category(cdcm)

    async def test_update_category_success(self):
        ucm = UpdateCategoryModel(name="Test", new_name="Test2")

        try:
            await update_category(ucm)
        except HTTPException:
            pytest.fail()

        assert await Category.filter(name="Test2").exists()
        assert not await Category.filter(name="Test").exists()

    async def test_update_category_not_found_failure(self):
        ucm = UpdateCategoryModel(name="Test2", new_name="Test3")
        with pytest.raises(HTTPException):
            await update_category(ucm)

    async def test_update_category_new_name_already_exist_failure(self):
        await Category.create(name="Test2")
        ucm = UpdateCategoryModel(name="Test", new_name="Test2")

        with pytest.raises(HTTPException):
            await update_category(ucm)

    async def test_delete_category_success(self):
        await Category.create(name="Test2")
        cdcm = CreateDeleteCategoryModel(name="Test2")

        try:
            await delete_category(cdcm)
        except HTTPException:
            pytest.fail()

        assert not await Category.filter(name="Test2").exists()

    async def test_delete_category_not_found_failure(self):
        cdcm = CreateDeleteCategoryModel(name="Test2")

        with pytest.raises(HTTPException):
            await delete_category(cdcm)

    async def test_delete_category_in_use_failure(self):
        diff = await Difficulty.create(level="Test")
        qns = await Question.create(
            title="Test Title",
            description="Test Description",
            difficulty=diff,
        )
        await QuestionCategory.create(category=self.cat, question=qns)

        cdcm = CreateDeleteCategoryModel(name="Test")

        with pytest.raises(HTTPException):
            await delete_category(cdcm)


class TestDifficultyRelatedMethods:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_db_objects(self, init_test_db):
        self.valid_difficulty = "Test"
        self.diff = await Difficulty.create(level=self.valid_difficulty)

    async def test_fetch_difficulty_levels_success(self):
        res = await fetch_difficulty_levels()
        assert res["difficulties"] == [self.valid_difficulty]

    async def test_create_difficulty_success(self):
        cddm = CreateDeleteDifficultyModel(level="Test2")

        try:
            await create_difficulty_level(cddm)
        except HTTPException:
            pytest.fail()

        assert await Difficulty.filter(level="Test2").exists()

    async def test_create_difficulty_already_exist_failure(self):
        cddm = CreateDeleteDifficultyModel(level="Test")

        with pytest.raises(HTTPException):
            await create_difficulty_level(cddm)

    async def test_update_difficulty_success(self):
        udm = UpdateDifficultyModel(level="Test", new_level="Test2")

        try:
            await update_difficulty_level(udm)
        except HTTPException:
            pytest.fail()

        assert await Difficulty.filter(level="Test2").exists()

    async def test_update_difficulty_not_found_failure(self):
        udm = UpdateDifficultyModel(level="Test2", new_level="Test3")

        with pytest.raises(HTTPException):
            await update_difficulty_level(udm)

    async def test_update_difficulty_new_level_already_exist_failure(self):
        await Difficulty.create(level="Test2")
        udm = UpdateDifficultyModel(level="Test", new_level="Test2")

        with pytest.raises(HTTPException):
            await update_difficulty_level(udm)

    async def test_delete_difficulty_success(self):
        await Difficulty.create(level="Test2")
        cddm = CreateDeleteDifficultyModel(level="Test2")

        try:
            await delete_difficulty_level(cddm)
        except HTTPException:
            pytest.fail()

        assert not await Difficulty.filter(level="Test2").exists()

    async def test_delete_difficulty_not_found_failure(self):
        cddm = CreateDeleteDifficultyModel(level="Test2")

        with pytest.raises(HTTPException):
            await delete_difficulty_level(cddm)

    async def test_delete_difficulty_in_use_failure(self):
        await Question.create(
            title="Test Question",
            description="Test Description",
            difficulty_id=self.valid_difficulty,
        )

        cddm = CreateDeleteDifficultyModel(level=self.valid_difficulty)

        with pytest.raises(HTTPException):
            await delete_difficulty_level(cddm)


class TestQuestionBankRelatedMethods:
    @pytest.fixture(scope="function", autouse=True)
    async def setup_db_objects(self, init_test_db):
        self.valid_difficulty = "Test"
        self.valid_categories = ["Test"]
        cat = await Category.create(name=self.valid_categories[0])
        diff = await Difficulty.create(level=self.valid_difficulty)
        qns = await Question.create(
            title="Test Question",
            description="Test Description",
            difficulty=diff,
        )
        self.valid_id = qns.id
        await QuestionCategory.create(question=qns, category=cat)
        self.valid_qns_model = convert_question_orm_to_py_model(
            qns, self.valid_categories
        )

        self.alt_valid_difficulty = "Alt"
        self.alt_valid_categories = ["Alt"]
        await Category.create(name=self.alt_valid_categories[0])
        await Difficulty.create(level=self.alt_valid_difficulty)

    async def test_fetch_question_bank_categories_success(self):
        qns_bank_cat = await fetch_question_bank_categories()
        assert set(qns_bank_cat["categories"]) == set(self.valid_categories)
        assert self.alt_valid_categories[0] not in qns_bank_cat["categories"]

    async def test_fetch_question_bank_category_difficulty_levels_success(self):
        valid_cat_diff = await fetch_question_bank_category_difficulty_levels(
            self.valid_categories[0]
        )
        assert valid_cat_diff["difficulty_levels"] == [self.valid_difficulty]

        assert self.alt_valid_difficulty not in valid_cat_diff["difficulty_levels"]

    @patch("controllers.question_controller.random", new_callable=AsyncMock)
    async def test_fetch_single_question_from_bank_success(self, mock_random):
        mock_random.choice = MagicMock()
        mock_random.choice.return_value = self.valid_id

        valid_qns = await fetch_single_question_from_bank(
            self.valid_categories[0], self.valid_difficulty
        )
        assert valid_qns == self.valid_qns_model

    async def test_fetch_single_question_from_bank_no_question_exception(self):
        with pytest.raises(HTTPException):
            await fetch_single_question_from_bank(
                self.alt_valid_categories[0], self.alt_valid_difficulty
            )
