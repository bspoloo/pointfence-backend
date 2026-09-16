from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.security.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.file_schema import FileSchema
from app.services.segment_service import segment_image_procesed
import numpy as np
import cv2
import json

router = APIRouter()

@router.post("/")
async def segment_image(image: UploadFile = File(...), coords: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contents = await image.read()
    coordinates = json.loads(coords)
    np_image = np.frombuffer(contents, np.uint8)

    image_bgr = cv2.imdecode( np_image, cv2.IMREAD_COLOR)
    
    return await segment_image_procesed(image_bgr, image.filename, (coordinates['xs'], coordinates['ys']), db, current_user)
