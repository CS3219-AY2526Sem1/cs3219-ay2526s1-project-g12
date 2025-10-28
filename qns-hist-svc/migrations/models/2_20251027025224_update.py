from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question_attempt" ADD "time_elapsed" INT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "question_attempt" DROP COLUMN "time_elapsed";"""


MODELS_STATE = (
    "eJztmG1P2zAQgP9KlU8gMQQdb9q3UMrogHaDsiEQitzETS0Sp8TOoEL97zs7SfNSJyOCQi"
    "vyrT3f2XePz774njXXs7DDNnXOsTvmxxhbA2Tea98azxpFLoYfRSobDQ2Nx4mCEHA0cKQN"
    "CpWNYVp7wLiPTA7jQ+QwDCILM9MnY048ClIaOI4QeiYoEmonooCShwAb3LMxH2EfBm7vQE"
    "yohZ8wi/+O740hwY6V8Z5YYm0pN/hkLGUdyo+lolhtYJieE7g0UR5P+MijM21CuZDamGIf"
    "cSym534g3BfeRRHHEYWeJiqhiykbCw9R4PBUuC9kYHpU8ANvmAzQFqt8aW7v7O8cfN3bOQ"
    "AV6clMsj8Nw0tiDw0lgW5fm8pxxFGoITEm3NI7l6XXx08F+NI2OYjgeh5ijKyMYixIMCap"
    "8zYcSyD129d94bTL2IMjBN3f+kXrRL9YO9ev1+XIJBo563W/x+oeJHl4Crqts96h5Jxwhb"
    "iY8NGIj0ilBC2w/n/GLgfst0hacdKH98qczdOZB3vs+ZjY9BRPJN8OeIeoiRUMo1vvVzSl"
    "nsxYFeuib4JpnCSxNFnCR4+zK7Eod0AAkWIuo27ply39qK1JyuIoPyLfMjK4xYjX9HKSme"
    "78kNt08xJEkS1RiIiE/wW0FWVIsSHFZUiVEHUZWrYTXVaGOOEOnkfXGiFfzW5msCoFCE7D"
    "k+FgavORwLa7W8Irrj+gtZ4rNdFQMxzL1py0ZxXKec5sVYC+d0U34d4xxPXiAIYqfOcMa8"
    "JqwgyQyWucIYBVibHCtKaspmyR4ZCY4Pmk0iWRsarZFtwREL3t+ZXIpm1qrmqunLjYwA4a"
    "M1zlAytv9pneT5mLNRi4BD6NLSO+JyvdrUrrOlXVqQpPEHiBACykeJceARqRlGrQOdMcYS"
    "uy3Yx/LCdvzcfI6lFnooWPkDL+nfP2ZV8//5nZhCO93xYjzcwGxNK1vdwX8WySxp9O/6Qh"
    "/jZuet22JOgxbvtyxUSvf6MJn1DAPYN6jwayUu+lWBqDmW9DFL+YMzkw1xbNJsJhNMPx6Q"
    "XcTwVnqrgju3zbXtSdyJyNgGE/fqOz10G5gqle0az5QCCLbKykqSiaKjloxQ0VuVGL76rc"
    "hguFfZC55e7qpstimy4p+C9tu6RMVuUD4B0aL3Wz/7M1+z+ufmysXrtfxz4xR6qCFI2U1i"
    "KU6NQt/SU7t2XV5S/2mfKlWVxdUiZ1dUleE3A0KkCM1FcT4PbW1gsAglYhQDmW79xTjqmi"
    "cvy47HWLevYzkxzIKwoB3lrE5BsNhzB+t5xYSyiKqMvbHvkOx0b2KS0mOFRV7fcsL9N/lU"
    "fnwQ=="
)
