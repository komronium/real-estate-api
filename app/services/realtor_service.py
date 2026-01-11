from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from uuid import UUID

from app.models.user import User, UserRole
from app.models.ad import Ad
from app.models.favourite import Favourite


class RealtorService:
    def __init__(self, db: Session):
        self.db = db

    def get_realtor_ranking(self) -> List[Dict]:
        """
        Get realtors ranked by their ads' total favourites and views
        Ranking is based on:
        1. Total favourites count (sum of all favourites for realtor's ads)
        2. Total views count (sum of all views for realtor's ads)
        """
        # Get all realtors
        realtors = self.db.query(User).filter(User.role == UserRole.REALTOR).all()
        
        ranking = []
        
        for realtor in realtors:
            # Get all ads by this realtor
            ads = self.db.query(Ad).filter(Ad.user_id == realtor.id).all()
            ad_ids = [ad.id for ad in ads] if ads else []
            
            # Calculate total favourites count
            total_favourites = 0
            if ad_ids:
                total_favourites = self.db.query(func.count(Favourite.id)).filter(
                    Favourite.ad_id.in_(ad_ids)
                ).scalar() or 0
            
            # Calculate total views count
            total_views = 0
            if ad_ids:
                total_views = self.db.query(func.sum(Ad.views_count)).filter(
                    Ad.id.in_(ad_ids)
                ).scalar() or 0
            
            # Calculate ranking score (weighted: favourites * 2 + views)
            ranking_score = (total_favourites * 2) + total_views
            
            ranking.append({
                "realtor": realtor,
                "total_favourites": total_favourites,
                "total_views": total_views,
                "total_ads": len(ad_ids),
                "ranking_score": ranking_score
            })
        
        # Sort by ranking score (descending)
        ranking.sort(key=lambda x: x["ranking_score"], reverse=True)
        
        return ranking
