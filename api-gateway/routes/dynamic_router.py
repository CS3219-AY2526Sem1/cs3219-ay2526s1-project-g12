"""Catch‑all routing for dynamic microservices registered in the service
registry.

Any request that does not match an existing static route will be
forwarded to the appropriate microservice based on the ServiceRegistry.
This router must be included after all other routers so that specific
routes defined elsewhere take precedence.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from controllers.gateway_controller import GatewayController
from service.cookie_management import extend_access_token_cookie
from service.redis_settings import get_gateway

router = APIRouter(include_in_schema=False)


async def auth_user(
    access_token: str = Depends(extend_access_token_cookie),
    gateway: GatewayController = Depends(get_gateway),
) -> dict:
    """Validates and extends the TTL of the access token if present.
    Returns user data if valid, or an empty dict if unauthenticated.
    """
    if not access_token:
        return {}

    return await gateway.validate_token(access_token)


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def dynamic_forward(
    path: str,
    request: Request,
    user_data: dict = Depends(auth_user),
    gateway: GatewayController = Depends(get_gateway),
):
    """Forward any unmatched request to the appropriate service. The
    path is combined with a leading slash and passed to the
    GatewayController for resolution.  If the registry
    cannot resolve the path to a service, a 404 error is returned.
    """
    method = request.method
    headers = dict(request.headers)
    params = dict(request.query_params)
    body = await request.body()

    code, data = await gateway.forward(
        method,
        "/" + path,
        headers=headers,
        params=params,
        data=body,
        user_data=user_data,
    )
    if not (200 <= code < 300):
        raise HTTPException(status_code=code, detail=data)
    return JSONResponse(content=data, status_code=code)
