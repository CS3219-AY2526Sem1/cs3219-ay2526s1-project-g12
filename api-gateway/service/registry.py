"""Service registry module for the API gateway.

This module provides a lightweight Redis‑backed service discovery and
route registry for the API gateway. Each microservice instance
registers its available routes and capabilities on startup and
periodically renews a heartbeat key so the gateway can tell which
instances are alive. The gateway in turn consults this registry when
handling incoming requests to determine which service should receive
the call, whether the HTTP method is permitted, and what roles may
access a given endpoint.

Key naming conventions
----------------------

All keys used by the registry are prefixed with ``gw:`` to avoid
collisions with other data stored in Redis. The following keys are
used:

* ``gw:routes:map`` – a hash where each field is a route path and the
  corresponding value is the name of the service that owns the route.
  This enables a quick lookup to discover which service should handle
  a given path.
* ``gw:service:<service_name>:routes`` – a hash containing the
  definition of each route exposed by ``<service_name>``. Each field
  in this hash is a route path (e.g. ``/users/me``) and the value is
  a JSON string describing the allowed HTTP methods and roles for
  that route.
* ``gw:service:<service_name>:instances`` – a hash of live instances
  for the service.  The field name is an instance identifier, and the
  value is a JSON string containing any metadata about the instance.
* ``gw:service:<service_name>:instance:<instance_id>:heartbeat`` – a
  simple key (string) with a TTL.  The presence of this key indicates
  that the corresponding instance is healthy; services should renew
  this key on a periodic basis.  When the TTL expires, the registry
  considers the instance dead.
"""

from __future__ import annotations

import json
import re
from typing import Iterable, List, Optional, Tuple

import redis.asyncio as aioredis

from models.api_models import RoutePayload
from models.registry_models import RouteDefinition


