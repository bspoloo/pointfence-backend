from fastapi import APIRouter, FastAPI
from app.api.v1.endpoints import file

routes = APIRouter()
routes.include_router(file.router, prefix="/file", tags=["file"])