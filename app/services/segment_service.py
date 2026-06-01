from typing import Tuple, List
from cv2.typing import MatLike
import cv2
import numpy as np
from app.core.classes.sam_predictor import SAMPredictor
from app.core.config import UPLOAD_DIR
from fastapi.responses import FileResponse
import os

def segment_image_procesed(image: MatLike, filename: str, coords: Tuple[List[int], List[int]]):
    h, w = image.shape[:2]
    xs = np.array(coords[0], dtype=int)
    ys = np.array(coords[1], dtype=int)
    
    valid_mask = (
        (xs >= 0) & (xs < w) &
        (ys >= 0) & (ys < h)
    )

    xs = xs[valid_mask]
    ys = ys[valid_mask]

    if len(xs) == 0:
        print("[WARNING] Sin puntos válidos")
        return

    input_points = np.column_stack((xs, ys))
    input_labels = np.ones(len(input_points))

    try:

        sam_predictor : SAMPredictor = SAMPredictor()
        sam_predictor.set_up_model()
        sam_predictor.set_image(image)
        mask = sam_predictor.predict_mask(input_points, input_labels)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        output_mask = os.path.join(
            UPLOAD_DIR,
            filename.replace(".JPG", "_mask.png")
        )
        mask_uint8 = (mask.astype(np.uint8)) * 255
        cv2.imwrite(output_mask, mask_uint8)

    except Exception as e:
        print(f"[ERROR] {e}")
        return

    # aquí va lógica real (validaciones, reglas, etc.)
    # return save_file(file)
    return FileResponse(
        path=output_mask,
        media_type="image/png",
        filename=os.path.basename(output_mask)
    )