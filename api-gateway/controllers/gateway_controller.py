from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import httpx
import redis.asyncio as aioredis
from fastapi import HTTPException

from models.api_models import RoutePayload
from service.registry import ServiceRegistry
from utils.logger import log
from utils.utils import get_envvar

DEFAULT_COOKIE_MAX_AGE = get_envvar("DEFAULT_COOKIE_MAX_AGE")


class GatewayController:
    """API Gateway controller for managing user sessions and routing requests based
    on the service registry"""

    def __init__(
        self,
        redis: aioredis.Redis,
        token_ttl_seconds: int = int(DEFAULT_COOKIE_MAX_AGE),
        heartbeat_ttl: int = 30,
        rr_ttl: int = 3600,
    ):
        self.redis = redis
        self.ttl = token_ttl_seconds
        self.registry = ServiceRegistry(
            redis, heartbeat_ttl=heartbeat_ttl, rr_ttl=rr_ttl
        )

    async def _find_existing_token_key(self, user_id: str) -> str | None:
        """Scans for an existing access token key associated with a user ID.

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
        """Validates a token atomically, extends TTL in redis and returns
        the associated user data.
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
            _, _, _, user_data = await pipe.execute()

        log.info(f"Token validation successful for user: {user_id}")

        return user_data

    async def store_token(self, resp: Dict[str, Any]):
        """Stores an access token in Redis. If the user already has a session,
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
        del resp["access_token"], resp["role"]  # Remove token & role from user data
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
        """Logs out a user by completely removing their session from all three Redis tables.

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

    async def register_service(
        self,
        service_name: str,
        instance_id: str,
        address: str,
        routes: Iterable[RoutePayload],
    ) -> None:
        """Register a service instance and its routes in the service registry."""
        await self.registry.register_service(
            service_name=service_name,
            instance_id=instance_id,
            address=address,
            routes=routes,
        )

    async def forward(
        self,
        method: str,
        path: str,
        *,
        headers: Dict[str, str] | None = None,
        params: Dict[str, Any] | None = None,
        data: Any = None,
        user_data: Dict[str, Any],
    ) -> tuple[int, Any]:
        """Forwards a request to the appropriate service based on the registry.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Full request path including gateway prefix
            headers: Request headers to forward
            params: Optional query parameters
            data: Optional request body
            user_data: Data of the authenticated user making the request
        """
        method = method.upper()
        user_id = user_data.get("user_id")
        role = user_data.get("role")

        # Find the service responsible for this path
        matched_route = await self.registry.find_route(path)
        if not matched_route:
            log.warning(
                f"Blocked forwarding of request to '{path}': no service found for path"
            )
            return 404, {"detail": "Not Found"}

        service_name, canonical_path = matched_route

        internal_path = path.removeprefix(f"/{service_name}")

        # Fetch the route definition
        route_def = await self.registry.get_route_definition(
            service_name, canonical_path
        )
        if not route_def:
            log.warning(
                f"Blocked forwarding of request to '{internal_path}' for service {service_name}: "
                f"no route definition found"
            )
            return 404, {"detail": "Not found"}

        # Check method
        if method not in route_def.methods:
            log.warning(
                f"Blocked forwarding of {method} request to '{internal_path}': method not allowed"
            )
            return 405, {"detail": "Method not allowed"}

        # Check role
        if route_def.methods[method] and (
            not role or role not in route_def.methods[method]
        ):
            log.warning(
                f"Blocked forwarding of request to '{internal_path}': role {role} not permitted"
            )
            return 401, {"detail": "Unauthorized"}

        # Choose instance
        address = await self.registry.choose_instance(service_name)
        if not address:
            log.error(
                f"Blocked forwarding of request to '{internal_path}': "
                f"no alive instances found for service {service_name}"
            )
            return 503, {"detail": "Service unavailable"}

        url = f"{address}{internal_path}"

        log.info(f"Forwarding request: {method} {path} → [{service_name}] {url}")

        # Check if there is an existing header dictionary
        if headers is None:
            headers = {}

        # Insert user info into headers
        if user_id:
            headers["X-User-ID"] = str(user_id)
        if role:
            headers["X-User-Role"] = str(role)

        try:
            async with httpx.AsyncClient(timeout=190.0) as client:
                r = await client.request(
                    method, url, headers=headers, params=params or {}, data=data
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
