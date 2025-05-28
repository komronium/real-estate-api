from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base
import enum


class DealType(enum.Enum):
    SALE = "sale"
    RENT = "rent"


class PropertyType(enum.Enum):
    YER_UCHASTKASI = "yer_uchastkasi"
    HOVLI = "hovli"
    XONADON = "xonadon"
    NOTURAR = "noturar"
    SANOAT = "sanoat"


class ContactType(enum.Enum):
    REALTOR = "realtor"
    OWNER = "owner"


class Ad(Base):
    # Basic information
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Deal and property type
    deal_type = Column(Enum(DealType), nullable=False, default=DealType.SALE)
    property_type = Column(Enum(PropertyType), nullable=False)

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
    contact_type = Column(Enum(ContactType), nullable=False, default=ContactType.REALTOR)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    # Relationships
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="ads")

    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    category = relationship("Category", back_populates="ads")
