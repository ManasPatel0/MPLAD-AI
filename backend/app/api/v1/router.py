"""Main API v1 router consolidating all sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_v1_router = APIRouter()

# Register endpoint sub-routers
api_v1_router.include_router(health.router, prefix="", tags=["System"])
