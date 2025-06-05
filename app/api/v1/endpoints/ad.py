from fastapi import APIRouter, Depends, status, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.schemas.category import AdCategoryUpdate
from app.services.ad_service import AdService
from app.schemas.ad import AdCreate, AdOut, AdUpdate, DealType, UploadFileResponse
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
    deal_type: Optional[DealType] = None,
    rooms_count: Optional[int] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ad_service = AdService(db)
    return ad_service.get_all_ads(
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        deal_type=deal_type,
        rooms_count=rooms_count,
        city=city
    )


@router.get("/nearby", response_model=List[AdOut])
def get_nearby_ads(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5.0, ge=0.1, le=50),
    db: Session = Depends(get_db)
):
    ad_service = AdService(db)
    return ad_service.get_ads_by_location(latitude, longitude, radius_km)


@router.get('/mine', response_model=List[AdOut])
def get_my_ads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    return ad_service.get_ads_by_user(current_user.id)


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


@router.post("/{ad_id}/images", response_model=AdOut)
def add_images_to_ad(
    ad_id: int,
    image_urls: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.add_images_to_ad(ad_id, image_urls)


@router.delete("/{ad_id}/images", response_model=AdOut)
def remove_image_from_ad(
    ad_id: int,
    image_url: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.remove_image_from_ad(ad_id, image_url)


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


@router.post("/upload-image", response_model=UploadFileResponse,status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ad_service = AdService(db)
    return await ad_service.upload_file(file)
