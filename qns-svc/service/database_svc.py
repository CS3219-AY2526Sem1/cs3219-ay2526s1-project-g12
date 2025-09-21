from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from utils.utils import get_envvar
from utils.logger import log

ORM_CONFIG = {
    "connections": {"default": get_envvar("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["models.db_models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


def register_database(app: FastAPI):
    log.info("Registering Services")
    Tortoise.init_models(ORM_CONFIG["apps"]["models"]["models"], "models")
    register_tortoise(
        app,
        config=ORM_CONFIG,
        generate_schemas=False,
        add_exception_handlers=False,
    )
