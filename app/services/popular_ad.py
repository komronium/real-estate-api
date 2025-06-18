from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ad import Ad
from app.models.popular_ad import PopularAd
from app.schemas.popular_ad import PopularAdCreate


class PopularAdService:
    def __init__(self, db: Session):
        self.db = db

    def create_popular_ad(self, data: PopularAdCreate, admin_id):
        ad = self.db.query(Ad).filter(Ad.id == data.ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        existing = self.db.query(PopularAd).filter(PopularAd.ad_id == data.ad_id, PopularAd.is_active == True).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ad is already popular")
        popular_ad = PopularAd(
            ad_id=data.ad_id,
            added_by=admin_id,
            expires_at=data.expires_at
        )
        self.db.add(popular_ad)
        self.db.commit()
        self.db.refresh(popular_ad)
        return popular_ad

    def remove_popular_ad(self, ad_id: int):
        popular_ad = self.db.query(PopularAd).filter(PopularAd.ad_id == ad_id, PopularAd.is_active == True).first()
        if not popular_ad:
            raise HTTPException(status_code=404, detail="Popular ad not found")
        popular_ad.is_active = False
        self.db.commit()

    def get_all_popular_ads(self):
        return self.db.query(PopularAd).filter(PopularAd.is_active == True).all()