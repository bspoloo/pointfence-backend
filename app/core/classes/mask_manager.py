import numpy as np
import os
import cv2

class MaskManager:
    def __init__(self, threshold: int = 127):
        self.threshold = threshold

    def get_point_mask(self, mask_path):
        print("MASK PATH:", mask_path)
        if not os.path.exists(mask_path):
            print(f"No existe ruta: {mask_path}")
            return None

        mask = cv2.imread(
            mask_path,
            cv2.IMREAD_GRAYSCALE
        )

        if mask is None:
            print(f"No se pudo leer máscara: {mask_path}")
            return None

        _, mask_bin = cv2.threshold(
            mask,
            self.threshold,
            255,
            cv2.THRESH_BINARY
        )

        ys, xs = np.where(mask_bin == 255)

        points = np.column_stack((xs, ys)).astype(np.int32)

        return points