class ServiceRegistry:
    """Redis‑backed registry for microservice routes and instances."""

    # Key templates
    ROUTE_MAP_KEY = "gw:routes:map"
    SERVICE_ROUTES_KEY = "gw:service:{service_name}:routes"
    SERVICE_INSTANCES_KEY = "gw:service:{service_name}:instances"
    HEARTBEAT_KEY = "gw:service:{service_name}:instance:{instance_id}:heartbeat"

    def __init__(self, redis: aioredis.Redis, heartbeat_ttl: int = 30) -> None:
        """Initialize the registry.

        Args:
            redis: The aioredis client instance used for storage.
            heartbeat_ttl: Expiration time (in seconds) for heartbeat keys.
                Each service instance must refresh its heartbeat before
                the TTL expires to remain registered as healthy.
        """
        self.redis = redis
        self.heartbeat_ttl = heartbeat_ttl

    async def register_service(
        self,
        service_name: str,
        instance_id: str,
        address: str,
        routes: Iterable[RoutePayload],
    ) -> None:
        """Register a service instance and its routes in Redis.

        This stores the instance information, route definitions, and
        updates the global route map. If a route already exists for
        the service, it will be overwritten with the new definition.

        Args:
            service_name: Unique name of the microservice.
            instance_id: Identifier for this specific instance
            address: Host:port of the instance, used by the gateway
                when forwarding requests.
            routes: An iterable of RouteDefinition objects describing
                each exposed route.
        """
        # Store instance metadata
        inst_key = self.SERVICE_INSTANCES_KEY.format(service_name=service_name)
        await self.redis.hset(inst_key, instance_id, json.dumps({"address": address}))

        # Write or refresh heartbeat key
        hb_key = self.HEARTBEAT_KEY.format(
            service_name=service_name, instance_id=instance_id
        )
        await self.redis.set(hb_key, "1", ex=self.heartbeat_ttl)

        # Store each route in the service routes hash and global map
        svc_routes_key = self.SERVICE_ROUTES_KEY.format(service_name=service_name)
        async with self.redis.pipeline(transaction=True) as pipe:
            for rd in routes:
                await pipe.hset(svc_routes_key, rd.path, rd.model_dump_json())
                await pipe.hset(self.ROUTE_MAP_KEY, rd.path, service_name)
                if rd.path[-1] == "/":
                    await pipe.hset(
                        svc_routes_key, rd.path.rstrip("/"), rd.model_dump_json()
                    )
                    await pipe.hset(
                        self.ROUTE_MAP_KEY, rd.path.rstrip("/"), service_name
                    )
                else:
                    await pipe.hset(svc_routes_key, f"{rd.path}/", rd.model_dump_json())
                    await pipe.hset(self.ROUTE_MAP_KEY, f"{rd.path}/", service_name)
            await pipe.execute()

    async def unregister_service(self, service_name: str, instance_id: str) -> None:
        """Remove a service instance from the registry.

        Deletes the instance entry and its heartbeat key. Route
        definitions remain until explicitly removed.
        """
        inst_key = self.SERVICE_INSTANCES_KEY.format(service_name=service_name)
        await self.redis.hdel(inst_key, instance_id)
        hb_key = self.HEARTBEAT_KEY.format(
            service_name=service_name, instance_id=instance_id
        )
        await self.redis.delete(hb_key)

    async def refresh_heartbeat(self, service_name: str, instance_id: str) -> None:
        """Refresh the heartbeat for a service instance."""
        hb_key = self.HEARTBEAT_KEY.format(
            service_name=service_name, instance_id=instance_id
        )
        await self.redis.set(hb_key, "1", ex=self.heartbeat_ttl)

    async def find_route(self, path: str) -> Optional[Tuple[str, str]]:
        """Resolve which service owns the given request path and the
        canonical route pattern that matches it.

        This method first performs an exact lookup in the route map. If
        no exact match is found, it iterates over all registered route
        patterns and attempts to match the provided path against each
        pattern by replacing any ``{param}`` segments with a wildcard
        that matches a single path element. The first matching pattern
        is returned.

        Args:
            path: The actual request path (e.g. "/questions/123").
        Returns:
            A tuple of (service_name, route_pattern) if a match is found,
            otherwise ``None``.
        """
        # Try exact match first
        service_name = await self.redis.hget(self.ROUTE_MAP_KEY, path)
        if service_name:
            return service_name, path
        # Otherwise perform a parameterised match
        routes = await self.redis.hgetall(self.ROUTE_MAP_KEY)
        for route_pattern, svc in routes.items():
            pattern_regex = re.sub(r"\{[^/{}]+\}", "[^/]+", route_pattern)
            pattern_regex = f"^{pattern_regex}$"
            if re.fullmatch(pattern_regex, path):
                return svc, route_pattern
        return None

    async def get_route_definition(
        self, service_name: str, path: str
    ) -> Optional[RouteDefinition]:
        """Retrieve the RouteDefinition for the given path within a service.

        Args:
            service_name: Name of the service that owns the route.
            path: Exact path pattern of the route.
        Returns:
            A RouteDefinition instance if found, else None.
        """
        svc_routes_key = self.SERVICE_ROUTES_KEY.format(service_name=service_name)
        data = await self.redis.hget(svc_routes_key, path)
        if data is None:
            return None
        return RouteDefinition.from_json(data)

    async def list_instances(self, service_name: str) -> List[str]:
        """Return a list of alive instance addresses for a service."""
        inst_key = self.SERVICE_INSTANCES_KEY.format(service_name=service_name)
        instances = await self.redis.hgetall(inst_key)
        alive: List[str] = []
        for instance_id, meta_json in instances.items():
            hb_key = self.HEARTBEAT_KEY.format(
                service_name=service_name, instance_id=instance_id
            )
            # Check heartbeat existence
            if await self.redis.exists(hb_key):
                try:
                    meta = json.loads(meta_json)
                    alive.append(meta.get("address"))
                except Exception:
                    continue
        return alive

    async def choose_instance(self, service_name: str) -> Optional[str]:
        """Choose one alive instance to handle a request."""
        # TODO : Implement better load balancing strategy
        instances = await self.list_instances(service_name)
        return instances[0] if instances else None
