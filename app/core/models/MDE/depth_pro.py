from app.core.models.MDE.mde import MDE
from app.core.config import DEVICE
import torch
from app.core.models import depth_pro
from app.functions.save_point_cloud import export_point_cloud_meters
import traceback

class DepthPro(MDE):
    def __init__(self):
        super().__init__()
        self.model = None
        self.transform = None
        self.model_name = self.__class__.__name__

    def setup_model(self)-> None:
        super().setup_model()
        encoder = 'vitl'
        self.model, self.transform = depth_pro.create_model_and_transforms()
        # self.model = torch.device(DEVICE)
        self.model = self.model.to(DEVICE).eval()

    def infer_depth(self, input_image: str):
        super().infer_depth(input_image)
        
        try:
            image, _, f_px = depth_pro.load_rgb(input_image)
            transformed_image = self.transform(image).to(DEVICE)
            
            with torch.no_grad():
                prediction = self.model.infer(transformed_image, f_px=f_px)
                print("prediction keys:", prediction.keys())
            
            depth_m = prediction["depth"].cpu().numpy()
            # f_px_val = float(f_px.cpu().numpy()) if torch.is_tensor(f_px) else float(f_px)
            
            return depth_m
                
        except Exception as e:
            print(f"Error en {input_image}: {e}")
            traceback.print_exc()
            return None
        
    def export_point_cloud_model(self, depth_map, color_image, output_ply_path, mask_points=None, step=4, depth_visual = 20.0):
        super().export_point_cloud_model(depth_map, color_image, output_ply_path, mask_points=None, step=4, depth_visual = 20.0)
        return export_point_cloud_meters(depth_map, color_image, output_ply_path, self.model_name,fx=None, fy=None, cx=None, cy=None, mask_points=mask_points,step=step, depth_visual= depth_visual)