from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, WebSocket, status
from sqlalchemy.orm import Session
from app.db.database import get_db
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

@router.post("/login", response_model= TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return await login_request(data, db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"[EROR] {e}",
        )