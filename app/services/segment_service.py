from typing import Tuple, List
from cv2.typing import MatLike
import cv2
import numpy as np
from app.core.models.sam_predictor.sam_predictor import SAMPredictorModel
from app.core.config import UPLOAD_DIR
from fastapi.responses import FileResponse
import os


def segment_image_procesed(image: MatLike,filename: str,coords: Tuple[List[int], List[int]]):
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
        return None

    input_points = np.column_stack((xs, ys))
    input_labels = np.ones(len(input_points))

    try:
        sam_predictor: SAMPredictorModel = SAMPredictorModel()
        sam_predictor.set_up_model()
        image_rgb = sam_predictor.set_image(image)
        mask = sam_predictor.predict_mask(
            input_points,
            input_labels
        )
        sam_predictor.clear_memory()

        masks_dir = os.path.join(UPLOAD_DIR, "masks")
        images_dir = os.path.join(UPLOAD_DIR, "images")

        os.makedirs(masks_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)

        base_name = os.path.splitext(filename)[0]

        output_mask = os.path.join(
            masks_dir,
            f"{base_name}_mask.png"
        )

        output_image = os.path.join(
            images_dir,
            f"{base_name}_image.png"
        )


        mask_uint8 = (mask.astype(np.uint8)) * 255

        cv2.imwrite(output_mask,mask_uint8)
        cv2.imwrite(output_image,image_rgb)

        print(f"[INFO] Mask: {output_mask}")
        print(f"[INFO] Image: {output_image}")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return None
    
    return FileResponse(
        path=output_mask,
        media_type="image/png",
        filename=os.path.basename(output_mask)
    )