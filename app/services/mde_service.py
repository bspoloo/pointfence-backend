

import os
from typing import Tuple
from cv2.typing import MatLike
from app.core.config import UPLOAD_DIR
from app.core.models.MDE.mde import MDE
from app.core.models.MDE.depth_anything import DepthAnything_V2
from app.core.classes.models_manager import ModelManager
from app.core.classes.mask_manager import MaskManager
from app.functions.save_point_cloud import export_point_cloud
import numpy as np
import cv2

def generate_poinst_cloud(image: MatLike, mask: MatLike | None , config, filenames: Tuple[str, str]):
    h_orig, w_orig = image.shape[:2]

    try:
        output_image = os.path.join(
                UPLOAD_DIR,"images",
                filenames[0].replace(".JPG", "_image.png"),
            )
        
        output_mask = None
        cv2.imwrite(output_image, image)
        if mask is not None:
            output_mask = os.path.join(
                    UPLOAD_DIR,"masks",
                    filenames[0].replace(".JPG", "_mask.png")
                )
            cv2.imwrite(output_mask, mask)
        

        mde: MDE = ModelManager().get_mde(str(config["model"]))
        mde.setup_model()
        depth = mde.infer_depth(output_image)
        depth = cv2.resize(depth, (h_orig, w_orig), interpolation=cv2.INTER_CUBIC)

        if depth is None:
            return {
            "status": "error",
            "message": "Error en profundidad"
        }

        depth = cv2.resize(
            depth,
            (w_orig, h_orig),
            interpolation=cv2.INTER_CUBIC
        )
        
        mask_manger : MaskManager = MaskManager()
        points = mask_manger.get_point_mask(output_mask) if mask is not None else None

        os.makedirs(
            os.path.join(UPLOAD_DIR, "points", config["model"]),
            exist_ok=True
        )

        export_point_cloud(
            depth_map=depth,
            color_image=image,
            output_ply_path=os.path.join(UPLOAD_DIR,"points", config["model"],f"{filenames[0].split(".")[0]}_{config["step"]}_{config["depth_visual"]}_{"image" if mask is None else "points"}.ply"),
            mask_points=points if mask is not None else None,
            step=int(config["step"]),
            depth_visual = float(config["depth_visual"])
        )

        del depth, mde

    except Exception as e:
        print(f"[ERROR] {e}")
        return {
            "status": "error",
            "message": e
        }
    
    return {
        "status": "ok",
        "message": f"Imagenes enviadas correctamente a unreal -> {output_image} - {output_mask}"
    }
