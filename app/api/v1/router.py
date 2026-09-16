from fastapi import APIRouter, FastAPI
from app.db import base
from app.api.v1.endpoints import segment, points_cloud, scanning, auth, me

routes = APIRouter()
routes.include_router(segment.router, prefix="/segment", tags=["segment"])
routes.include_router(points_cloud.router, prefix="/points", tags=["points"])
routes.include_router(scanning.router, prefix="/scanning", tags=["scanning"])
routes.include_router(auth.router, prefix="/auth", tags=["login"])
routes.include_router(me.router, prefix="/profile", tags=["me"])