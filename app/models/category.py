from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Category(Base):
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)

    # Relationships
    parent = relationship("Category", remote_side="Category.id", backref="subcategories")
    ads = relationship("Ad", back_populates="category")
