from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question_attempt" DROP CONSTRAINT IF EXISTS "question_attempt_title_key";
        DROP INDEX IF EXISTS "uid_question_at_title_6aeb75";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_question_at_title_6aeb75" ON "question_attempt" ("title");"""


MODELS_STATE = (
    "eJztmFtP2zAUgP9KlSeQugk6btpbKO3ogHaDsCEQitzETS0SpyTOoEL97zt2kuZSJ2sEhV"
    "bLW3su8TmfL8c+L4rjmtj2P6uMYWfCuhibQ2Q8KF8bLwpFDoYfRSbNhoImk8SACxga2sIH"
    "hcb6KG099JmHDAb6EbJ9DCIT+4ZHJoy4FKQ0sG0udA0wJNRKRAEljwHWmWthNsYeKO7uQU"
    "yoiZ+xH/+dPOgjgm0zEz0x+dhCrrPpRMh6lHWFIR9tqBuuHTg0MZ5M2dilc2tCGZdamGIP"
    "Mcw/z7yAh8+jizKOMwojTUzCEFM+Jh6hwGapdJdkYLiU84NofJGgxUf51NrdO9w7+nKwdw"
    "QmIpK55HAWppfkHjoKAn1NmQk9Yii0EBgTbumZy9LT8HMBvrRPDiKEnocYIyujGAsSjMnS"
    "eRuOJZC0zo3Gg3Z8/9Hmgv4v9bJ9ql5uXag320IzjTTng/632NyFRR7ugn77fHAsOCdcIS"
    "+fx6jHW6TSAi3w/veKXQ/Yb7Fo+U4fPUjXbJ7OItiu62Fi0TM8FXx7EB2iBpYwjE69n9En"
    "1eSLVbGu+iSYxYskliZDeOhpfiQWrR0QQKaYiazb6lVbPekogjLfyk/IM/UMbq5xW25OMr"
    "ddVDktJy9BFFkCBc+Ix19AW1KGJBNSXIZkC6IuQ+u2o8vKECPMxovo2mPkydnNHTalAMFu"
    "eNZtTC025tj290t4xfUHrLZzpSZStUJdtuakI6tQznNumwL0vSu6AeeOzo8XGzBU4bvgWB"
    "OWE/YBmTjGfQSwKjGWuNaU5ZRNMhoRAyKfVjokMl4124IzArK3XK8S2bRPzbXgZAiGDoG7"
    "nanHG73S4SD1rlnLWcMdGq7QAAtJHlYngIYRB8tB51xzhM3I93P8Yz15Kx5G5oDaUyW8RZ"
    "fx7110rjT14kdmEk5UrcM1rcwExNKtg9yVbv6Rxu+edtrgfxu3g35HEHR9ZnlixMROu1V4"
    "TChgrk7dJx2ZqQt/LI3BLL6ji598y3SFjiPP7tklhvuMfC8VtxLXb7qLntWZPRH42Isfl/"
    "7roFzDp17RZfhAIKvsCKSpSLoBOWjFnQAxUatvB9yFA4UP+IXh7utuwWq7BSn4y/YLUi6b"
    "UvjfoWNQd6n/ty71x9WP5ub1qVXsEWMsK0iRprQWocSm7kWv2b4tqy5/sOdLX5jF1SXlUl"
    "eX5CUJW6MCxMh8MwHu7uwsARCsCgEKXb7lTBmmksrx/WrQL2o2z11yIK8pJHhnEoM1Gzbx"
    "2f16Yi2hyLMub3fkOxvN7BOaf+BYVrXfs7zM/gL8+H9B"
)
