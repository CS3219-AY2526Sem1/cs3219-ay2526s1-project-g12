import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response
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
    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail=resp,
        )

    # Expect user service to return a token and user info
    token = resp.get("access_token")
    if not token:
        raise HTTPException(
            status_code=502, detail="User service did not return a token"
        )
    user_id = str(resp.get("user_id"))
    log.info(f"Received token for user={user_id}")

    await gateway.store_token(
        token,
        user_id,
    )
    log.info(f"Login succeeded for user={user_id}")

    # --- Set the access token in an HttpOnly cookie ---
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=False,  # Set to True in production (requires HTTPS)
        samesite="lax",  # Or "strict" for better CSRF protection
        expires=DEFAULT_COOKIE_MAX_AGE,  # Expiry in seconds
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
    }


@router.get("/logout")
async def logout(
    response: Response,
    token: str = Depends(get_token_from_cookie),
    gateway: GatewayController = Depends(get_gateway),
):
    await gateway.revoke_token(token)
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
    if code != 200:
        raise HTTPException(status_code=code, detail=data)
    return data
