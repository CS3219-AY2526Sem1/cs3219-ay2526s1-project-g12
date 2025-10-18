from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question" ADD "code_template" TEXT NOT NULL;
        ALTER TABLE "question" ADD "solution_sample" TEXT NOT NULL;
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_question_title_3b06d3" ON "question" ("title");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_question_title_3b06d3";
        ALTER TABLE "question" DROP COLUMN "code_template";
        ALTER TABLE "question" DROP COLUMN "solution_sample";"""
