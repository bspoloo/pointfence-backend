from fastapi import APIRouter, Depends, UploadFile, File, Form, WebSocket
from app.core.security.security import get_current_user
from app.models.user import User
from app.schemas.file_schema import FileSchema
from app.services.mde_service import send_poinst_cloud_unreal
from app.services.segment_service import segment_image_procesed
from app.core.classes.connection_manager import ConnectionManager
import numpy as np
import cv2
import json

router = APIRouter()
manager = ConnectionManager()

@router.get("/me")
async def sends_points_cloud( current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "names": current_user.names,
        "email": current_user.email,
    }
