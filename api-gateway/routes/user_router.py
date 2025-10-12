
from fastapi import APIRouter, Depends, HTTPException, Request

from controllers.gateway_controller import GatewayController
from service.settings import get_gateway, get_token_from_cookie
from utils.logger import log

router = APIRouter(prefix="/users", tags=["users"])


async def auth_user(
    token_str: str = Depends(get_token_from_cookie),
    gateway: GatewayController = Depends(get_gateway),
) -> dict:
    """
    Validates the token from the cookie and returns its payload.
    This function now orchestrates token retrieval and validation.
    """
    return await gateway.validate_token(token_str)


@router.get("/me")
async def me(
    token_payload: dict = Depends(auth_user),
    gateway: GatewayController = Depends(get_gateway),
):
    """
    Get the current user's details. The `auth_user` dependency protects this route.
    """
    user_id = token_payload.get("userID")
    log.info(f"Fetching details for user={user_id}")

    code, data = await gateway.forward(
        "GET",
        "/users/me",
        headers={
            "X-User-ID": str(user_id),
        },
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=data)

    # Combine token info with user data
    response_data = {
        "token_info": {
            "created_at": token_payload.get("created_at"),
            "expires_at": token_payload.get("expires_at"),
        },
        "user_data": data if isinstance(data, dict) else {},
    }
    return response_data


@router.patch("/me")
async def me_patch(
    request: Request,
    token_payload: dict = Depends(auth_user),
    access_token: str = Depends(get_token_from_cookie),
    gateway: GatewayController = Depends(get_gateway),
):
    """
    Update the current user's details. Also protected by `auth_user`.
    """
    user_id = token_payload.get("userID")
    body = await request.json()

    code, data = await gateway.forward(
        "PATCH",
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-User-ID": str(user_id),
        },
        data=body,
    )

    if code != 200:
        raise HTTPException(status_code=code, detail=data)

    return data


# Wildcard proxy for any other /users/* route
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
async def forward_users(
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
