from fastapi import APIRouter

from ._well_known_routes import router as _well_known_router
from .authorization_routes import router as auth_router
from .token_routes import router as token_router
from .user_routes import router as user_router

api_router = APIRouter()

api_router.include_router(_well_known_router)
api_router.include_router(auth_router)
api_router.include_router(token_router)
api_router.include_router(user_router)