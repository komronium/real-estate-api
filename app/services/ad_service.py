from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.models.ad import Ad
from app.schemas.ad import AdCreate, AdUpdate


class AdService:

    def __init__(self, db: Session):
        self.db = db

    def get_all_ads(
        self,
        category_id: Optional[int] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None
    ):
        query = self.db.query(Ad)

        if category_id is not None:
            query = query.filter(Ad.category_id == category_id)

        if min_price is not None:
            query = query.filter(Ad.price >= min_price)
        if max_price is not None:
            query = query.filter(Ad.price <= max_price)

        return query.all()
    
    def get_ad_or_404(self, ad_id: int):
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        return ad

    def create_ad(self, ad_data: AdCreate, user_id: int):
        new_ad = Ad(**ad_data.model_dump(), user_id=user_id)
        self.db.add(new_ad)
        self.db.commit()
        self.db.refresh(new_ad)
        return new_ad

    def update_ad(self, ad_id: int, ad_data: AdUpdate):
        ad = self.get_ad_or_404(ad_id)
        for key, value in ad_data.model_dump().items():
            if value is not None:
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
