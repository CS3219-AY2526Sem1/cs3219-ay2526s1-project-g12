import redis.asyncio as aioredis
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth_router import router as auth_router
from routes.dynamic_router import router as dynamic_router
from routes.registry_router import router as registry_router
from service.redis_settings import get_redis, lifespan
from utils.utils import get_envvar

FRONT_END_URL =get_envvar("FRONT_END_URL")
app = FastAPI(title="API Gateway", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(registry_router)
app.include_router(dynamic_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONT_END_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Redis Debugging Endpoints (TODO remove in production) ---
@app.get("/print-all")
async def print_all_from_redis_aioredis(r: aioredis = Depends(get_redis)):
    """
    Retrieves all keys and their corresponding values from Redis using aioredis
    and returns them. Also prints them to the server console.
    """
    result = {}

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
async def flush_all_redis(r: aioredis = Depends(get_redis)):
    """
    Delete all keys from all Redis databases.
    WARNING: This operation is irreversible and will delete ALL data!
    """
    try:
        await r.flushall()
        return {"message": "All Redis databases have been flushed successfully"}
    except Exception as e:
        return {"error": f"Failed to flush Redis: {str(e)}"}
