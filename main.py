from fastapi import FastAPI
from app.api.v1.router import routes

app = FastAPI()

app.include_router(router=routes, prefix="/api/v1", tags=["v1"])