import re
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, UUID4

from app.models.user import UserRole


class UserBase(BaseModel):
    name: Optional[str] = None


class UserAdminCreate(UserBase):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, value: str):
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must include at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must include at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must include at least one digit')
        if not re.search(r'[!@#$%^&*(),.?\':{}|<>]', value):
            raise ValueError('Password must include at least one special character')
        return value


class UserUpdate(BaseModel):
    name: Optional[str] = None


class UserOut(UserBase):
    id: UUID
    role: UserRole 
    phone_number: Optional[str] = None
    username: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
