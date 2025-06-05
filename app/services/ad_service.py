import uuid
import boto3
from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.ad import Ad, DealType, ContactType
from app.schemas.ad import AdCreate, AdUpdate

from app.core.config import settings


class AdService:

    def __init__(self, db: Session):
        self.db = db

    def get_all_ads(
            self,
            category_id: Optional[int] = None,
            min_price: Optional[int] = None,
            max_price: Optional[int] = None,
            deal_type: Optional[DealType] = None,
            rooms_count: Optional[int] = None,
            city: Optional[str] = None
    ):
        query = self.db.query(Ad)

        if category_id is not None:
            query = query.filter(Ad.category_id == category_id)

        if min_price is not None:
            query = query.filter(Ad.price >= min_price)
        if max_price is not None:
            query = query.filter(Ad.price <= max_price)

        if deal_type is not None:
            query = query.filter(Ad.deal_type == deal_type)

        if rooms_count is not None:
            query = query.filter(Ad.rooms_count == rooms_count)

        if city is not None:
            query = query.filter(Ad.city.ilike(f"%{city}%"))

        return query.all()
    
    def get_ads_by_user(self, user_id: int):
        """Get all ads created by a specific user"""
        return self.db.query(Ad).filter(Ad.user_id == user_id).all()

    def get_ad_or_404(self, ad_id: int):
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        return ad

    def create_ad(self, ad_data: AdCreate, user_id: int):
        category_id = ad_data.category_id
        if not category_id:
            raise HTTPException(status_code=400, detail="Category ID is required")
        
        new_ad = Ad(**ad_data.model_dump(), user_id=user_id)
        self.db.add(new_ad)
        self.db.commit()
        self.db.refresh(new_ad)
        return new_ad

    def update_ad(self, ad_id: int, ad_data: AdUpdate):
        ad = self.get_ad_or_404(ad_id)
        update_data = ad_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if hasattr(ad, key):
                setattr(ad, key, value)

        self.db.commit()
        self.db.refresh(ad)
        return ad

    def update_ad_category(self, ad_id: int, category_id: int):
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        ad.category_id = category_id
        self.db.commit()
        self.db.refresh(ad)
        return ad

    def delete_ad(self, ad_id: int):
        ad = self.get_ad_or_404(ad_id)
        self.db.delete(ad)
        self.db.commit()

    def add_images_to_ad(self, ad_id: int, image_urls: List[str]):
        """Add multiple images to an existing ad"""
        ad = self.get_ad_or_404(ad_id)

        if ad.image_urls is None:
            ad.image_urls = []

        ad.image_urls.extend(image_urls)
        self.db.commit()
        self.db.refresh(ad)
        return ad

    def remove_image_from_ad(self, ad_id: int, image_url: str):
        """Remove a specific image from an ad"""
        ad = self.get_ad_or_404(ad_id)

        if ad.image_urls and image_url in ad.image_urls:
            ad.image_urls.remove(image_url)
            self.db.commit()
            self.db.refresh(ad)

        return ad

    def get_ads_by_location(self, latitude: float, longitude: float, radius_km: float = 5.0):
        """Get ads within a certain radius from given coordinates"""
        # Simple distance calculation (for more accurate results, use PostGIS)
        lat_diff = radius_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
        lng_diff = radius_km / (111.0 * abs(latitude))

        query = self.db.query(Ad).filter(
            Ad.latitude.between(latitude - lat_diff, latitude + lat_diff),
            Ad.longitude.between(longitude - lng_diff, longitude + lng_diff)
        )

        return query.all()
    
    async def upload_file(self, file: UploadFile = File(...)):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )

        file_extension = file.filename.split(".")[-1]
        s3_file_name = f"{uuid.uuid4()}.{file_extension}"


        s3_client.upload_fileobj(
            file.file,
            settings.AWS_S3_BUCKET_NAME,
            s3_file_name,
            ExtraArgs={'ACL': 'public-read'}
        )
        return {
            'url':f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{s3_file_name}"
        }
