from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl, model_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

from app.schemas.category import CategoryOut
from app.schemas.user import UserOut


class DealType(str, Enum):
    sale = "sale"
    rent = "rent"


class ContactType(str, Enum):
    REALTOR = "realtor"
    OWNER = "owner"


class GoldVerificationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class AdBase(BaseModel):
    # Basic information
    title: str
    description: Optional[str] = None

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
    """Schema for updating ads - only includes fields that can be updated"""
    title: Optional[str] = None
    description: Optional[str] = None
    deal_type: Optional[DealType] = None
    category_id: Optional[int] = None

    # Location
    city: Optional[str] = None
    complex_name: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

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
    user_id: Optional[UUID] = None
    category: CategoryOut
    
    # Computed fields - verification status from related data
    is_author_verified: bool = False
    is_gold_verified: bool = False
    gold_verification_status: Optional[GoldVerificationStatus] = None
    gold_verification_requested_at: Optional[datetime] = None
    gold_verification_processed_at: Optional[datetime] = None
    gold_verification_comment: Optional[str] = None

    @model_validator(mode='after')
    def compute_verification_status(self):
        """Compute verification status from user and gold verification requests"""
        # Author verification from user
        if hasattr(self, 'user') and self.user:
            self.is_author_verified = self.user.is_verified
        
        # Gold verification from latest request
        if hasattr(self, 'gold_verification_requests') and self.gold_verification_requests:
            # Get the latest gold verification request
            latest_request = max(self.gold_verification_requests, key=lambda x: x.requested_at)
            self.is_gold_verified = latest_request.status == GoldVerificationStatus.approved
            self.gold_verification_status = latest_request.status
            self.gold_verification_requested_at = latest_request.requested_at
            self.gold_verification_processed_at = latest_request.processed_at
            self.gold_verification_comment = latest_request.admin_comment
        
        return self

    class Config:
        from_attributes = True


class UploadFileResponse(BaseModel):
    url: HttpUrl

    class Config:
        from_attributes = True


class GoldVerificationRequestBase(BaseModel):
    request_reason: Optional[str] = None


class GoldVerificationRequestCreate(GoldVerificationRequestBase):
    ad_id: int


class GoldVerificationRequestUpdate(BaseModel):
    status: GoldVerificationStatus
    admin_comment: Optional[str] = None


class GoldVerificationRequestOut(GoldVerificationRequestBase):
    id: int
    ad_id: int
    # Map to ORM relationship 'requester' and 'processor' to expose full users
    requested_by: UserOut = Field(..., validation_alias='requester')
    processed_by: Optional[UserOut] = Field(None, validation_alias='processor')
    status: GoldVerificationStatus
    admin_comment: Optional[str] = None
    requested_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
