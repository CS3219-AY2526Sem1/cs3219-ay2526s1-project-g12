from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "question_attempt" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL UNIQUE,
    "description" TEXT NOT NULL,
    "code_template" TEXT NOT NULL,
    "solution_sample" TEXT NOT NULL,
    "difficulty" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "submitted_solution" TEXT NOT NULL,
    "attmpted_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "attempt_feedback" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "feedback" TEXT NOT NULL,
    "question_attempt_id" INT NOT NULL REFERENCES "question_attempt" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_question_attempt" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_id" VARCHAR(255) NOT NULL,
    "question_attempt_id" INT NOT NULL REFERENCES "question_attempt" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_questi_user_id_b1e90a" UNIQUE ("user_id", "question_attempt_id")
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


MODELS_STATE = (
    "eJztmFtP2zAUgP9K1SeQugk6btpbKO3ogHaDsCEQitzETS0Sp8TOoEL97zt2kuZSJyOCQt"
    "Hy1p5LfM7ny7HPU9P1LOywzxrn2J3yHsbWCJl3za+NpyZFLoYfRSatRhNNp4mBEHA0cqQP"
    "Co2Ncdp6xLiPTA76MXIYBpGFmemTKSceBSkNHEcIPRMMCbUTUUDJfYAN7tmYT7APiptbEB"
    "Nq4UfM4r/TO2NMsGNloieWGFvKDT6bSlmf8p40FKONDNNzApcmxtMZn3h0YU0oF1IbU+wj"
    "jsXnuR+I8EV0UcZxRmGkiUkYYsrHwmMUODyV7jMZmB4V/CAaJhO0xSif2ts7+zsHX/Z2Ds"
    "BERrKQ7M/D9JLcQ0dJYKA351KPOAotJMaEW3rmsvR0/FiAL+2Tgwih5yHGyMooxoIEY7J0"
    "XodjCSS9e6WLoF3G7h0hGPzSzjvH2vnGmXa1KTWzSHM6HHyLzT1Y5OEuGHROh4eSc8IV8m"
    "IiRiPeIpUWaIH3v1fsesB+jUUrdvr4Trlm83SWwfY8HxObnuCZ5NuH6BA1sYJhdOr9jD6p"
    "JV+sinXVJ8E8XiSxNBnCRw+LI7Fo7YAAMsVcZt3RLjraUbcpKYut/IB8y8jgFhqv7eUkC9"
    "tlldt28xJEkS1RiIxE/AW0FWVIMSHFZUi1IOoytG47uqwMccIdvIyuM0G+mt3C4XUK0Mr5"
    "uejRcDC1+URA290toRVXH7DazBWaSNUOddmKk46sQjHPudX1XF3PTTh1DHG4OIChCt8lx5"
    "qwmjADZPIQZwhgVWKscK0pqylbZDwmJkQ+q3RIZLxqtgVnBGRve34lsmmfmmvByRCMXAI3"
    "O8uIN3qlw0HpXbNWs4YbNFygARZSPKuOAA0nLlaDzrnmCFuR7+f4x3rybvoYWUPqzKI7YB"
    "n//ln3QtfOfmQm4UjTu0LTzkxALN3Yy13pFh9p/O7rxw3xt3E9HHQlQY9x25cjJnb6dVPE"
    "hALuGdR7MJCVuq7G0hjM8iu6+MH3nJ7QYeTZOznHcJ9R76XiRuL6TXfRozqzJwKG/fhpyV"
    "4G5RI+9YIewzsCWWU/IE1F0QvIQSvuA8iJWn0z4CYcKHy+Lw13W/cKVtsrSMF/brcg5fJR"
    "Cv8bdAzqHvX/1qN+v/rR+nhdag37xJyoClKkKa1FKLGpO9Frtm/Lqssf7DPlC7O4uqRc6u"
    "qSvCRha1SAGJl/TIDbW1vPAAhWhQClLt9yphxTReX4fjEcFDWbFy45kJcUEryxiMlbDYcw"
    "frueWEsoiqzL2x35zkYr+4QWHzhUVe23LC/zv5I4fqs="
)
