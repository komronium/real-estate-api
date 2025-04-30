from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class AdBase(BaseModel):
    title: str
    description: str = Field(..., min_length=40)
    image_url: Optional[str] = None
    full_name: str
    email: EmailStr
    phone_number: str
    price: Optional[int] = None
    latitude: float  = Field(..., ge=-90, le=90, examples=[12.345678])
    longitude: float = Field(..., ge=-180, le=180, examples=[-123.456789])

    @field_validator('latitude', 'longitude')
    def round_coordinates(cls, v):
        return round(float(v), 6)


class AdCreate(AdBase):
    pass


class AdUpdate(AdBase):
    description: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AdOut(AdBase):
    id: int
    user_id: UUID

    class Config:
        from_attributes = True
