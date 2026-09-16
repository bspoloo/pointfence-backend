from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, WebSocket
from sqlalchemy.orm import Session
from app.core.classes.connection_manager import ConnectionManager
from app.core.security.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.file_schema import FileSchema
from app.services.scanning_service import get_object_data, send_scanned_to_unreal, send_file_to_unreal
import numpy as np
import cv2
import json
from PIL import Image
from pydantic import BaseModel

router = APIRouter()
manager = ConnectionManager()

class ScannedModel(BaseModel):
    filename: str

@router.get("/list")
async def scanning_image(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_object_data(db, current_user, page, limit)

@router.post("/generate")
async def scanning_image(image: UploadFile = File(...), mask: UploadFile = File(...),  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    img = await image.read()
    np_image = np.frombuffer(img, np.uint8)
    image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    msk_bgr = None

    if mask is not None:
        msk = await mask.read()
        np_mask = np.frombuffer(msk, np.uint8)
        msk_bgr = cv2.imdecode(np_mask, cv2.IMREAD_GRAYSCALE)

    return await send_scanned_to_unreal(image_bgr, msk_bgr ,image.filename, db)

@router.post("/filename")
async def scanning_image(data: ScannedModel, db: Session = Depends(get_db)):
    return await send_file_to_unreal(data.filename, db=db)

@router.websocket("/ws/unreal")
async def websocket_unreal_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Mensaje de UE4: {data}")
            if data == "READY":
                await websocket.send_text("ACK")
    except Exception as e:
        print(f"Error en conexion: {e}")
        manager.disconnect(websocket)

