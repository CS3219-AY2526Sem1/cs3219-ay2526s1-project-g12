import asyncio

import pytest
from tortoise import Tortoise
from tortoise.contrib.test import (
    _init_db,
    getDBConfig,
)


# Acknowledgement and credits to gxpd-jjh
# Reused from: https://github.com/tortoise/tortoise-orm/issues/1110#issuecomment-1881967845
@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def init_test_db(request, event_loop):
    config = getDBConfig(app_label="models", modules=["models.db_models"])

    event_loop.run_until_complete(_init_db(config))

    request.addfinalizer(
        lambda: event_loop.run_until_complete(Tortoise._drop_databases())
    )
