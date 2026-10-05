from fastapi import APIRouter
from app.api.v1.resources import router as resources_router
from app.api.v1.categories import router as categories_router
from app.api.v1.auth import router as auth_router
from app.api.v1.reports import router as reports_router
from app.api.v1.admin import router as admin_router
from app.api.v1.cron import router as cron_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(resources_router)
api_router.include_router(categories_router)
api_router.include_router(auth_router)
api_router.include_router(reports_router)
api_router.include_router(admin_router)
api_router.include_router(cron_router)
