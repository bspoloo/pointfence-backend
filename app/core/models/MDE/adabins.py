from .mde import MDE
import torch
from app.core.models.adabins.infer import InferenceHelper
from PIL import Image
from app.functions.save_point_cloud import export_point_cloud_relative

class AdaBins(MDE):

    def __init__(self):
        super().__init__()
        self.infer_helper = None
        self.model_name = self.__class__.__name__

    def setup_model(self) -> None:
        super().setup_model()
        self.infer_helper = InferenceHelper(dataset='nyu')

    def infer_depth(self, input_image: str):

        try:
            img = Image.open(input_image).convert("RGB")

            target_w = 640
            target_h = 480

            img.thumbnail((target_w, target_h))

            canvas = Image.new("RGB", (target_w, target_h))

            offset_x = (target_w - img.width) // 2
            offset_y = (target_h - img.height) // 2

            canvas.paste(img, (offset_x, offset_y))

            with torch.no_grad():
                _, predicted_depth = self.infer_helper.predict_pil(canvas)

            return predicted_depth.squeeze()

        except Exception as e:
            print(f"Error en {input_image}: {e}")
            return None
    def export_point_cloud_model(self, depth_map, color_image, output_ply_path, mask_points=None, step=4, depth_visual = 20.0):
        super().export_point_cloud_model(depth_map, color_image, output_ply_path, mask_points=mask_points, step=step, depth_visual = depth_visual)
        return export_point_cloud_relative(depth_map, color_image, output_ply_path, mask_points, step, depth_visual)