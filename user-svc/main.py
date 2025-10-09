from fastapi import FastAPI

from routes.auth_router import router as auth_router
from routes.user_router import router as user_router

app = FastAPI(title="PeerPrep User Service")

app.include_router(auth_router)
app.include_router(user_router)
