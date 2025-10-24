from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer

from controllers.gateway_controller import GatewayController
from service.cookie_management import get_token_from_cookie, set_access_token_cookie
from service.redis_settings import get_gateway
from utils.logger import log
from utils.utils import get_envvar

USER_SERVICE_LOGIN_PATH = get_envvar("USER_SERVICE_LOGIN_PATH")

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
    status_code, resp = await gateway.forward("POST", USER_SERVICE_LOGIN_PATH, data=body, user_data={})
    if not (200 <= status_code < 300):
        raise HTTPException(
            status_code=status_code,
            detail=resp,
        )

    if not resp:
        raise HTTPException(
            status_code=502, detail="User service did not return a response"
        )
    
    token = await gateway.store_token(resp)
    log.info(f"Login succeeded for user={username}")

    # --- Set the access token in an cookie ---
    await set_access_token_cookie(
        response=response,
        token=token
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
