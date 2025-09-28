from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "category" (
    "name" VARCHAR(100) NOT NULL PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS "difficulty" (
    "level" VARCHAR(50) NOT NULL PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS "question" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "difficulty_id" VARCHAR(50) NOT NULL REFERENCES "difficulty" ("level") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "question_category" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "category_id" VARCHAR(100) NOT NULL REFERENCES "category" ("name") ON DELETE CASCADE,
    "question_id" INT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_question_ca_categor_cefada" UNIQUE ("category_id", "question_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
