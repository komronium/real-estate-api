import uuid
from enum import Enum
from sqlalchemy import Column, UUID, String, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, Enum):
    USER = 'user'
    LEGAL = 'legal'
    ADMIN = 'admin'


class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(length=128), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String(length=5), SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=False)
    username = Column(String(length=64), unique=True, nullable=True)

    phone_number = Column(String(length=16), unique=True, nullable=True)
    password = Column(String(length=64), nullable=True)
    # e-signature fields here

    ads = relationship('Ad', back_populates='user')
    otps = relationship('OTP', back_populates='user')
    comments = relationship("Comment", back_populates="user", cascade="all, delete")
    popular_ads = relationship("PopularAd", back_populates="admin")
