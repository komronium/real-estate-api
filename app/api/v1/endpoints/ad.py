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
def create_ad(ad: AdCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AdService.create_ad(ad, current_user.id, db)


@router.get("/", response_model=List[AdOut])
def list_ads(
    category_id: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return AdService.get_all_ads(db, category_id=category_id, min_price=min_price, max_price=max_price)


@router.get("/{ad_id}", response_model=AdOut)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    return AdService.get_ad_by_id(ad_id, db)


@router.patch("/{ad_id}", response_model=AdOut)
def update_ad(
    ad_id: int,
    ad_update: AdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad = AdService.get_ad_by_id(ad_id, db)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return AdService.update_ad(ad_id, ad_update, db)


@router.patch("/{ad_id}/category", response_model=AdOut)
def update_ad_category(
    ad_id: int,
    category_update: AdCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad = AdService.get_ad_by_id(ad_id, db)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return AdService.update_ad_category(ad_id, category_update.category_id, db)


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(ad_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ad = AdService.get_ad_by_id(ad_id, db)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    AdService.delete_ad(ad_id, db)