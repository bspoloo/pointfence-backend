from cv2.typing import MatLike
import cv2
from numpy.typing import NDArray
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
from app.core.config import SAM_CHECKPOINT, DEVICE

class SAMPredictor:
    predictor = None
    type: str
    def __init__(self):
        self.type = "vit_l"
    
    def set_up_model(self)->None:
        sam = sam_model_registry[self.type](checkpoint=SAM_CHECKPOINT)
        sam.to(DEVICE)
        self.predictor = SamPredictor(sam)

    def set_image(self, image: MatLike) -> None:
        image_rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )
        self.predictor.set_image(image_rgb)

    def predict_mask(self, input_points: NDArray[np.float64], input_labels: NDArray[np.float64]):
        masks, scores, logits = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=True
        )
        # return the best mask
        return masks[np.argmax(scores)]
