from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exists
from typing import Optional

from app.models.ad import Ad, GoldVerificationRequest, GoldVerificationStatus
from app.models.user import User
from app.models.favourite import Favourite
from app.schemas.popular_ad import PopularAdCreate


class PopularAdService:
    def __init__(self, db: Session):
        self.db = db

    def _annotate_favourites(self, ads: list[Ad], current_user: Optional[User]) -> list[Ad]:
        """Attach transient attributes is_favourited to each ad."""
        if not ads:
            return ads

        # Build list of ad ids to check favourite membership
        ad_ids = [ad.id for ad in ads]

        user_fav_set = set()
        if current_user is not None:
            user_fav_set = set(
                id for (id,) in self.db.query(Favourite.ad_id).filter(Favourite.user_id == current_user.id, Favourite.ad_id.in_(ad_ids)).all()
            )
        for ad in ads:
            # transient attribute to be picked by schema field
            setattr(ad, 'is_favourited', ad.id in user_fav_set if current_user is not None else False)

        return ads

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

    def get_all_popular_ads(self, current_user: Optional[User] = None):
        # Popular ads are ads with approved gold verification
        ads = (
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
        return self._annotate_favourites(ads, current_user)