from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: int
    names: str
    email: str
    player_name: str

    model_config = ConfigDict(from_attributes=True)