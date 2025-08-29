from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.services.category_service import CategoryService
from app.services.ad_service import AdService
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate, CategoryWithChildren
from app.schemas.ad import AdOut
from app.models.user import User

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
        category: CategoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return CategoryService.create_category(category, current_user, db)


@router.post("/{category_id}/icon", response_model=CategoryOut)
async def upload_category_icon(
        category_id: int,
        icon: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Upload icon for a category
    """
    return await CategoryService.upload_category_icon(category_id, icon, current_user, db)


@router.delete("/{category_id}/icon")
async def delete_category_icon(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Delete icon for a category
    """
    return await CategoryService.delete_category_icon(category_id, current_user, db)


@router.get("/", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return CategoryService.get_all_categories(db)


@router.get("/root", response_model=List[CategoryWithChildren])
def list_root_categories(db: Session = Depends(get_db)):
    return CategoryService.get_root_categories(db)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return CategoryService.get_category_by_id(category_id, db)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
        category_id: int,
        category_update: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return CategoryService.update_category(category_id, category_update, current_user, db)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    CategoryService.delete_category(category_id, current_user, db)


@router.get("/{category_id}/ads", response_model=List[AdOut])
def list_ads_by_category(
        category_id: int,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        db: Session = Depends(get_db)
):
    CategoryService.get_category_by_id(category_id, db)
    ad_service = AdService(db)
    return ad_service.get_all_ads(
        category_id=category_id, 
        min_price=min_price, 
        max_price=max_price
    )
