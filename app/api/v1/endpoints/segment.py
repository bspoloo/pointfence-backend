from fastapi import APIRouter, UploadFile, File, Form
from app.schemas.file_schema import FileSchema
from app.services.segment_service import segment_image_procesed
import numpy as np
import cv2
import json

router = APIRouter()

@router.post("/")
async def segment_image(image: UploadFile = File(...), coords: str = Form(...)):
    contents = await image.read()
    coordinates = json.loads(coords)
    np_image = np.frombuffer(contents, np.uint8)

    image_bgr = cv2.imdecode( np_image, cv2.IMREAD_COLOR)
    
    return segment_image_procesed(image_bgr, image.filename, (coordinates['xs'], coordinates['ys']))


# @router.get("/{file_id}")
# async def get_file(file_id: int):
#     return {"file_id": file_id}