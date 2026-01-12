import uuid
from enum import Enum

from sqlalchemy import UUID, Boolean, Column, Date, DateTime, ForeignKey, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, Enum):
    USER = "user"
    REALTOR = "realtor"
    LEGAL = "legal"
    ADMIN = "admin"


class OneIDInfo(Base):
    """One ID (Yagona identifikatsiya tizimi) ma'lumotlari"""

    __tablename__ = "one_id_info"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), unique=True, nullable=False
    )

    # One ID asosiy ma'lumotlari
    pin = Column(
        String(length=14),
        unique=True,
        nullable=False,
        comment="Personal identification number (JShShIR)",
    )
    one_id_user_id = Column(
        String(length=255),
        unique=True,
        nullable=False,
        comment="One ID user identifier",
    )
    one_id_session_id = Column(
        String(length=255), nullable=True, comment="One ID session identifier"
    )

    # Shaxsiy ma'lumotlar
    full_name = Column(
        String(length=255), nullable=False, comment="Full name from One ID"
    )
    first_name = Column(
        String(length=255), nullable=False, comment="First name from One ID"
    )
    last_name = Column(
        String(length=255), nullable=False, comment="Last name from One ID"
    )
    middle_name = Column(
        String(length=255),
        nullable=False,
        comment="Middle name (father's name) from One ID",
    )
    passport_number = Column(
        String(length=20), nullable=False, comment="Passport number from One ID"
    )
    birth_date = Column(Date, nullable=False, comment="Birth date from One ID")
    user_type = Column(
        String(length=1), nullable=False, comment="User type (I-Individual, L-Legal)"
    )

    # Tasdiqlash ma'lumotlari
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="User verification status from One ID",
    )
    validation_method = Column(
        String(length=255), nullable=True, comment="Verification methods used"
    )
    auth_method = Column(
        String(length=20), nullable=True, comment="Authentication method"
    )

    # Yuridik shaxs ma'lumotlari (agar bo'lsa)
    pkcs_legal_tin = Column(
        String(length=9), nullable=True, comment="Legal entity TIN for PKCS auth"
    )

    # Vaqt belgilari
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    user = relationship("User", back_populates="one_id_info")


class User(Base):
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name = Column(String(length=128), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(
        String(length=16),
        SQLAlchemyEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )
    username = Column(String(length=64), unique=True, nullable=True)

    phone_number = Column(String(length=16), unique=True, nullable=True)
    password = Column(String(length=64), nullable=True)
    is_verified = Column(
        Boolean, default=False, nullable=False, comment="User verification status"
    )

    # Realtor fields
    avatar = Column(String, nullable=True, comment="S3 URL for user avatar")
    company_name = Column(
        String(length=255), nullable=True, comment="Company name for realtors"
    )

    ads = relationship("Ad", back_populates="user")
    otps = relationship("OTP", back_populates="user")
    comments = relationship("Comment", back_populates="user", cascade="all, delete")
    popular_ads = relationship("PopularAd", back_populates="admin")
    gold_verification_requests = relationship(
        "GoldVerificationRequest",
        foreign_keys="GoldVerificationRequest.requested_by",
        back_populates="requester",
    )
    favourites = relationship("Favourite", back_populates="user", cascade="all, delete")

    # One ID relationship
    one_id_info = relationship("OneIDInfo", back_populates="user", uselist=False)
