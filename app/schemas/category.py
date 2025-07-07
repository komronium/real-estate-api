from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.models.category import LanguageEnum


class CategoryNameBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lang: LanguageEnum

    class Config:
        from_attributes = True



class CategoryBase(BaseModel):
    parent_id: Optional[int] = Field(gt=0)
    names: Dict[LanguageEnum, str]


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class CategoryWithChildren(CategoryOut):
    subcategories: List["CategoryWithChildren"] = []

    class Config:
        from_attributes = True


CategoryWithChildren.model_rebuild()


class AdCategoryUpdate(BaseModel):
    category_id: Optional[int] = None
