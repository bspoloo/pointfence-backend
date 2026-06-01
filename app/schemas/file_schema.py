from pydantic import BaseModel

class FileSchema(BaseModel):
    name: str
    content: str