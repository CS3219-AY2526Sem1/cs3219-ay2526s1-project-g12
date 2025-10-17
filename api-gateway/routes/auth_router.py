import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from controllers.gateway_controller import GatewayController
from service.settings import get_gateway, get_token_from_cookie
from utils.logger import log

DEFAULT_COOKIE_MAX_AGE = os.getenv("DEFAULT_COOKIE_MAX_AGE")
router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


@router.post("/login")
async def login(
    body: dict,
    response: Response,
    gateway: GatewayController = Depends(get_gateway),
):
    username = body.get("username")
    log.info(f"Login attempt for user={username}")

    # Forward to user-service /auth/login
    status_code, resp = await gateway.forward("POST", "/auth/login", data=body)
    if not (200 <= status_code < 300):
        raise HTTPException(
            status_code=status_code,
            detail=resp,
        )

    if not resp:
        raise HTTPException(
            status_code=502, detail="User service did not return a respesponse"
        )
    
    token = await gateway.store_token(resp)
    log.info(f"Login succeeded for user={username}")

    # --- Set the access token in an HttpOnly cookie ---
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=False,  # Set to True in production (requires HTTPS)
        samesite="lax",  # Or "strict" for better CSRF protection
        expires=int(DEFAULT_COOKIE_MAX_AGE),  # Expiry in seconds
    )

    return {
        "access_token": token,
    }


@router.post("/logout")
async def logout(
    response: Response,
    token: str = Depends(get_token_from_cookie),
    gateway: GatewayController = Depends(get_gateway),
):
    await gateway.logout_user(token)
    log.info("Logout succeeded")

    response.delete_cookie(key="access_token")


# Wildcard proxy for any other /auth/* route
@router.api_route(
    "/{path:path}",
    methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    ],
    include_in_schema=False,
)
async def forward_auth(
    path: str, request: Request, gateway: GatewayController = Depends(get_gateway)
):
    method = request.method
    headers = dict(request.headers)
    params = dict(request.query_params)
    body = None
    if method in {"POST", "PUT", "PATCH"}:
        body = await request.body()

    code, data = await gateway.forward(
        method, f"/auth/{path}", headers=headers, params=params, data=body
    )
    if not (200 <= code < 300):
        raise HTTPException(status_code=code, detail=data)
    return JSONResponse(content=data, status_code=code)
