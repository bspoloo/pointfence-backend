from fastapi import APIRouter, UploadFile, File, Form, WebSocket
from app.schemas.file_schema import FileSchema
from app.services.mde_service import send_poinst_cloud_unreal
from app.services.segment_service import segment_image_procesed
from app.core.classes.connection_manager import ConnectionManager
import numpy as np
import cv2
import json

router = APIRouter()
manager = ConnectionManager()

@router.post("/generate")
async def sends_points_cloud(
    image: UploadFile = File(...),
    mask: UploadFile = File(None),
    configs: str = Form(...)
):
    config = json.loads(configs)
    print(config)
    if not config:
        return {
            "status": "error",
            "message": "Sin ajustes establecidos"
        }

    img = await image.read()
    np_image = np.frombuffer(img, np.uint8)
    image_bgr = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    mask_bgr = None

    if mask is not None:
        msk = await mask.read()
        np_mask = np.frombuffer(msk, np.uint8)
        mask_bgr = cv2.imdecode(np_mask, cv2.IMREAD_COLOR)
    
    return await send_poinst_cloud_unreal(
        image_bgr,
        mask_bgr,
        config,
        (image.filename, mask.filename if mask else None)
    )

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
