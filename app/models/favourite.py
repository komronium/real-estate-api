from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class Favourite(Base):
    __tablename__ = "favourite"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    ad_id = Column(Integer, ForeignKey("ad.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="favourites")
    ad = relationship("Ad", back_populates="favourited_by")

    __table_args__ = (
        UniqueConstraint("user_id", "ad_id", name="uq_favourite_user_ad"),
    )


