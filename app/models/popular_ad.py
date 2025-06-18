from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

class PopularAd(Base):
    __tablename__ = "popular_ads"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ad.id"), unique=True, nullable=False)
    added_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    ad = relationship("Ad", back_populates="popular_ad")
    admin = relationship("User")