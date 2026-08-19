from typing import Tuple, List
from cv2.typing import MatLike
import cv2
import numpy as np
from app.core.models.hunyuan3d_2.hunyuan3d_2 import HunyuanModel
from app.core.config import UPLOAD_DIR
from fastapi.responses import FileResponse
import os
from PIL import Image
import traceback

def generate_scanning_image(image: np.ndarray, filename: str):
    try:
        hunyuan: HunyuanModel = HunyuanModel()
        hunyuan.set_up_model()
        # OpenCV BGR -> RGB -> PIL
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)

        hunyuan.generate_mesh(image_pil)
        hunyuan.save_mesh(filename)

        hunyuan.clear_memory()

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise
    
    return {
        "status": "200",
        "message": "generado escaneo 3d"
    }