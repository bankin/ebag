from pydantic import BaseModel, ConfigDict


class ImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    url: str
