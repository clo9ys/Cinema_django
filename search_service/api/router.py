from fastapi import APIRouter
from search_service.api.v1.auth import router as auth

api_router = APIRouter()

api_router.include_router(auth, prefix="/auth", tags=["Authentication"])