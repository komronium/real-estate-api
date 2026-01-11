import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole

PHONE_REGEX = r'^\+998\d{9}$' # Uzbekistan phone number format


class OTPBase(BaseModel):
    phone_number: str = Field(..., pattern=PHONE_REGEX)


class OTPRequest(OTPBase):
    role: Optional[UserRole] = Field(UserRole.USER, description="User role: user or realtor")


class OTPVerify(OTPBase):
    code: str = Field(..., min_length=6, max_length=6, example='123456')
    role: Optional[UserRole] = Field(UserRole.USER, description="User role: user or realtor")


class OTPOut(OTPBase):
    id: int
    code: str
    expires_at: datetime.datetime
    used: bool

    model_config = ConfigDict(from_attributes=True)


class OTPResponse(BaseModel):
    message: str = Field(..., example='Code sent')
