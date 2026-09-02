import gc
import os
from typing import Literal, Any

import torch
from PIL import Image

from app.core.models.hunyuan3d_2.hy3dgen.shapegen.pipelines import (Hunyuan3DDiTFlowMatchingPipeline)
from app.core.models.hunyuan3d_2.hy3dgen.texgen import (Hunyuan3DPaintPipeline)

from app.core.config import UPLOAD_DIR, CHECKPOINTS_DIR

class HunyuanModel:
    pipeline_mesh_gen: Any = None
    pipeline_text_gen: Any = None
    mesh: Any = None
    device: Literal["cuda", "cpu"]

    def set_up_model(self) -> None:

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Using device: {self.device}")
        print("Loading Hunyuan3D mesh generation model...")

        self.pipeline_mesh_gen = (
            Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                model_path=str(CHECKPOINTS_DIR),
                subfolder="hunyuan3d-dit-v2-mini-turbo",
                use_safetensors=True,
                device=self.device,
            )
        )

        print("Mesh generation model loaded.")

    def generate_mesh(self, image: Image.Image):

        self.mesh = self.pipeline_mesh_gen(
            image=image,
            num_inference_steps=5,
            octree_resolution=256,
            num_chunks=10000,
            output_type="trimesh",
        )[0]

        self.clear_mesh_pipeline()

        # self.pipeline_text_gen = Hunyuan3DPaintPipeline.from_pretrained(
        #     model_path=str(CHECKPOINTS_DIR),
        #     subfolder="hunyuan3d-paint-v2-0",
        # )
        # mesh = self.pipeline_text_gen(self.mesh,image=image)
        # self.clear_paint_pipeline()
        return self.mesh

    def clear_mesh_pipeline(self):

        if self.pipeline_mesh_gen is not None:
            print("Releasing mesh generation model...")
            del self.pipeline_mesh_gen
            self.pipeline_mesh_gen = None

        gc.collect()

        if torch.cuda.is_available():

            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    def clear_paint_pipeline(self)->None:

        if self.pipeline_text_gen is not None:

            del self.pipeline_text_gen
            self.pipeline_text_gen = None

        gc.collect()

        if torch.cuda.is_available():

            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    def clear_memory(self)->None:
        if self.pipeline_mesh_gen is not None:
            del self.pipeline_mesh_gen

        if self.pipeline_text_gen is not None:
            del self.pipeline_text_gen

        del self.mesh
        
        self.pipeline_mesh_gen = None
        self.pipeline_text_gen = None

        self.mesh = None

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    def save_mesh(self, filename: str)-> str:

        meshs_dir = os.path.join(
            UPLOAD_DIR,
            "scanings"
        )

        base_name = os.path.splitext(filename)[0]

        os.makedirs(
            meshs_dir,
            exist_ok=True
        )

        output_mesh = os.path.join(
            meshs_dir,
            f"{base_name}_3d.glb"
        )

        self.mesh.export(output_mesh)

        return output_mesh