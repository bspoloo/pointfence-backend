from fastapi import APIRouter, HTTPException, UploadFile, File, Form, WebSocket, status
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.file_schema import FileSchema
from app.services.auth_service import login_request
from app.services.mde_service import send_poinst_cloud_unreal
from app.services.segment_service import segment_image_procesed
from app.core.classes.connection_manager import ConnectionManager
import numpy as np
import cv2
import json

router = APIRouter()
manager = ConnectionManager()

@router.post("/auth/login", data= TokenResponse)
async def login(data: LoginRequest):
    try:
        return login_request(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )