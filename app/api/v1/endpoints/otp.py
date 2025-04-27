from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import Token
from app.schemas.otp import OTPRequest, OTPVerify, OTPResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.otp_service import OTPService


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
    user, _ = await user_service.get_or_create_by_phone(request.phone_number)
    otp_service = OTPService(db)
    code = await otp_service.create_otp(request)

    # TODO: Integrate with SMS service
    print(f"OTP code: {code}")

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
    user = await user_service.get_by_phone(request.phone_number)
    await otp_service.verify_otp(request)
    return await auth_service.create_token(user)
