from .mde import MDE
import torch
from infer import InferenceHelper
from PIL import Image

class AdaBins(MDE):

    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.infer_helper = None
        self.model_name = model_name

    def setup_model(self, model: InferenceHelper) -> None:
        super().setup_model(model)
        self.infer_helper = model

    def infer_depth(self, input_image: str):

        try:
            img = Image.open(input_image).convert("RGB")

            target_w = 640
            target_h = 480

            # mantener proporción
            img.thumbnail((target_w, target_h))

            # crear canvas negro
            canvas = Image.new("RGB", (target_w, target_h))

            # centrar imagen
            offset_x = (target_w - img.width) // 2
            offset_y = (target_h - img.height) // 2

            canvas.paste(img, (offset_x, offset_y))

            with torch.no_grad():
                _, predicted_depth = self.infer_helper.predict_pil(canvas)

            return predicted_depth.squeeze()

        except Exception as e:
            print(f"Error en {input_image}: {e}")
            return None