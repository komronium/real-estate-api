from pydantic import BaseModel
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


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


 # for recursive Pydantic model (: Kamron
CategoryWithChildren.model_rebuild()


class AdCategoryUpdate(BaseModel):
    category_id: Optional[int] = None