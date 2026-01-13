import random
from datetime import datetime, timedelta
from string import digits

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.otp import OTP
from app.models.user import User
from app.schemas.otp import OTPVerify


class OTPService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_code(self) -> str:
        return "".join(random.choices(digits, k=settings.OTP_LENGTH))

    async def create_otp(self, user: User) -> str:
        self.db.query(OTP).filter(
            OTP.user_id == user.id, OTP.used == False, OTP.expires_at > datetime.now()
        ).update({OTP.used: True})

        code = self._generate_code()
        expires_at = datetime.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        otp = OTP(user_id=user.id, code=code, expires_at=expires_at)
        self.db.add(otp)
        self.db.commit()
        print(f"OTP created for user {user.id}: {code}")
        return otp.code

    async def verify_otp(self, user: User, request: OTPVerify) -> None:
        otp = (
            self.db.query(OTP)
            .filter(
                OTP.user_id == user.id,
                OTP.code == request.code,
                OTP.expires_at > datetime.now(),
                OTP.used == False,
            )
            .first()
        )

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP code",
            )

        otp.used = True
        self.db.commit()
