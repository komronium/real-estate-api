from sqlalchemy.orm import Session

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
    def get_all_ads(db: Session):
        return db.query(Ad).all()

    @staticmethod
    def get_ad_by_id(ad_id: int, db: Session):
        return db.query(Ad).filter(Ad.id == ad_id).first()

    @staticmethod
    def update_ad(ad_id: int, ad_data: AdUpdate, db: Session):
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad:
            for key, value in ad_data.model_dump().items():
                setattr(ad, key, value)
            db.commit()
            db.refresh(ad)
        return ad

    @staticmethod
    def delete_ad(ad_id: int, db: Session):
        ad = db.query(Ad).filter(Ad.id == ad_id).first()
        if ad:
            db.delete(ad)
            db.commit()
