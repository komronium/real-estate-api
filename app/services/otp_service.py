import random
import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.otp import OTP
from app.schemas.otp import OTPRequest, OTPVerify


class OTPService:

    def __init__(self, db: Session):
        self.db = db

    def _generate_code(self) -> str:
        return ''.join(random.choices('0123456789', k=settings.OTP_LENGTH))
        
    async def create_otp(self, request: OTPRequest) -> str:
        existing_otps = self.db.query(OTP).filter(OTP.phone_number == request.phone_number)
        existing_otps.delete()

        code = self._generate_code()
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        otp = OTP(
            phone_number=request.phone_number,
            code=code,
            expires_at=expires_at
        )
        self.db.add(otp)
        self.db.commit()
        return otp.code

    async def verify_otp(self, request: OTPVerify) -> None:
        otp = self.db.query(OTP).filter(
            OTP.phone_number == request.phone_number,
            OTP.code == request.code,
            OTP.expires_at > datetime.datetime.now(),
            OTP.used == False
        ).first()

        if not otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid or expired OTP code')
        
        otp.used = True
        self.db.commit()
