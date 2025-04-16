import uuid

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AdBase(BaseModel):
    title: str
    description: str = Field(..., min_length=40)
    image_url: Optional[str] = None
    location: Optional[str] = None
    full_name: str
    email: EmailStr
    phone_number: str


class AdCreate(AdBase):
    pass


class AdUpdate(AdBase):
    description: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class AdOut(AdBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
