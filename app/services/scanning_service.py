from typing import Tuple, List
from cv2.typing import MatLike
import cv2
from fastapi import WebSocket
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.classes.connection_manager import ConnectionManager
from app.core.models.hunyuan3d_2.hunyuan3d_2 import HunyuanModel
from app.core.config import UPLOAD_DIR
from fastapi.responses import FileResponse
import os
import traceback
from app.core.config import UPLOAD_DIR, BASE_DIR
import json
import base64
import asyncio
import trimesh
import traceback

from app.models.image import Image
from PIL import Image as PILImage
from app.models.image_mask import ImageMask
from app.models.mask import Mask
from app.models.object import Object
from app.models.scaning import Scanning
from app.models.user import User
from app.schemas.create_file import CreateModel, CreateObject
from app.services.files_services import get_scanning_by_filename, save_image_mask, save_object, save_scanning

manager = ConnectionManager()

async def convert_image_to_object(image: MatLike, mask: MatLike, base_name: str, db: Session)->tuple[MatLike, Object] | None:
    objects_dir = os.path.join(UPLOAD_DIR, "objects")

    os.makedirs(objects_dir, exist_ok=True)

    output_object = os.path.join(objects_dir,f"{base_name}_object.png")
    mask_uint8 = mask.astype(np.uint8)

    image_rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    image_rgba[:, :, 3] = mask_uint8
    success = cv2.imwrite(output_object,image_rgba)

    image_mask = await save_image_mask(
        filename=base_name,
        db=db
    )

    object = await save_object(
        file=CreateObject(
            filename=base_name,
            extension='.png',
            url=output_object,
            image_mask_id= image_mask.id
        ),
        db=db
    )

    if success is not True:
        return None

    return image_rgba, object

async def get_object_data(db: Session,user: User, page: int = 1, limit: int = 0):
    offset = (page -1) * limit
    scannins = db.scalars(
        select(Object)
        .where(
                Object.image_mask.has(
                    ImageMask.image.has(
                        Image.user.has(
                            User.id == user.id
                        )
                    )
                )
        )
        .where(
                Object.image_mask.has(
                    ImageMask.mask.has(
                        Mask.user.has(
                            User.id == user.id
                        )
                    )
                )
        )
        .where(Object.deleted_at.is_(None))
        .offset(offset)
        .limit(limit)
    ).all()
    return scannins

async def send_scanned_to_unreal(image: MatLike,mask: MatLike,filename: str,  db: Session):

    try:

        base_name = os.path.splitext(filename)[0]

        hunyuan: HunyuanModel = HunyuanModel()
        hunyuan.set_up_model()
        object_image , object = await convert_image_to_object(image,mask,base_name, db)

        if object_image is None:
            raise RuntimeError("No se pudo crear la imagen del objeto.")

        image_object = PILImage.fromarray(object_image)
        print("Generando mesh 3D...")

        mesh = hunyuan.generate_mesh(image_object)
        output_path = hunyuan.save_mesh(base_name)

        scanning = await save_scanning(
            file=CreateModel(
                filename=base_name,
                extension='.glb',
                url=output_path,
                object_id=object.id
            ),
            db=db
        )

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

        print(f"[ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise

async def send_file_to_unreal(filename: str, db: Session):

    try:
        scanning = await get_scanning_by_filename(filename, db=db)

        # models_dir = os.path.join(BASE_DIR, UPLOAD_DIR,"scannings")

        # file_path = os.path.join(models_dir, filename)
        file_path = scanning.url

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No se encontró el mesh: {file_path}")

        print(f"Cargando mesh desde: {file_path}")

        mesh = trimesh.load(file_path, force="mesh")
        if mesh is None:
            raise RuntimeError("No se pudo cargar el mesh.")

        print("Mesh cargado correctamente.")
        print(f"Vertices: {len(mesh.vertices)}")
        print(f"Triángulos: {len(mesh.faces)}")

        print("Enviando mesh a Unreal...")
        success = await manager.send_mesh_binary(mesh)

        if not success:

            print("No se pudo enviar el mesh a Unreal.")
            return {
                "status": "500",
                "message": "No se pudo enviar el mesh a Unreal"
            }

        print("Mesh enviado correctamente a Unreal.")
        return {
            "status": "200",
            "message": "Mesh enviado correctamente",
            "filename": filename
        }

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()

        return {
            "status": "500",
            "message": str(e)
        }