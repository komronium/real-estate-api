from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_admin_user, get_current_user_optional
from app.schemas.popular_ad import PopularAdCreate
from app.schemas.ad import AdOut
from app.models.user import User
from app.services.popular_ad import PopularAdService

router = APIRouter(prefix="/api/v1/popular-ads", tags=["Popular Ads"])

@router.get("/", response_model=List[AdOut])
def list_popular_ads(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    service = PopularAdService(db)
    return service.get_all_popular_ads(current_user)


@router.post("/", response_model=AdOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
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