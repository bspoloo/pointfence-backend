from pydantic import BaseModel, ConfigDict


class CreateFile(BaseModel):
    filename: str
    extension: str
    url: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class CreateObject(BaseModel):
    filename: str
    extension: str
    url: str
    image_mask_id: int
    model_config = ConfigDict(from_attributes=True)

class CreateModel(BaseModel):
    filename: str
    extension: str
    url: str
    object_id: int
    model_config = ConfigDict(from_attributes=True)


