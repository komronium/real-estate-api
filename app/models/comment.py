from sqlalchemy import UUID, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Comment(Base):
    text = Column(Text, nullable=False)
    ad_id = Column(Integer, ForeignKey("ad.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    ad = relationship("Ad", back_populates="comments")
    user = relationship("User")
