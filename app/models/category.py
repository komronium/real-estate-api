from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum

from app.db.base import Base


class LanguageEnum(str, Enum):
    uz = "uz"
    ru = "ru"
    en = "en"


class Category(Base):
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    icon = Column(String, nullable=True, default=None)

    # Relationships
    parent = relationship("Category", remote_side="Category.id", backref="subcategories")
    ads = relationship("Ad", back_populates="category")
    names = relationship("CategoryName", back_populates="category", cascade="all, delete-orphan")


class CategoryName(Base):
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String, nullable=False)
    lang = Column(String, nullable=False, default=LanguageEnum.uz.value)

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="names")
