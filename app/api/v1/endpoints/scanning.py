from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.file_schema import FileSchema
from app.services.scanning_service import generate_scanning_image
import numpy as np
import cv2
import json
from PIL import Image

router = APIRouter()

@router.post("/")
async def scanning_image(image: UploadFile = File(...)):
    contents = await image.read()

    np_image = np.frombuffer(contents, dtype=np.uint8)
    image_bgr = cv2.imdecode(
        np_image,
        cv2.IMREAD_COLOR
    )

    if image_bgr is None:
        raise ValueError("No se pudo decodificar la imagen")

    return generate_scanning_image(image_bgr,image.filename)