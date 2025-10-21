import os
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
import redis.asyncio as aioredis
from fastapi import HTTPException

from utils.logger import log

DEFAULT_COOKIE_MAX_AGE = os.getenv("DEFAULT_COOKIE_MAX_AGE")


class GatewayController:
    def __init__(
        self,
        redis: aioredis.Redis,
        user_service_url: str,
        token_ttl_seconds: int = int(DEFAULT_COOKIE_MAX_AGE),
    ):
        self.redis = redis
        self.user_service_url = user_service_url.rstrip("/")
        self.ttl = token_ttl_seconds

    async def _find_existing_token_key(self, user_id: str) -> str | None:
        """
        Scans for an existing access token key associated with a user ID.

        Args:
            user_id: The ID of the user to search for.

        Returns:
            The Redis key of the existing token if found, otherwise None.
        """
        # Iterate through keys matching the 'token:*' pattern
        token = await self.redis.get(f"user:{user_id}")
        if token:
            return token

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validates a token atomically, extends TTL in redis and returns the associated user data.
        """
        log.info(f"Validating token: {token}")

        # Get userID from token
        user_id = await self.redis.get(f"token:{token}")
        if not user_id:
            log.warning(f"Token not found: {token}")
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )

        # Atomically extend expiration for all three keys
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.expire(f"token:{token}", self.ttl)
            await pipe.expire(f"user:{user_id}", self.ttl)
            await pipe.expire(f"userdata:{user_id}", self.ttl)
            await pipe.hgetall(f"userdata:{user_id}")
            _,_,_,user_data=await pipe.execute()

        log.info(f"Token validation successful for user: {user_id}")
        

        return user_data

    async def store_token(self, resp: Dict[str, Any]):
        """
        Stores an access token in Redis. If the user already has a session,
        the old session is deleted before the new one is created.
        """
        # Expect user service to return a token and user info
        token = resp.get("access_token")

        user_id = str(resp.get("user_id"))
        # 1. Check for and delete any existing session for the user
        existing_key = await self._find_existing_token_key(user_id)
        if existing_key:
            log.info(
                f"{user_id} has an active session. Logging out from old session: {existing_key}"
            )
            await self.logout_user(existing_key)

        # 2. Proceed to store the new token
        redis_key = f"token:{token}"

        role = resp.get("role").get("role")
        del resp["access_token"],resp["role"]  # Remove token & role from user data
        resp["role"] = role
        user_data = resp  # Remaining user data to store
        user_data["create_time"] = datetime.now(timezone.utc).isoformat()

        # Use a Redis pipeline for atomic execution
        async with self.redis.pipeline(transaction=True) as pipe:
            # Table 1: user:{userID} -> token
            await pipe.set(f"user:{user_id}", token, ex=self.ttl)

            # Table 2: token:{token} -> userID
            await pipe.set(f"token:{token}", user_id, ex=self.ttl)

            # Table 3: userdata:{userID} -> user data hash
            await pipe.hset(f"userdata:{user_id}", mapping=user_data)
            await pipe.expire(f"userdata:{user_id}", self.ttl)

            await pipe.execute()

        log.info(f"Stored new session for user {user_id} with key: {redis_key}")
        return token

    async def logout_user(self, token: str) -> Dict[str, Any]:
        """
        Logs out a user by completely removing their session from all three Redis tables.

        Args:
            token: The authentication token to logout
        Raises:
            HTTPException: If token is invalid or already expired
        """
        log.info(f"Processing logout for token: {token}")

        # Step 1: Get user ID from token table
        user_id = await self.redis.get(f"token:{token}")
        log.info(f"Processing logout: {user_id}")
        if not user_id:
            log.error(f"Logout attempted with invalid token: {token}")
            raise HTTPException(
                status_code=401, detail="Invalid or already expired token"
            )

        # Step 3: Delete from all three tables atomically
        async with self.redis.pipeline(transaction=True) as pipe:
            # Delete from Table 1: user:{userID} -> token
            await pipe.delete(f"user:{user_id}")

            # Delete from Table 2: token:{token} -> userID
            await pipe.delete(f"token:{token}")

            # Delete from Table 3: userdata:{userID} -> user data
            await pipe.delete(f"userdata:{user_id}")

            # Execute all deletions
            await pipe.execute()

        log.info(f"Successfully logged out user {user_id} ")

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
