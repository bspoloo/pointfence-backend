from abc import ABC, abstractmethod
import torch
class MDE:
    
    def setup_model(self)-> None:
        self.model = None
        print(f"Cargando modelo")

    def infer_depth(self, input_image: str):
        print(f"haciendo inferencia con {self.model_name} a {input_image}")
    
    def export_point_cloud_model(self, depth_map, color_image, output_ply_path, mask_points=None, step=4, depth_visual = 20.0):
        print(f"Exportando nube de puntos...")

    def clear_memory(self):
        print(f"Limpiando memoria")
        del self.model
        torch.cuda.empty_cache()