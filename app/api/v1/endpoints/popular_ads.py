from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_admin_user
from app.schemas.popular_ad import PopularAdCreate, PopularAdOut
from app.models.user import User
from app.services.popular_ad import PopularAdService

router = APIRouter(prefix="/api/v1/popular-ads", tags=["Popular Ads"])

@router.get("/", response_model=List[PopularAdOut])
def list_popular_ads(db: Session = Depends(get_db)):
    service = PopularAdService(db)
    return service.get_all_popular_ads()

@router.post("/", response_model=PopularAdOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
def add_popular_ad(
    data: PopularAdCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    service = PopularAdService(db)
    return service.create_popular_ad(data, admin.id)

@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_admin_user)])
def remove_popular_ad(
    ad_id: int,
    db: Session = Depends(get_db)
):
    service = PopularAdService(db)
    service.remove_popular_ad(ad_id)