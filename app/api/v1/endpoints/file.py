from fastapi import APIRouter
from app.schemas.file_schema import FileSchema
from app.services.file_service import create_file_service

router = APIRouter()

@router.post("/file")
async def create_file(file: FileSchema):
    return create_file_service(file)