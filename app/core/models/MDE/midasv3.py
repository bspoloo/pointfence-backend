from .mde import MDE
import torch
import cv2
from PIL import Image

class MidasV3(MDE):
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.model = None
        self.model_name = model_name
        self.transform = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def setup_model(self, model)-> None:
        super().setup_model(model)
        model_type = "DPT_Large"
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
        self.transform = midas_transforms.dpt_transform if "DPT" in model_type else midas_transforms.small_transform
        self.model = model

    def infer_depth(self, input_image: str):
        super().infer_depth(input_image)
        
        try:
            img = cv2.imread(input_image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            input_batch = self.transform(img).to(self.device)
        
            with torch.no_grad():
                prediction = self.model(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            return prediction.cpu().numpy()
            
        except Exception as e:
            print(f"Error en {input_image}: {e}")
            return None