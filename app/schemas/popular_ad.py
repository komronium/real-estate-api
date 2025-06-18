from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from app.schemas.ad import AdOut


class PopularAdBase(BaseModel):
    ad_id: int
    expires_at: Optional[datetime] = None


class PopularAdCreate(PopularAdBase):
    pass


class PopularAdOut(PopularAdBase):
    id: int
    ad: AdOut
    added_by: UUID
    added_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True
