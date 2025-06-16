from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl
from typing import Optional, List
from enum import Enum

from app.schemas.category import CategoryOut


class DealType(str, Enum):
    sale = "sale"
    rent = "rent"


class ContactType(str, Enum):
    REALTOR = "realtor"
    OWNER = "owner"


class AdBase(BaseModel):
    # Basic information
    title: str
    description: str = Field(..., min_length=40)

    # Deal and property type
    deal_type: DealType = DealType.sale
    category_id: int

    # Location
    city: Optional[str] = None
    complex_name: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90, examples=[41.33575242335])
    longitude: float = Field(..., ge=-180, le=180, examples=[69.21214325235])

    # Property characteristics
    floors_in_building: Optional[int] = None
    current_floor: Optional[int] = None
    rooms_count: Optional[int] = None
    bathrooms_count: Optional[int] = None
    bedrooms_count: Optional[int] = None

    # Areas
    total_area: Optional[float] = None
    living_area: Optional[float] = None
    kitchen_area: Optional[float] = None
    ceiling_height: Optional[float] = None

    # Images
    image_urls: Optional[List[str]] = []

    # Price and terms
    price: Optional[int] = None
    currency: str = "USD"
    commission_from_buyer: bool = False

    # Contact information
    contact_type: ContactType = ContactType.REALTOR
    full_name: str
    email: EmailStr
    phone_number: str

    @field_validator('latitude', 'longitude')
    def round_coordinates(cls, v):
        return round(float(v), 10)

    @field_validator('total_area', 'living_area', 'kitchen_area', 'ceiling_height')
    def round_areas(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v


class AdCreate(AdBase):
    pass


class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deal_type: Optional[DealType] = None

    # Location
    city: Optional[str] = None
    complex_name: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Property characteristics
    floors_in_building: Optional[int] = None
    current_floor: Optional[int] = None
    rooms_count: Optional[int] = None
    bathrooms_count: Optional[int] = None
    bedrooms_count: Optional[int] = None

    # Areas
    total_area: Optional[float] = None
    living_area: Optional[float] = None
    kitchen_area: Optional[float] = None
    ceiling_height: Optional[float] = None

    # Images
    image_urls: Optional[List[str]] = None

    # Price and terms
    price: Optional[int] = None
    currency: Optional[str] = None
    commission_from_buyer: Optional[bool] = None

    # Contact information
    contact_type: Optional[ContactType] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    @field_validator('latitude', 'longitude')
    def round_coordinates(cls, v):
        if v is not None:
            return round(float(v), 6)
        return v

    @field_validator('total_area', 'living_area', 'kitchen_area', 'ceiling_height')
    def round_areas(cls, v):
        if v is not None:
            return round(float(v), 2)
        return v


class AdOut(AdBase):
    id: int
    user_id: UUID
    category: CategoryOut

    class Config:
        from_attributes = True


class UploadFileResponse(BaseModel):
    url: HttpUrl

    class Config:
        from_attributes = True
