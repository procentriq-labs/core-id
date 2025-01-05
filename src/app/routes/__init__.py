from fastapi import APIRouter

from .authorization_routes import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router)