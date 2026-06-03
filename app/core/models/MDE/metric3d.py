from .mde import MDE
import torch
import cv2
from PIL import Image
import numpy as np
from typing import Tuple, Dict, List

class Metric3D(MDE):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.ort_session = None
        self.model_name = model_name

    def setup_model(self, ort_session)-> None:
        super().setup_model(ort_session)
        self.ort_session = ort_session

    def infer_depth(self, input_image: str):
        super().infer_depth(input_image)
        
        try:
            img = cv2.imread(input_image)

            if img is None:
                print(f"No se pudo cargar: {input_image}")
                return None
        
            rgb_image = img[:, :, ::-1]
            original_shape = rgb_image.shape[:2]
        
            input_size = (544, 1216)
        
            onnx_input, pad_info = self.prepare_input(rgb_image, input_size)
            outputs = self.ort_session.run(None, {"pixel_values": onnx_input["image"]})
            depth = outputs[0].squeeze()
        
            depth = depth[
                pad_info[0]: input_size[0] - pad_info[1],
                pad_info[2]: input_size[1] - pad_info[3],
            ]
        
            depth = cv2.resize(
                depth,
                (original_shape[1], original_shape[0]),
                interpolation=cv2.INTER_LINEAR
            )
        
            # depth_vis = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
            # depth_vis = depth_vis.astype(np.uint8)
            # depth_colored = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)
        
            return depth
            
        except Exception as e:
            print(f"Error en {input_image}: {e}")
            return None

    def prepare_input(self, rgb_image: np.ndarray, input_size: Tuple[int, int] ) -> Tuple[Dict[str, np.ndarray], List[int]]: # La función devuelve un diccionario con la imagen preparada y una lista con la información de padding
        h, w = rgb_image.shape[:2]
        scale = min(input_size[0] / h, input_size[1] / w)
        rgb = cv2.resize(
            rgb_image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_LINEAR
        ) # Redimensionar la imagen manteniendo la relación de aspecto
        
        padding = [123.675, 116.28, 103.53]
        h, w = rgb.shape[:2]
        pad_h = input_size[0] - h
        pad_w = input_size[1] - w
        pad_h_half = pad_h // 2
        pad_w_half = pad_w // 2
        rgb: np.ndarray = cv2.copyMakeBorder(
            rgb,
            pad_h_half,
            pad_h - pad_h_half,
            pad_w_half,
            pad_w - pad_w_half,
            cv2.BORDER_CONSTANT,
            value=padding,
        )
        pad_info = [pad_h_half, pad_h - pad_h_half, pad_w_half, pad_w - pad_w_half]
        
        # Preparar la imagen para el modelo ONNX: convertir a formato CHW (Canal, Alto, Ancho) y agregar una dimensión de lote
        onnx_input = {
            "image": np.ascontiguousarray(
                np.transpose(rgb, (2, 0, 1))[None], dtype=np.float32
            ),  # 1, 3, H, W
        }
        # Devolver la imagen preparada y la información de padding para su uso posterior en la post-procesamiento
        return onnx_input, pad_info