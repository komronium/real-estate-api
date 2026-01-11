from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.services.realtor_service import RealtorService
from app.schemas.user import UserOut
from pydantic import BaseModel, ConfigDict


class RealtorRankingOut(BaseModel):
    realtor: UserOut
    total_favourites: int
    total_views: int
    total_ads: int
    ranking_score: int

    model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/api/v1/realtors", tags=["Realtors"])


@router.get("/ranking", response_model=List[RealtorRankingOut])
def get_realtor_ranking(db: Session = Depends(get_db)):
    """
    Get realtors ranked by their ads' total favourites and views
    """
    realtor_service = RealtorService(db)
    ranking_data = realtor_service.get_realtor_ranking()
    
    # Convert to response format
    result = []
    for item in ranking_data:
        result.append(RealtorRankingOut(
            realtor=item["realtor"],
            total_favourites=item["total_favourites"],
            total_views=item["total_views"],
            total_ads=item["total_ads"],
            ranking_score=item["ranking_score"]
        ))
    
    return result
