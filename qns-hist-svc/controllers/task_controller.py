from celery import Celery

from utils.logger import log
from utils.utils import get_envvar


def setup_celery():  # pragma: no cover
    log.info("Setting up Celery")
    cel = Celery(
        "cel",
        broker=get_envvar("REDIS_QUEUE_URL"),
        result=get_envvar("REDIS_QUEUE_URL"),
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        enable_utc=True,
        include=["service.feedback_ai_svc"],
        task_reject_on_worker_lost=True,
    )
    return cel


cel = setup_celery()
