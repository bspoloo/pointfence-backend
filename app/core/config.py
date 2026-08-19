# route_original = r"./dataset_oficial"
import torch
from pathlib import Path
import sys

# SAM CONFIGURATION
SAM_MODEL_NAME = "SAM_MASKS"
MODEL_TYPE = "vit_l"
DEVICE = torch.device("cuda" if torch.cuda.is_available else "cpu")
UPLOAD_DIR = "uploads"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SAM_CHECKPOINT = BASE_DIR / "checkpoints" / "SAM" / "sam_vit_l_0b3195.pth"
HUNYAN_CHECKPOINT = BASE_DIR / "checkpoints" / "hunyuan3d-dit-v2-mini-turbo"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"

HY3DGEN_PATH = Path(__file__).resolve().parent.parent / "core" / "models" / "hunyuan3d_2"
sys.path.insert(0, str(HY3DGEN_PATH))