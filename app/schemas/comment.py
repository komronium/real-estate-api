from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserOut

class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class CommentCreate(CommentBase):
    pass


class CommentOut(CommentBase):
    id: int
    ad_id: int
    user: UserOut
    created_at: datetime

    class Config:
        from_attributes = True
