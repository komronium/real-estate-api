from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Dict

from app.models.category import LanguageEnum


class CategoryBase(BaseModel):
    parent_id: Optional[int] = Field(gt=0)
    names: Dict[LanguageEnum, str]

    @field_serializer('names', mode='plain')
    def get_names(self, names):
        return {t.lang: t.name for t in names}


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
