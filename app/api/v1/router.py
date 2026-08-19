from fastapi import APIRouter, FastAPI
from app.api.v1.endpoints import segment, points_cloud, scanning

routes = APIRouter()
routes.include_router(segment.router, prefix="/segment", tags=["segment"])
routes.include_router(points_cloud.router, prefix="/points", tags=["points"])
routes.include_router(scanning.router, prefix="/scanning", tags=["scanning"])