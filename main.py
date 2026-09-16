from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import routes
from app.core.config import UPLOAD_DIR

app = FastAPI()
app.mount(
    "/api/v1/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)
app.include_router(router=routes, prefix="/api/v1", tags=["v1"])