import uuid

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdBase(BaseModel):
    id: int
    title: str
    description: str = Field(..., min_length=40)
    image_url: Optional[str]
    location: Optional[str]
    full_name: str
    email: EmailStr
    phone_number: str


class AdCreate(AdBase):
    pass


class AdUpdate(AdBase):
    pass


class AdOut(AdBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
