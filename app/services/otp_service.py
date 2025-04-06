import random
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import create_access_token
from app.core.config import settings
from app.models.otp import OTP
from app.schemas.auth import Token
from app.schemas.otp import OTPRequest, OTPVerify


class OTPService:

    @staticmethod
    def _generate_code() -> str:
        return ''.join(random.choices('0123456789', k=settings.OTP_LENGTH))
        
    @staticmethod
    async def create_otp(request: OTPRequest, db: Session) -> str:
        existing_otps = db.query(OTP).filter(OTP.phone_number == request.phone_number)
        existing_otps.delete()

        code = OTPService._generate_code()
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        otp = OTP(
            phone_number=request.phone_number,
            code=code,
            expires_at=expires_at
        )
        db.add(otp)
        db.commit()
        return code

    @staticmethod
    async def verify_otp(request: OTPVerify, db: Session) -> None:
        otp = db.query(OTP).filter(
            OTP.phone_number == request.phone_number,
            OTP.code == request.code,
            OTP.expires_at > datetime.datetime.now(),
            OTP.used == False
        ).first()

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid or expired OTP code'
            )
        otp.used = True
        db.commit()
    
    @staticmethod
    async def create_token(user) -> Token:
        access_token = create_access_token({'sub': str(user.id)})
        return Token(access_token=access_token)
    