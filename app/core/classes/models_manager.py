from app.core.models.MDE.mde import MDE
from app.core.models.MDE.depth_anything import DepthAnything_V2
from app.core.models.MDE.midasv3 import MidasV3
from app.core.models.MDE.adabins import AdaBins
from app.core.models.MDE.metric3d import Metric3D
from app.core.models.MDE.depth_pro import DepthPro

class ModelManagerMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class ModelManager(metaclass=ModelManagerMeta):
    models : dict[str, MDE]
    def __init__(self):
        self.models = {
            "depth_anything": DepthAnything_V2(),
            "midas": MidasV3(),
            "ada_bins": AdaBins(),
            "metric_3d": Metric3D(),
            "depth_pro": DepthPro(),
        }

    def get_mde(self, model_name : str)->MDE:
        model : MDE = self.models[model_name]
        if model is not None:
            return model
        else:
            print(f'model with name {model_name} not found!')
            return None