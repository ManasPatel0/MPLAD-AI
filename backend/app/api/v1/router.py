"""Main API v1 router consolidating all sub-routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, health, ingest, projects

api_v1_router = APIRouter()

# Register endpoint sub-routers (each sub-router already defines its own resource prefix)
api_v1_router.include_router(health.router, prefix="", tags=["System"])
api_v1_router.include_router(auth.router, prefix="", tags=["Authentication & Access Control"])
api_v1_router.include_router(projects.router, prefix="", tags=["Projects Management"])
api_v1_router.include_router(analytics.router, prefix="", tags=["Analytics & Executive Dashboards"])
api_v1_router.include_router(ingest.router, prefix="", tags=["Data Ingestion & ETL"])
