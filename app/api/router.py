from fastapi import APIRouter

from app.api.endpoints import webhook, admin

api_router = APIRouter()
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])