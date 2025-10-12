import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import httpx
import redis.asyncio as aioredis
from fastapi import HTTPException, status

from utils.logger import log

DEFAULT_COOKIE_MAX_AGE = os.getenv("DEFAULT_COOKIE_MAX_AGE")


class GatewayController:
    def __init__(
        self,
        redis: aioredis.Redis,
        user_service_url: str,
        token_ttl_seconds: int = DEFAULT_COOKIE_MAX_AGE,
    ):
        self.redis = redis
        self.user_service_url = user_service_url.rstrip("/")
        self.ttl = token_ttl_seconds

    async def _find_existing_token_key(self, user_id: str) -> str | None:
        """
        Scans for an existing access token key associated with a user ID.

        Args:
            redis: The asynchronous Redis connection instance.
            user_id: The ID of the user to search for.

        Returns:
            The Redis key of the existing token if found, otherwise None.
        """
        # Iterate through keys matching the 'token:*' pattern
        async for key in self.redis.scan_iter("token:*"):
            # Check the 'userID' field in the hash stored at the key
            stored_user_id = await self.redis.hget(key, "userID")
            log.info(f"Checking key {key} for userID {stored_user_id}")
            if stored_user_id == user_id:
                return key
        return None

    async def validate_token(self, token: str) -> Dict[str, Any]:
        log.info(f"Validating token: {token}")
        data = await self.redis.hgetall(f"token:{token}")
        if not data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        log.info(f"Token data from Redis: {data}")
        await self.redis.expire(f"token:{token}", self.ttl)  # extend expiration
        return data

    async def store_token(self, token: str, user_id: str):
        """
        Stores an access token in Redis. If the user already has a session,
        the old session is deleted before the new one is created.
        """
        # 1. Check for and delete any existing session for the user
        existing_key = await self._find_existing_token_key(user_id)
        if existing_key:
            log.info(
                f"User {user_id} already has an active session. Deleting old key: {existing_key}"
            )
            await self.revoke_token(existing_key)

        # 2. Proceed to store the new token
        redis_key = f"token:{token}"
        create_time = datetime.now(timezone.utc)
        expire_in_minutes = self.ttl / 60
        expiry_time = create_time + timedelta(minutes=expire_in_minutes)

        token_data = {
            "userID": user_id,
            "create_time": create_time.isoformat(),
            "expiry_time": expiry_time.isoformat(),
        }

        # Use a Redis pipeline for atomic execution
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.hset(redis_key, mapping=token_data)
            await pipe.expire(
                redis_key, int(timedelta(minutes=expire_in_minutes).total_seconds())
            )
            await pipe.execute()

        log.info(f"Stored new session for user {user_id} with key: {redis_key}")

    async def revoke_token(self, token: str) -> bool:
        return bool(await self.redis.delete(token))

    async def forward(
        self,
        method: str,
        path: str,
        *,
        headers: Dict[str, str] | None = None,
        params: Dict[str, Any] | None = None,
        data: Any = None,
    ) -> tuple[int, Any]:
        log.info(f"Forwarding {method} request to {self.user_service_url}{path}")
        url = f"{self.user_service_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.request(
                    method, url, headers=headers or {}, params=params or {}, data=data
                )
                try:
                    body = r.json()
                except Exception:
                    body = r.text
                return r.status_code, body
        except httpx.TimeoutException:
            return 504, {"detail": "Gateway timeout"}
        except httpx.RequestError as e:
            log.error(f"Forwarding error: {e}")
            return 502, {"detail": "Bad gateway"}
