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

manager = ConnectionManager()

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

async def send_scanned_to_unreal(
    image: MatLike,
    mask: MatLike,
    filename: str
):
    try:

        base_name = os.path.splitext(filename)[0]

        hunyuan: HunyuanModel = HunyuanModel()

        print("Configurando Hunyuan3D...")

        hunyuan.set_up_model()
        print("Convirtiendo imagen a objeto...")

        object_image = convert_image_to_object(
            image,
            mask,
            base_name
        )

        if object_image is None:
            raise RuntimeError("No se pudo crear la imagen del objeto.")

        image_object = Image.fromarray(object_image)
        print("Generando mesh 3D...")

        mesh = hunyuan.generate_mesh(image_object)
        output_path = hunyuan.save_mesh(base_name)

        if mesh is None:
            raise RuntimeError("Hunyuan3D no generó ningún mesh.")

        print("Mesh generado correctamente.")
        print(f"Vertices generados: "f"{len(mesh.vertices)}")
        print(f"Triángulos generados: "f"{len(mesh.faces)}")
        print("Enviando mesh a Unreal...")

        success = await manager.send_mesh_binary(mesh)

        if not success:
            print("No se pudo enviar el mesh a Unreal.")

            return {
                "status": "500",
                "message": "No se pudo enviar el mesh a Unreal"
            }

        print("Mesh enviado correctamente a Unreal.")

        hunyuan.clear_memory()
        return {
            "status": "200",
            "message": "generado escaneo 3d"
        }

    except Exception as e:

        print(
            f"[ERROR] {type(e).__name__}: {e}"
        )

        traceback.print_exc()

        raise