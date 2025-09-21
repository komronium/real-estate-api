from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from app.api.deps import get_db
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/api/v1/statistics", tags=["Statistics"])


@router.get("/users/count", response_model=Dict[str, int])
def get_total_users_count(db: Session = Depends(get_db)):
    """Get total number of users"""
    stats_service = StatisticsService(db)
    count = stats_service.get_total_users_count()
    return {"total_users": count}


@router.get("/ads/count", response_model=Dict[str, int])
def get_total_ads_count(db: Session = Depends(get_db)):
    """Get total number of ads"""
    stats_service = StatisticsService(db)
    count = stats_service.get_total_ads_count()
    return {"total_ads": count}


@router.get("/ads/monthly/{year}", response_model=List[Dict[str, Any]])
def get_ads_count_by_month(
    year: int,
    db: Session = Depends(get_db)
):
    """Get ads count by month for a specific year"""
    if year < 2000 or year > datetime.now().year + 1:
        raise HTTPException(status_code=400, detail="Invalid year")
    
    stats_service = StatisticsService(db)
    return stats_service.get_ads_count_by_month(year)


@router.get("/ads/yearly", response_model=List[Dict[str, int]])
def get_ads_count_by_year(db: Session = Depends(get_db)):
    """Get ads count by year"""
    stats_service = StatisticsService(db)
    return stats_service.get_ads_count_by_year()


@router.get("/ads/monthly-yearly", response_model=List[Dict[str, Any]])
def get_ads_count_by_month_and_year(db: Session = Depends(get_db)):
    """Get ads count by month and year"""
    stats_service = StatisticsService(db)
    return stats_service.get_ads_count_by_month_and_year()


@router.get("/ads/current-month", response_model=Dict[str, int])
def get_current_month_ads_count(db: Session = Depends(get_db)):
    """Get ads count for current month"""
    stats_service = StatisticsService(db)
    count = stats_service.get_current_month_ads_count()
    return {"current_month_ads": count}


@router.get("/ads/current-year", response_model=Dict[str, int])
def get_current_year_ads_count(db: Session = Depends(get_db)):
    """Get ads count for current year"""
    stats_service = StatisticsService(db)
    count = stats_service.get_current_year_ads_count()
    return {"current_year_ads": count}


@router.get("/overview", response_model=Dict[str, Any])
def get_statistics_overview(db: Session = Depends(get_db)):
    """Get overview of all statistics"""
    stats_service = StatisticsService(db)
    
    return {
        "total_users": stats_service.get_total_users_count(),
        "total_ads": stats_service.get_total_ads_count(),
        "current_month_ads": stats_service.get_current_month_ads_count(),
        "current_year_ads": stats_service.get_current_year_ads_count(),
        "monthly_stats_current_year": stats_service.get_ads_count_by_month(datetime.now().year),
        "yearly_stats": stats_service.get_ads_count_by_year()
    }
