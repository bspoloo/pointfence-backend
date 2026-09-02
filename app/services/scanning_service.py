from typing import Tuple, List
from cv2.typing import MatLike
import cv2
from fastapi import WebSocket
import numpy as np
from app.core.classes.connection_manager import ConnectionManager
from app.core.models.hunyuan3d_2.hunyuan3d_2 import HunyuanModel
from app.core.config import UPLOAD_DIR
from fastapi.responses import FileResponse
import os
from PIL import Image
import traceback
from app.core.config import UPLOAD_DIR
import json
import base64
import asyncio

def convert_image_to_object(image: MatLike, mask: MatLike, base_name: str)->MatLike | None:
    objects_dir = os.path.join(UPLOAD_DIR, "objects")

    os.makedirs(objects_dir, exist_ok=True)

    output_object = os.path.join(objects_dir,f"{base_name}_object.png")
    mask_uint8 = mask.astype(np.uint8)

    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    image_rgba[:, :, 3] = mask_uint8
    success = cv2.imwrite(output_object,image_rgba)

    if success is not True:
        return None

    return image_rgba

async def send_scanned_to_unreal(image: MatLike, mask: MatLike, filename: str):
    try:
        base_name = filename.split(".")[0]
        hunyuan: HunyuanModel = HunyuanModel()
        hunyuan.set_up_model()

        image_object = Image.fromarray(convert_image_to_object(image, mask, base_name))

        hunyuan.generate_mesh(image_object)
        output_path = hunyuan.save_mesh(filename)
        hunyuan.clear_memory()

        # manager = ConnectionManager()
        # await asyncio.sleep(0.5)

        # if output_path and os.path.exists(output_path):
        #     success = await manager.send_glb_file(output_path)
        #     if success:
        #         print(f"Archivo GLB enviado a Unreal: {output_path}")
        #     else:
        #         print(f"Error enviando archivo GLB a Unreal")
        # else:
        #     print(f"Archivo GLB no encontrado: {output_path}")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise
    
    return {
        "status": "200",
        "message": "generado escaneo 3d"
    }