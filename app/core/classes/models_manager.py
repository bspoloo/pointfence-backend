from app.core.models.MDE.mde import MDE
from app.core.models.MDE.depth_anything import DepthAnything_V2

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
        }

    def get_mde(self, model_name : str)->MDE:
        model : MDE = self.models[model_name]
        if model is not None:
            return model
        else:
            print(f'model with name {model_name} not found!')
            return None