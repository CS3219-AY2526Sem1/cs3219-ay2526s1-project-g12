from fastapi import APIRouter

from models.api_models import UserRead, UserUpdate
from service.auth_svc import fastapi_users

router = APIRouter()
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)
