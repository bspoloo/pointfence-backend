import torch
from PIL import Image
from cv2.typing import MatLike
from app.core.models.hunyuan3d_2.hy3dgen.shapegen.pipelines import Hunyuan3DDiTFlowMatchingPipeline
import cv2
from typing import Literal, Any
import numpy as np
from numpy.typing import NDArray
from app.core.config import UPLOAD_DIR, CHECKPOINTS_DIR
import os

class HunyuanModel:
    pipeline: Any = None
    predictor: Any = None
    mesh: Any = None
    device: Literal['cuda', 'cpu']

    def set_up_model(self)->None:

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            CHECKPOINTS_DIR,
            subfolder="hunyuan3d-dit-v2-mini-turbo",
            use_safetensors=True,
            device=self.device
        )

    def generate_mesh(self, image: Image.Image):
        mesh = self.pipeline(
            image=image,
            num_inference_steps=5,
            octree_resolution=256,
            num_chunks=10000,
            output_type="trimesh",
        )[0]
        self.mesh = mesh

    def save_mesh(self, filename: str)->None:
        meshs_dir = os.path.join(UPLOAD_DIR, "scanings")
        base_name = os.path.splitext(filename)[0]

        os.makedirs(meshs_dir, exist_ok=True)
        output_mesh = os.path.join(meshs_dir,f"{base_name}_3d.glb")
        self.mesh.export(output_mesh)
    
    def clear_memory(self)->None:
        if self.pipeline is not None:
            del self.pipeline

        self.pipeline = None

        import gc
        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()