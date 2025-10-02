# Import all models to ensure SQLAlchemy can resolve relationships
# Import order matters - import base models first, then dependent models

# Base models (no dependencies)
from app.models.category import Category, CategoryName, LanguageEnum

# Models that depend on base models
from app.models.user import User, UserRole
from app.models.ad import Ad, DealType, ContactType
from app.models.comment import Comment
from app.models.otp import OTP
from app.models.popular_ad import PopularAd
from app.models.favourite import Favourite

# This ensures all models are imported and available when SQLAlchemy initializes
__all__ = [
    "Category",
    "CategoryName", 
    "LanguageEnum",
    "User",
    "UserRole", 
    "Ad",
    "DealType",
    "ContactType",
    "Comment",
    "OTP",
    "PopularAd",
    "Favourite"
]
