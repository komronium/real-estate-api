from app.db.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, Enum


class OTP(Base):
    phone_number = Column(String(length=16), unique=True, nullable=False)
    code = Column(String(length=6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
