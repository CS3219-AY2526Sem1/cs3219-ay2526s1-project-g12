from fastapi import APIRouter, Depends, HTTPException

from controllers.gateway_controller import GatewayController
from models.api_models import (
    RegisterOpenApiPayload,
    RegisterServicePayload,
    ServiceInstancePayload,
    RoutePayload,
)
from service.redis_settings import get_gateway

router = APIRouter(prefix="/registry", tags=["registry"])


@router.post("/register")
async def register_service(
    payload: RegisterServicePayload,
    gateway: GatewayController = Depends(get_gateway),
):
    """Register a service instance and its routes.

    Services should call this endpoint on startup to publish their
    available routes. If the service is already registered, new route
    definitions will override the previous ones.
    """
    try:
        await gateway.register_service(
            service_name=payload.service_name,
            instance_id=payload.instance_id,
            address=payload.address,
            routes=payload.routes,
        )
        return {"detail": "Service registered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register-openapi")
async def register_openapi(
    payload: RegisterOpenApiPayload,
    gateway: GatewayController = Depends(get_gateway),
):
    """Register a service instance by parsing its OpenAPI specification.

    Services can call this endpoint and supply their OpenAPI JSON in
    ``payload.openapi``. The gateway will extract all paths and
    associated HTTP methods from the specification and register them.
    Role information is inferred from an ``x-roles`` extension.
    """
    try:
        address = payload.openapi["servers"][0]["url"]
        paths = payload.openapi.get("paths", {})
        route_defs = []
        # Iterate over each path and collect methods and roles
        for path, operations in paths.items():
            # Exclude standard documentation endpoints
            if path in {"/openapi.json", "/docs", "/redoc"}:
                continue
            methods: dict[str, list[str]] = dict()
            for method_name, op_spec in operations.items():
                roles = []
                # Attempt to read custom roles from extensions
                ext_roles = op_spec.get("x-roles")
                if ext_roles:
                    for r in ext_roles:
                        roles.append(r)
                methods[method_name.upper()] = roles
            if not methods:
                continue
            route_defs.append(RoutePayload(path=path, methods=methods))
        await gateway.register_service(
            service_name=payload.service_name,
            instance_id=payload.instance_id,
            address=address,
            routes=route_defs,
        )
        return {"detail": "Service registered from OpenAPI"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heartbeat")
async def heartbeat(
    payload: ServiceInstancePayload,
    gateway: GatewayController = Depends(get_gateway),
):
    """Renew the heartbeat for a service instance.  Instances should
    call this periodically to keep themselves marked as alive. If a
    heartbeat expires, the instance will no longer be considered
    when routing requests.
    """
    try:
        await gateway.registry.refresh_heartbeat(payload.service_name, payload.instance_id)
        return {"detail": "Heartbeat refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deregister")
async def deregister(
    payload: ServiceInstancePayload,
    gateway: GatewayController = Depends(get_gateway),
):
    """Deregister a service instance. Instances should call this on
    graceful shutdown to remove themselves from the registry.
    """
    try:
        await gateway.registry.unregister_service(payload.service_name, payload.instance_id)
        return {"detail": "Service deregistered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
