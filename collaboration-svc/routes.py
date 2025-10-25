from contextlib import asynccontextmanager
from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)
from fastapi import FastAPI
from utils.logger import log

ADMIN_ROLE = "admin"
USER_ROLE = "user"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the collaboration service.
    """
    register_self_as_service(app)
    hc_task = register_heartbeat()
    yield
    # This is the shut down procedure when the matching service stops.
    log.info("Collaboration service shutting down.")
    hc_task.cancel()

