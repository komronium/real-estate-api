from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.models.ad import Ad
from app.schemas.ad import AdCreate, AdUpdate


class AdService:
    @staticmethod
    def create_ad(ad_data: AdCreate, user_id: int, db: Session):
        new_ad = Ad(**ad_data.model_dump(), user_id=user_id)
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)
        return new_ad

    @staticmethod
    def get_all_ads(
            db: Session,
            category_id: Optional[int] = None,
            min_price: Optional[int] = None,
            max_price: Optional[int] = None
    ):
        query = db.query(Ad)

        if category_id is not None:
            query = query.filter(Ad.category_id == category_id)

        if min_price is not None:
            query = query.filter(Ad.price >= min_price)
        if max_price is not None:
            query = query.filter(Ad.price <= max_price)

        return query.all()

    @staticmethod
    def get_ad_by_id(ad_id: int, db: Session):
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        return ad

    @staticmethod
    def update_ad(ad_id: int, ad_data: AdUpdate, db: Session):
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad:
            for key, value in ad_data.model_dump().items():
                if value is not None:
                    setattr(ad, key, value)
            db.commit()
            db.refresh(ad)
        return ad

    @staticmethod
    def update_ad_category(ad_id: int, category_id: int, db: Session):
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        ad.category_id = category_id
        db.commit()
        db.refresh(ad)
        return ad

    @staticmethod
    def delete_ad(ad_id: int, db: Session):
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad:
            db.delete(ad)
            db.commit()