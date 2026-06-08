from .mde import MDE
import torch
import cv2
from PIL import Image
from app.core.config import DEVICE
from app.functions.save_point_cloud import export_point_cloud_relative

class MidasV3(MDE):
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_name = self.__class__.__name__
        self.transform = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def setup_model(self)-> None:
        super().setup_model()
        model_type = "DPT_Large"
        # midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
        self.transform = midas_transforms.dpt_transform if "DPT" in model_type else midas_transforms.small_transform
        self.model = torch.hub.load("intel-isl/MiDaS", model_type, trust_repo=True)
        self.model.to(DEVICE).eval()


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
    def export_point_cloud_model(self, depth_map, color_image, output_ply_path, mask_points=None, step=4, depth_visual = 20.0):
        super().export_point_cloud_model(depth_map, color_image, output_ply_path, mask_points=mask_points, step=step, depth_visual = depth_visual)
        return export_point_cloud_relative(depth_map, color_image, output_ply_path, mask_points, step, depth_visual)