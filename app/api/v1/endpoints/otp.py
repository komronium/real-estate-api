from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import Token
from app.schemas.otp import OTPRequest, OTPVerify, OTPResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.otp_service import OTPService
from app.utils.sms import send_sms


router = APIRouter(
    prefix='/api/v1/auth/otp',
    tags=['Authentication']
)


@router.post(
    '/request',
    response_model=OTPResponse,
    status_code=200,
)
async def request_otp(
    request: OTPRequest,
    db: Session = Depends(get_db),
) -> OTPResponse:
    user_service = UserService(db)
    otp_service = OTPService(db)

    user, _ = await user_service.get_or_create_by_phone(request.phone_number, request.role)
    code = await otp_service.create_otp(user)

    await send_sms(request.phone_number, code)
    return OTPResponse(message="Code sent")


@router.post(
    '/login',
    response_model=Token,
    status_code=200,
    responses={
        400: {'description': 'Invalid or expired OTP code'}
    }
)
async def login_with_otp(
    request: OTPVerify,
    db: Session = Depends(get_db),
) -> Token:
    user_service = UserService(db)
    otp_service = OTPService(db)
    auth_service = AuthService(db)
    
    # Get or create user with role
    user, _ = await user_service.get_or_create_by_phone(request.phone_number, request.role)
    await otp_service.verify_otp(user, request)
    return auth_service.generate_tokens(user)
