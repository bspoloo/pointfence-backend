from fastapi import APIRouter, FastAPI
from app.api.v1.endpoints import segment

routes = APIRouter()
routes.include_router(segment.router, prefix="/segment", tags=["segment"])