from pydantic import BaseModel, Field, field_serializer, model_serializer
from typing import Optional, List, Dict

from app.models.category import LanguageEnum


class CategoryBase(BaseModel):
    parent_id: Optional[int] = Field(gt=0)
    names: Dict[LanguageEnum, str]

    @field_serializer('names', mode='plain')
    def get_names(self, names):
        return {lang.value: name for lang, name in names.items()}

    @model_serializer(mode='wrap')
    def serialize_category(self):
        return {
            "parent_id": self.parent_id,
            "names": {lang.value: name for lang, name in self.names.items()}
        }


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
