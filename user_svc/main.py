from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth_router import fastapi_users
from routes.auth_router import router as auth_router
from models.db_models import User

app = FastAPI(title="PeerPrep API Gateway")
# Configure CORS
origins = [
    "http://localhost:5173",  # Vite development server
    # Add production URL after deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Important for cookie-based controllers
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],
)

app.include_router(auth_router)

# Get the current_user dependency from FastAPIUsers instance
current_user = fastapi_users.current_user(active=True)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"
