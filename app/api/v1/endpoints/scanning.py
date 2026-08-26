from fastapi import APIRouter, UploadFile, File, Form, WebSocket
from app.core.classes.connection_manager import ConnectionManager
from app.schemas.file_schema import FileSchema
from app.services.scanning_service import send_scanned_to_unreal
import numpy as np
import cv2
import json
from PIL import Image

router = APIRouter()
manager = ConnectionManager()

@router.post("/generate")
async def scanning_image(image: UploadFile = File(...), mask: UploadFile = File(...)):
    img = await image.read()
    np_image = np.frombuffer(img, np.uint8)
    image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    msk_bgr = None

    if mask is not None:
        msk = await mask.read()
        np_mask = np.frombuffer(msk, np.uint8)
        msk_bgr = cv2.imdecode(np_mask, cv2.IMREAD_GRAYSCALE)

    return await send_scanned_to_unreal(image_bgr, msk_bgr ,image.filename)

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