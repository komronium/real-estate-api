from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.schemas.category import AdCategoryUpdate
from app.services.ad_service import AdService
from app.schemas.ad import AdCreate, AdOut, AdUpdate
from app.models.user import User

router = APIRouter(prefix="/api/v1/ads", tags=["Ads"])


@router.post("/", response_model=AdOut, status_code=status.HTTP_201_CREATED)
def create_ad(
    ad_data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    return ad_service.create_ad(ad_data, current_user.id)


@router.get("/", response_model=List[AdOut])
def list_ads(
    category_id: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    ad_service = AdService(db)
    return ad_service.get_all_ads(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price
    )


@router.get("/{ad_id}", response_model=AdOut)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    ad_service = AdService(db)
    return ad_service.get_ad_or_404(ad_id)


@router.patch("/{ad_id}", response_model=AdOut)
def update_ad(
    ad_id: int,
    ad_update: AdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.update_ad(ad_id, ad_update)


@router.patch("/{ad_id}/category", response_model=AdOut)
def update_ad_category(
    ad_id: int,
    category_update: AdCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.update_ad_category(ad_id, category_update.category_id)


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(
    ad_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    ad_service.delete_ad(ad_id)
