from .mde import MDE
import torch
import cv2
from PIL import Image
from app.core.models.depth_anything_v2.dpt import DepthAnythingV2 # Importar el modelo Depth Anything V2
from app.core.config import DEVICE, CHECKPOINTS_DIR

class DepthAnything_V2(MDE):
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_name = self.__class__.__name__
        self.model_configs = {
            'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
            'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
            'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]},
            'vitg': {'encoder': 'vitg', 'features': 384, 'out_channels': [1536, 1536, 1536, 1536]}
        }

    def setup_model(self)-> None:
        super().setup_model()
        encoder = 'vitl'
        self.model = DepthAnythingV2(**self.model_configs[encoder])
        self.model.load_state_dict(torch.load(f'{CHECKPOINTS_DIR}/depth_anything_v2/depth_anything_v2_vitl.pth'))
        self.model.to(DEVICE).eval()

    def infer_depth(self, input_image: str):
        super().infer_depth(input_image)
        
        try:
            raw_img = cv2.imread(input_image)
            depth = self.model.infer_image(raw_img)
            return depth
            
        except Exception as e:
            print(f"Error en {input_image}: {e}")
            return None