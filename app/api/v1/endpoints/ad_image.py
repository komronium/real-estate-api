from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.ad import AdOut, UploadFileResponse
from app.services.ad_service import AdService

router = APIRouter(prefix="/api/v1/ads", tags=["Ad Images"])


@router.post("/{ad_id}/images", response_model=AdOut)
def add_images_to_ad(
    ad_id: int,
    image_urls: List[str],
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.remove_image_from_ad(ad_id, image_url)


@router.post("/{ad_id}/documents", response_model=AdOut)
def add_documents_to_ad(
    ad_id: int,
    document_urls: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.add_documents_to_ad(ad_id, document_urls)


@router.delete("/{ad_id}/documents", response_model=AdOut)
def remove_document_from_ad(
    ad_id: int,
    document_url: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ad_service = AdService(db)
    ad = ad_service.get_ad_or_404(ad_id)
    if ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ad_service.remove_document_from_ad(ad_id, document_url)


@router.post(
    "/upload-image",
    response_model=UploadFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ad_service = AdService(db)
    return await ad_service.upload_file(file)


@router.post(
    "/upload-document",
    response_model=UploadFileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ad_service = AdService(db)
    return await ad_service.upload_file(file)
