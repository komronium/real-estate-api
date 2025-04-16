from pydantic import BaseModel


class Base64Dto(BaseModel):
    data: str
