from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean, Enum, UUID, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.db.base import Base
import enum
from datetime import datetime


class DealType(enum.Enum):
    sale = "sale"
    rent = "rent"


class ContactType(enum.Enum):
    realtor = "realtor"
    owner = "owner"


class GoldVerificationStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Ad(Base):
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Deal and property type
    deal_type = Column(Enum(DealType), nullable=False, default=DealType.sale)

    # Location
    city = Column(String, nullable=True)
    complex_name = Column(String, nullable=True)
    street = Column(String, nullable=True)
    house_number = Column(String, nullable=True)
    latitude = Column(Float(precision=8), nullable=False)
    longitude = Column(Float(precision=8), nullable=False)

    # Property characteristics - House/Building
    floors_in_building = Column(Integer, nullable=True)
    current_floor = Column(Integer, nullable=True)

    # Property characteristics - Apartment/Room details
    rooms_count = Column(Integer, nullable=True)
    bathrooms_count = Column(Integer, nullable=True)
    bedrooms_count = Column(Integer, nullable=True)

    # Areas (in square meters)
    total_area = Column(Float, nullable=True)
    living_area = Column(Float, nullable=True)
    kitchen_area = Column(Float, nullable=True)
    ceiling_height = Column(Float, nullable=True)

    # Images - storing as array of URLs
    image_urls = Column(ARRAY(String), nullable=True, default=[])

    # Price and terms
    price = Column(Integer, nullable=True)
    currency = Column(String, default="USD", nullable=False)
    commission_from_buyer = Column(Boolean, default=False)

    # Contact information
    contact_type = Column(Enum(ContactType), nullable=False, default=ContactType.realtor)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    # Verification fields
    is_gold_verified = Column(Boolean, default=False, nullable=False, comment="Gold verification status")
    gold_verification_status = Column(Enum(GoldVerificationStatus), default=GoldVerificationStatus.pending, nullable=False)
    gold_verification_requested_at = Column(DateTime(timezone=True), nullable=True)
    gold_verification_processed_at = Column(DateTime(timezone=True), nullable=True)
    gold_verification_comment = Column(Text, nullable=True, comment="Admin comment for gold verification")

    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    user = relationship("User", back_populates="ads")

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="ads")

    comments = relationship("Comment", back_populates="ad", cascade="all, delete")
    popular_ad = relationship("PopularAd", uselist=False, back_populates="ad")
    gold_verification_requests = relationship("GoldVerificationRequest", back_populates="ad", cascade="all, delete")


class GoldVerificationRequest(Base):
    """Model for tracking gold verification requests"""
    __tablename__ = "gold_verification_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ad.id"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    processed_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    
    status = Column(Enum(GoldVerificationStatus), default=GoldVerificationStatus.pending, nullable=False)
    request_reason = Column(Text, nullable=True, comment="User's reason for requesting gold verification")
    admin_comment = Column(Text, nullable=True, comment="Admin's comment on the request")
    
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    ad = relationship("Ad", back_populates="gold_verification_requests")
    requester = relationship("User", foreign_keys=[requested_by], back_populates="gold_verification_requests")
    processor = relationship("User", foreign_keys=[processed_by])
