import asyncio
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
MAILTRAP_HOST = "live.smtp.mailtrap.io"
MAILTRAP_SMTP_PORTS = [25, 465, 587]  # Common SMTP ports


@app.get("/ping-mailtrap-tcp")
async def ping_mailtrap_tcp():
    """
    Attempts to establish a TCP connection to Mailtrap's SMTP server
    on common ports to check its liveness.
    """
    results = {}
    for port in MAILTRAP_SMTP_PORTS:
        try:
            reader, writer = await asyncio.open_connection(MAILTRAP_HOST, port)
            writer.close()
            await writer.wait_closed()
            results[port] = {
                "status": "success",
                "message": f"TCP connection to {MAILTRAP_HOST}:{port} successful.",
            }
        except ConnectionRefusedError:
            results[port] = {
                "status": "failed",
                "message": f"Connection to {MAILTRAP_HOST}:{port} refused.",
            }
        except OSError as e:
            results[port] = {
                "status": "failed",
                "message": f"OS error connecting to {MAILTRAP_HOST}:{port}: {e}",
            }
        except Exception as e:
            results[port] = {
                "status": "error",
                "message": f"An unexpected error occurred connecting to {MAILTRAP_HOST}:{port}: {e}",
            }

    # Determine overall status
    if any(res["status"] == "success" for res in results.values()):
        overall_status = "live"
    else:
        overall_status = "down or unreachable"

    return {
        "host": MAILTRAP_HOST,
        "overall_status": overall_status,
        "port_checks": results,
    }


app.include_router(auth_router)
app.include_router(user_router)
