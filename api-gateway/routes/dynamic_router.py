"""Catch‑all routing for dynamic microservices registered in the service
registry.

Any request that does not match an existing static route will be
forwarded to the appropriate microservice based on the ServiceRegistry.
This router must be included after all other routers so that specific
routes defined elsewhere take precedence.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from controllers.gateway_controller import GatewayController
from service.cookie_management import extend_access_token_cookie
from service.redis_settings import get_gateway
from utils.logger import log

router = APIRouter(include_in_schema=False)



async def auth_user(
    access_token: str = Depends(extend_access_token_cookie),
    gateway: GatewayController = Depends(get_gateway),
) -> dict:
    """Validates and extends the TTL of the access token if present.
    Returns user data if valid, or an empty dict if unauthenticated.
    """

    if not access_token:
        log.info("[AUTH_USER] No access token provided, returning empty dict")
        return {}

    try:
        result = await gateway.validate_token(access_token)
        log.info(f"[AUTH_USER] Token validation successful: {result}")
        return result
    except Exception as e:
        log.error(
            f"[AUTH_USER] Token validation failed with error: {str(e)}", exc_info=True
        )
        raise


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
    request_id = uuid4()
    method = request.method
    log.info(
        f"{request_id} [DYNAMIC_FORWARD]  HOST: {request.client.host} Incoming request: {method} /{path}"
    )
    headers = dict(request.headers)
    log.debug(f"{request_id} [DYNAMIC_FORWARD] Headers: {headers}")

    params = dict(request.query_params)
    log.debug(f"{request_id} [DYNAMIC_FORWARD] Query params: {params}")

    body = await request.body()

    try:
        code, data = await gateway.forward(
            method, "/" + path, data=body, user_data=user_data,params=params
        )

    except Exception as e:
        log.error(
            f"{request_id} [DYNAMIC_FORWARD] Gateway forward failed: {str(e)}",
            exc_info=True,
        )
        raise

    if not (200 <= code < 300):
        log.warning(f"{request_id} [DYNAMIC_FORWARD] Non-success status code: {code}")
        if isinstance(data, dict) and "detail" in data:
            log.warning(
                f"{request_id} [DYNAMIC_FORWARD] Error detail: {data['detail']}"
            )
            if data["detail"]:
                data = data["detail"]
        raise HTTPException(status_code=code, detail=data)

    log.info(
        f"{request_id} [DYNAMIC_FORWARD] Returning successful response with status {code}"
    )
    return JSONResponse(content=data, status_code=code)
