from abc import ABC, abstractmethod
import torch
class MDE:
    
    def setup_model(self)-> None:
        print(f"Cargando modelo")

    def infer_depth(self, input_image: str):
        print(f"haciendo inferencia con {self.model_name} a {input_image}")
    
    def clear_memory(self):
        print(f"Limpiando memoria")
        torch.cuda.empty_cache()