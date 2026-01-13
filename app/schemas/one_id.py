from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class OneIDLegalInfo(BaseModel):
    """Legal entity information from One ID"""

    is_basic: bool = Field(..., description="Is this the primary legal entity")
    tin: str = Field(..., description="Tax identification number", max_length=9)
    le_tin: Optional[str] = Field(None, description="Legal entity TIN")
    acron_UZ: str = Field(..., description="Legal entity name in Uzbek")
    le_name: Optional[str] = Field(None, description="Legal entity full name")


class OneIDUserInfo(BaseModel):
    """User information from One ID system"""

    valid: bool = Field(..., description="Is user verified")
    validation_method: Optional[List[str]] = Field(
        None, description="Verification methods used"
    )
    pin: str = Field(..., description="Personal identification number", max_length=14)
    user_id: str = Field(..., description="One ID user identifier", max_length=255)
    full_name: str = Field(..., description="Full name", max_length=255)
    pport_no: str = Field(..., description="Passport number", max_length=20)
    birth_date: str = Field(..., description="Birth date in yyyy-MM-dd format")
    sur_name: str = Field(..., description="Surname", max_length=255)
    first_name: str = Field(..., description="First name", max_length=255)
    mid_name: str = Field(
        ..., description="Middle name (father's name)", max_length=255
    )
    user_type: str = Field(
        ..., description="User type (I-Individual, L-Legal)", max_length=1
    )
    sess_id: str = Field(..., description="Session ID (UUID)")
    ret_cd: str = Field(
        ..., description="Return code (0-success, 1-failure)", max_length=1
    )
    auth_method: str = Field(..., description="Authentication method", max_length=20)
    pkcs_legal_tin: Optional[str] = Field(
        None, description="Legal entity TIN for PKCS auth", max_length=9
    )
    legal_info: Optional[List[OneIDLegalInfo]] = Field(
        None, description="Legal entity information"
    )


class OneIDTokenResponse(BaseModel):
    """Token response from One ID OAuth2"""

    scope: str = Field(..., description="OAuth scope")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(..., description="Token type (bearer)")
    refresh_token: str = Field(..., description="Refresh token")
    access_token: str = Field(..., description="Access token")


class OneIDCodeRequest(BaseModel):
    """One ID authorization code request"""

    code: str = Field(..., description="Authorization code from One ID")


class OneIDInfoResponse(BaseModel):
    """One ID information response"""

    id: UUID = Field(..., description="One ID info ID")
    pin: str = Field(..., description="Personal identification number")
    one_id_user_id: str = Field(..., description="One ID user identifier")
    one_id_session_id: Optional[str] = Field(
        None, description="One ID session identifier"
    )
    full_name: str = Field(..., description="Full name")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    middle_name: str = Field(..., description="Middle name")
    passport_number: str = Field(..., description="Passport number")
    birth_date: date = Field(..., description="Birth date")
    user_type: str = Field(..., description="User type")
    is_verified: bool = Field(..., description="Verification status")
    validation_method: Optional[str] = Field(None, description="Validation methods")
    auth_method: Optional[str] = Field(None, description="Authentication method")
    pkcs_legal_tin: Optional[str] = Field(None, description="Legal entity TIN")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    class Config:
        from_attributes = True


class UserWithOneIDResponse(UserOut):
    one_id_info: Optional[OneIDInfoResponse] = Field(
        None, description="One ID information"
    )

    class Config:
        from_attributes = True
