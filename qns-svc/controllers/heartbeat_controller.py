import asyncio
from uuid import uuid4

import requests
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from requests.exceptions import RequestException

from utils.logger import log
from utils.utils import get_envvar

SERVICE_NAME = "qns-svc"
INSTANCE_ID = str(uuid4())


def register_self_as_service(app: FastAPI):
    log.info(f"Registering service with {SERVICE_NAME} {INSTANCE_ID}")
    openapi_schema = get_openapi(
        title="Question Service API",
        version="1.0.0",
        routes=app.routes,
    )

    log.debug(openapi_schema)

    json_payload = {
        "service_name": SERVICE_NAME,
        "instance_id": INSTANCE_ID,
        "address": get_envvar("HOST_URL"),
        "openapi": openapi_schema,
    }

    try:
        requests.post(
            f"{get_envvar('APIGATEWAY_URL')}{get_envvar('REGISTRY_PATH')}",
            json=json_payload,
        )
    except RequestException as e:
        log.debug(e)
        log.warning("Could not register on API Gateway")


def _send_healthcheck():
    log.info("Sending Healthcheck now")
    json_payload = {"service_name": SERVICE_NAME, "instance_id": INSTANCE_ID}
    try:
        requests.post(
            f"{get_envvar('APIGATEWAY_URL')}{get_envvar('HEARTBEAT_PATH')}",
            json=json_payload,
        )
    except RequestException as e:
        log.debug(e)
        log.warning("Could not register on API Gateway")


async def _periodic_healtcheck():  # pragma: no cover
    while True:
        _send_healthcheck()
        await asyncio.sleep(int(get_envvar("HEARTBEAT_PERIOD")))


def register_heartbeat():  # pragma: no cover
    log.info("Registering heartbeat")
    loop = asyncio.get_event_loop()
    return loop.create_task(_periodic_healtcheck())
