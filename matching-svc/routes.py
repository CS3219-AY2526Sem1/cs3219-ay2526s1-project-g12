from contextlib import asynccontextmanager
from controllers.matching_controller import (
    find_match,
    check_redis_connection,
    confirm_match,
    terminate_match,
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.api_models import MatchRequest, MatchConfirmRequest
from service.redis_confirmation_service import connect_to_redis_confirmation_service
from service.redis_message_service import connect_to_redis_message_service
from service.redis_matchmaking_service import connect_to_redis_matchmaking_service
from utils.logger import log
from utils.utils import sever_connection, get_envvar

from controllers.heartbeat_controller import (
    register_heartbeat,
    register_self_as_service,
)

HOST_URL = get_envvar("HOST_URL")
FRONT_END_URL = get_envvar("FRONT_END_URL")
ENVIROMENT = get_envvar("ENVIROMENT")

ADMIN_ROLE = "admin"
USER_ROLE = "user"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Set up variables for the matching service.
    """
    app.state.redis_matchmaking_service = connect_to_redis_matchmaking_service()
    app.state.redis_message_service = connect_to_redis_message_service()
    app.state.redis_confirmation_service = connect_to_redis_confirmation_service()
    log.info("Matching service is Up.")
    register_self_as_service(app)
    hc_task = register_heartbeat()
    yield
    # This is the shut down procedure when the matching service stops.
    log.info("Matching service shutting down.")
    await sever_connection(app.state.redis_matchmaking_service)
    await sever_connection(app.state.redis_message_service)
    await sever_connection(app.state.redis_confirmation_service)
    hc_task.cancel()


app = FastAPI(title="PeerPrep Matching Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_END_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "success"}


@app.get("/check_connection/queue", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def check_queue_connection():
    return check_redis_connection(app.state.redis_queue)


@app.get(
    "/check_connection/message_queue",
    openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]},
)
async def check_message_connection():
    return check_redis_connection(app.state.redis_message_queue)


@app.post("/find_match", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def match(match_request: MatchRequest):
    return await find_match(
        match_request,
        app.state.redis_matchmaking_service,
        app.state.redis_message_service,
        app.state.redis_confirmation_service,
    )


@app.delete("/terminate_match", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]})
async def terminate(cancel_request: MatchRequest):
    return await terminate_match(
        cancel_request,
        app.state.redis_matchmaking_service,
        app.state.redis_message_service,
    )


@app.post(
    "/confirm_match/{match_id}", openapi_extra={"x-roles": [ADMIN_ROLE, USER_ROLE]}
)
async def confirm_user_match(match_id: str, confirm_request: MatchConfirmRequest):
    return await confirm_match(
        match_id,
        confirm_request,
        app.state.redis_matchmaking_service,
        app.state.redis_message_service,
        app.state.redis_confirmation_service,
    )

if ENVIROMENT =="DEV":
    # --- Redis Debugging Endpoints
    @app.get("/print-all")
    async def print_all_from_redis_aioredis():
        """
        Retrieves all keys and their corresponding values from Redis using aioredis
        and returns them. Also prints them to the server console.
        """
        result = {}
        # try:
        #     await app.state.redis_message_queue.ping()
        #     log.info("Redis q connection successful.")
        # except Exception as e:
        #     log.info(f"Redis q connection error: {e}")
        try:
            await app.state.redis_message_service.ping()
            log.info("Redis m connection successful.")
        except Exception as e:
            log.info(f"Redis m connection error: {e}")
        try:
            await app.state.redis_confirmation_service.ping()
            log.info("Redis c connection successful.")
        except Exception as e:
            log.info(f"Redis c connection error: {e}")

        r = app.state.redis_message_service

        async for key in r.scan_iter("*"):
            try:
                # Check the type of the key first
                key_type = await r.type(key)
                print(f"Key:, Type: {key_type}")
                if key_type == "string":
                    value = await r.get(key)
                elif key_type == "hash":
                    value = await r.hgetall(key)
                else:
                    value = f"<{key_type} type>"

                # print(f"{key} ({key_type}) => {value}")
                result[key] = value

            except Exception as e:
                print(f"Error processing key {key}: {e}")
                result[key] = f"<error: {str(e)}>"

        return result


    @app.delete("/flush-all")
    async def flush_all_redis():
        """
        Delete all keys from all Redis databases.
        WARNING: This operation is irreversible and will delete ALL data!
        """
        try:
            await app.state.redis_message_service.flushall()
            return {"message": "All Redis databases have been flushed successfully"}
        except Exception as e:
            return {"error": f"Failed to flush Redis: {str(e)}"}
