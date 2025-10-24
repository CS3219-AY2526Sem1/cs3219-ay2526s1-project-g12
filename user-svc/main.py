from contextlib import asynccontextmanager

from fastapi import FastAPI

from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)
from routes.auth_router import router as auth_router
from routes.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    # On Startup
    register_self_as_service(app)
    hc_task = register_heartbeat()

    yield
    # On Shutdown
    hc_task.cancel()


app = FastAPI(title="PeerPrep User Service", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
