from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Cookie, Depends, FastAPI, HTTPException

from controllers.gateway_controller import GatewayController
from utils.logger import log
from utils.utils import get_envvar

# Environment
USER_SERVICE_URL = get_envvar("USER_SERVICE_URL")
REDIS_URL = get_envvar("REDIS_URL")
TOKEN_EXPIRE_HOURS = int(get_envvar("TOKEN_EXPIRE_HOURS"))
TOKEN_EXPIRE_SECONDS = int(
    get_envvar("TOKEN_EXPIRE_SECONDS", TOKEN_EXPIRE_HOURS * 3600)
)

# Singletons bound during app lifespan
_redis: aioredis.Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _redis
    _redis = await aioredis.from_url(
        f"{REDIS_URL}",
        decode_responses=True,
        encoding="utf-8",
        health_check_interval=5,
    )
    await _redis.ping()
    log.info("Connected to Redis")
    yield
    if _redis:
        await _redis.close()
        log.info("Redis connection closed")


async def get_redis() -> aioredis.Redis:
    assert _redis is not None, "Redis not initialized"
    return _redis


async def get_gateway(
    redis: aioredis.Redis = Depends(get_redis),
) -> GatewayController:
    return GatewayController(
        redis=redis,
        user_service_url=USER_SERVICE_URL,
        token_ttl_seconds=TOKEN_EXPIRE_SECONDS,
    )


async def get_token_from_cookie(access_token: Optional[str] = Cookie(None)) -> str:
    """
    Dependency to extract the access token from the browser cookie.
    Raises a 401 error if the cookie is not found.
    """
    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated: Access token cookie not found.",
        )
    return access_token
