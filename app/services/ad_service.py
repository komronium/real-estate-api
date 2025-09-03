import uuid
import boto3
from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.models.ad import Ad, DealType
from app.schemas.ad import AdCreate, AdUpdate

from app.core.config import settings

# Constants
COORDINATE_CONVERSION_FACTOR = 111.0  # 1 degree ≈ 111 km
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


class AdService:

    def __init__(self, db: Session):
        self.db = db

    def _apply_search_filter(self, query, search_query: str):
        """Apply search filter to the query"""
        like_query = f"%{search_query}%"
        return query.filter(
            (Ad.title.ilike(like_query)) |
            (Ad.description.ilike(like_query)) |
            (Ad.city.ilike(like_query)) |
            (Ad.street.ilike(like_query))
        )

    def _apply_price_filter(self, query, min_price: Optional[int], max_price: Optional[int]):
        """Apply price filters to the query"""
        if min_price is not None:
            query = query.filter(Ad.price >= min_price)
        if max_price is not None:
            query = query.filter(Ad.price <= max_price)
        return query

    def _apply_location_filter(self, query, city: Optional[str]):
        """Apply city filter to the query"""
        if city is not None:
            query = query.filter(Ad.city.ilike(f"%{city}%"))
        return query

    def _apply_area_filter(self, query, min_area: Optional[float], max_area: Optional[float]):
        """Apply area filters to the query"""
        if min_area is not None:
            query = query.filter(Ad.total_area >= min_area)
        if max_area is not None:
            query = query.filter(Ad.total_area <= max_area)
        return query

    def get_all_ads(
            self,
            search_query: Optional[str] = None,
            category_id: Optional[int] = None,
            min_price: Optional[int] = None,
            max_price: Optional[int] = None,
            deal_type: Optional[DealType] = None,
            rooms_count: Optional[int] = None,
            city: Optional[str] = None,
            min_area: Optional[float] = None,
            max_area: Optional[float] = None,
    ) -> List[Ad]:
        """
        Get all ads with optional filtering
        
        Args:
            search_query: Text to search in title, description, city, or street
            category_id: Filter by category ID
            min_price: Minimum price filter
            max_price: Maximum price filter
            deal_type: Filter by deal type (sale/rent)
            rooms_count: Filter by number of rooms
            city: Filter by city name
            min_area: Minimum area filter
            max_area: Maximum area filter
            
        Returns:
            List of filtered ads
        """
        query = self.db.query(Ad)

        # Apply search filter if search query is provided
        if search_query:
            query = self._apply_search_filter(query, search_query)

        if category_id is not None:
            query = query.filter(Ad.category_id == category_id)

        query = self._apply_price_filter(query, min_price, max_price)

        if deal_type is not None:
            query = query.filter(Ad.deal_type == deal_type)

        if rooms_count is not None:
            query = query.filter(Ad.rooms_count == rooms_count)

        query = self._apply_location_filter(query, city)
        query = self._apply_area_filter(query, min_area, max_area)

        return query.all()

    def get_ads_by_user(self, user_id: int) -> List[Ad]:
        """Get all ads created by a specific user"""
        return self.db.query(Ad).filter(Ad.user_id == user_id).all()

    def get_ad_or_404(self, ad_id: int) -> Ad:
        """Get ad by ID or raise 404 if not found"""
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        return ad

    def create_ad(self, ad_data: AdCreate, user_id: int) -> Ad:
        """Create a new ad"""
        if not ad_data.category_id:
            raise HTTPException(status_code=400, detail="Category ID is required")

        new_ad = Ad(**ad_data.model_dump(), user_id=user_id)
        self.db.add(new_ad)
        self.db.commit()
        self.db.refresh(new_ad)
        return new_ad

    def update_ad(self, ad_id: int, ad_data: AdUpdate) -> Ad:
        """Update an existing ad"""
        ad = self.get_ad_or_404(ad_id)
        update_data = ad_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if hasattr(ad, key):
                setattr(ad, key, value)

        self.db.commit()
        self.db.refresh(ad)
        return ad

    def update_ad_category(self, ad_id: int, category_id: int) -> Ad:
        """Update the category of an ad"""
        ad = self.get_ad_or_404(ad_id)
        ad.category_id = category_id
        self.db.commit()
        self.db.refresh(ad)
        return ad

    def delete_ad(self, ad_id: int) -> None:
        """Delete an ad"""
        ad = self.get_ad_or_404(ad_id)
        self.db.delete(ad)
        self.db.commit()

    def add_images_to_ad(self, ad_id: int, image_urls: List[str]) -> Ad:
        """Add multiple images to an existing ad"""
        ad = self.get_ad_or_404(ad_id)

        if ad.image_urls is None:
            ad.image_urls = []

        ad.image_urls.extend(image_urls)
        self.db.commit()
        self.db.refresh(ad)
        return ad

    def remove_image_from_ad(self, ad_id: int, image_url: str) -> Ad:
        """Remove a specific image from an ad"""
        ad = self.get_ad_or_404(ad_id)

        if ad.image_urls and image_url in ad.image_urls:
            ad.image_urls.remove(image_url)
            self.db.commit()
            self.db.refresh(ad)

        return ad

    def get_ads_by_location(self, latitude: float, longitude: float, radius_km: float = 5.0) -> List[Ad]:
        """Get ads within a certain radius from given coordinates"""
        # Simple distance calculation (for more accurate results, use PostGIS)
        lat_diff = radius_km / COORDINATE_CONVERSION_FACTOR
        lng_diff = radius_km / (COORDINATE_CONVERSION_FACTOR * abs(latitude))

        query = self.db.query(Ad).filter(
            Ad.latitude.between(latitude - lat_diff, latitude + lat_diff),
            Ad.longitude.between(longitude - lng_diff, longitude + lng_diff)
        )

        return query.all()

    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="File must have a filename")
        
        file_extension = file.filename.lower().split(".")[-1]
        if f".{file_extension}" not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    async def upload_file(self, file: UploadFile) -> dict:
        """Upload file to S3 and return the URL"""
        self._validate_file(file)
        
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME
        )

        file_extension = file.filename.split(".")[-1]
        s3_file_name = f"{uuid.uuid4()}.{file_extension}"

        try:
            s3_client.upload_fileobj(
                file.file,
                settings.AWS_S3_BUCKET_NAME,
                s3_file_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            return {
                'url': f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{s3_file_name}"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")