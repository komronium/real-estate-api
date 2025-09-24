from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exists

from app.models.ad import Ad, GoldVerificationRequest, GoldVerificationStatus
from app.schemas.popular_ad import PopularAdCreate


class PopularAdService:
    def __init__(self, db: Session):
        self.db = db

    def create_popular_ad(self, data: PopularAdCreate, admin_id):
        # Deprecated: popularity is derived from gold verification now
        ad = self.db.query(Ad).filter(Ad.id == data.ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        has_approved = self.db.query(
            exists().where(
                (GoldVerificationRequest.ad_id == data.ad_id) &
                (GoldVerificationRequest.status == GoldVerificationStatus.approved)
            )
        ).scalar()
        if not has_approved:
            raise HTTPException(status_code=400, detail="Ad is not gold verified")
        return ad

    def remove_popular_ad(self, ad_id: int):
        # Deprecated: popularity is derived from gold verification now
        ad = self.db.query(Ad).filter(Ad.id == ad_id).first()
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")
        return None

    def get_all_popular_ads(self):
        # Popular ads are ads with approved gold verification
        return (
            self.db.query(Ad)
            .options(
                joinedload(Ad.user),
                joinedload(Ad.gold_verification_requests)
            )
            .filter(
                exists().where(
                    (GoldVerificationRequest.ad_id == Ad.id) &
                    (GoldVerificationRequest.status == GoldVerificationStatus.approved)
                )
            )
            .all()
        )