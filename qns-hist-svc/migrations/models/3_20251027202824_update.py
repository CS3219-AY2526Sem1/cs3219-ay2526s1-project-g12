from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question_attempt" RENAME COLUMN "attmpted_at" TO "attempted_at";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question_attempt" RENAME COLUMN "attempted_at" TO "attmpted_at";"""


MODELS_STATE = (
    "eJztmG1P2zAQgP9KlU8gdQg63rRvobSjA9oNwoZAKHITN7VInBI7gwr1v892kualdkYEhV"
    "bkW3u+s+8en33xPWueb0OXbOmUQm9CuxDaQ2Dda98azxoGHmQ/VCrNhgYmk1SBCygYusIG"
    "RMrmKKs9JDQAFmXjI+ASyEQ2JFaAJhT5mElx6Lpc6FtMEWEnFYUYPYTQpL4D6RgGbOD2jo"
    "kRtuETJMnfyb05QtC1c94jm68t5CadToSsh2lXKPLVhqblu6GHU+XJlI59PNdGmHKpAzEM"
    "AIV8ehqE3H3uXRxxElHkaaoSuZixseEIhC7NhPtCBpaPOT/mDREBOnyVL62d3YPdw6/7u4"
    "dMRXgylxzMovDS2CNDQaBvaDMxDiiINATGlFt25/L0DPikwJe1KUBkrhchJsjKKCaCFGOa"
    "Om/DsQSS0bk2uNMeIQ8uF/R/6xftE/1i41y/3hQj03jkbND/nqj7LMmjU9Bvnw2OBOeUK4"
    "uLcB/N5IhUSlCF9f8zdjVgv0XS8pM+upfmbJHOItiuH0Dk4FM4FXx7zDuALShhGN96v+Ip"
    "9XTGqliXfRPMkiRJpOkSAXicX4mq3GECFimkIuq2ftnWjzuaoMyP8iMIbDOHm4/4Lb8gme"
    "suDnktrygBGDgCBY+I+6+gLSlDkg1RlyFZQtRlaNVOdFkZooi6cBFdewwCObu5wboUIHYa"
    "nkwXYoeOOba9vRJeSf1hWpuFUhMPtaKxfM3JelahnBfM1gXoe1d0i907Jr9eXIahCt8Fw5"
    "qwnDBhyMQ1TgCDVYmxxLSmLKdso9EIWczzaaVLImdVs1XcESx6xw8qkc3a1FzlXCnyoAld"
    "MCGwygdW0ewzvZ9yF2s49BD7NLbN5J6sdLdKretUladq/ARhtIDkYXrM2PCslJMu2hYY27"
    "HxVvJjNYlrAQT2ALtTLXqGlO1A77xzaejnP3PbcKwbHT7Sym1BIt3YL3wTzydp/OkZJw3+"
    "t3Ez6HcEQZ9QJxArpnrGjcZ9AiH1Tew/msDOvJgSaQJmsRGhfjMvZIGpbq8dxTN0Ty/YDa"
    "U4Veqe7Optu6o/kTsdIYFB8konr4NyxaZ6RbvmA4Ess7WSpSJpqxSgqVsqYqOW31e5jRaK"
    "OiELy93VbZfltl0y8F/aeMmYrMsnwDu0Xup2/2dr939c/WiuX8NfhwGyxrKCFI+U1iKQ6t"
    "RN/RU7t2XV5S8MiPStqa4uGZO6uqSvCXY0KkCM1dcT4M729gsAMi0lQDFW7N1jCrGkcvy4"
    "HPRVXfu5SQHkFWYB3trIos2Giwi9W02sJRR51OWNj2KPo5l/SvMJjmRV+z3Ly+wf0Wfoiw"
    "=="
)
