from app.db.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class OTP(Base):
    __tablename__ = 'otp'
    
    code = Column(String(length=6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    user = relationship('User', back_populates='otps')
