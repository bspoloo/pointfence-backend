# route_original = r"./dataset_oficial"
import torch
from pathlib import Path

# SAM CONFIGURATION
SAM_MODEL_NAME = "SAM_MASKS"
SAM_CHECKPOINT = r"../../checkpoints/SAM/sam_vit_l_0b3195.pth"
MODEL_TYPE = "vit_l"
DEVICE = torch.device("cuda" if torch.cuda.is_available else "cpu")
UPLOAD_DIR = "uploads"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SAM_CHECKPOINT = BASE_DIR / "checkpoints" / "SAM" / "sam_vit_l_0b3195.pth"