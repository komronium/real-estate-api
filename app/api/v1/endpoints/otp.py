from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import Token
from app.schemas.otp import OTPRequest, OTPVerify, OTPResponse
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
    user, _ = await UserService.get_or_create_by_phone(request.phone_number, db)
    code = await OTPService.create_otp(request, db)

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
    user = await UserService.get_by_phone(request.phone_number, db) 
    await OTPService.verify_otp(request, db)   
    return await OTPService.create_token(user)
