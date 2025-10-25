from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)
from service.database_svc import register_database


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    register_self_as_service(app)
    hc_task = register_heartbeat()

    yield

    hc_task.cancel()


app = FastAPI(
    title="PeerPrep Question Service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_database(app)

ADMIN_ROLE = "admin"
USER_ROLE = "user"


@app.get("/")
async def root():
    return {"status": "working"}
