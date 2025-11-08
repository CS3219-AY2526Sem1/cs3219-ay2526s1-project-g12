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

from utils.logger import log


async def auth_user(
    access_token: str = Depends(extend_access_token_cookie),
    gateway: GatewayController = Depends(get_gateway),
) -> dict:
    """Validates and extends the TTL of the access token if present.
    Returns user data if valid, or an empty dict if unauthenticated.
    """
    log.info("[AUTH_USER] Starting authentication")
    log.info(f"[AUTH_USER] Received access_token: {access_token[:20] if access_token else 'None'}...")
    
    if not access_token:
        log.info("[AUTH_USER] No access token provided, returning empty dict")
        return {}

    log.info("[AUTH_USER] Attempting to validate token")
    try:
        result = await gateway.validate_token(access_token)
        log.info(f"[AUTH_USER] Token validation successful: {result}")
        return result
    except Exception as e:
        log.error(f"[AUTH_USER] Token validation failed with error: {str(e)}", exc_info=True)
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
    method = request.method
    log.info(f"[DYNAMIC_FORWARD] Incoming request: {method} /{path}")
    log.info(f"[DYNAMIC_FORWARD] User data: {user_data}")
    
    headers = dict(request.headers)
    log.debug(f"[DYNAMIC_FORWARD] Headers: {headers}")
    
    params = dict(request.query_params)
    log.debug(f"[DYNAMIC_FORWARD] Query params: {params}")
    
    body = await request.body()
    log.debug(f"[DYNAMIC_FORWARD] Request body length: {len(body)} bytes")
    if body:
        try:
            log.debug(f"[DYNAMIC_FORWARD] Request body: {body[:200]}")
        except Exception as e:
            log.debug(f"[DYNAMIC_FORWARD] Could not log body: {str(e)}")

    log.info(f"[DYNAMIC_FORWARD] Forwarding to gateway: {method} /{path}")
    
    try:
        code, data = await gateway.forward(
            method,
            "/" + path,
            headers=headers,
            params=params,
            data=body,
            user_data=user_data,
        )
        log.info(f"[DYNAMIC_FORWARD] Gateway returned status code: {code}")
        log.debug(f"[DYNAMIC_FORWARD] Gateway response data: {data}")
        
    except Exception as e:
        log.error(f"[DYNAMIC_FORWARD] Gateway forward failed: {str(e)}", exc_info=True)
        raise

    if not (200 <= code < 300):
        log.warning(f"[DYNAMIC_FORWARD] Non-success status code: {code}")
        if isinstance(data, dict) and "detail" in data:
            log.warning(f"[DYNAMIC_FORWARD] Error detail: {data['detail']}")
            if data["detail"]:
                data = data["detail"]
        raise HTTPException(status_code=code, detail=data)
    
    log.info(f"[DYNAMIC_FORWARD] Returning successful response with status {code}")
    return JSONResponse(content=data, status_code=code)
