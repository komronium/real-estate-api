from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Dict, List
from datetime import datetime, date
from app.models.ad import Ad
from app.models.user import User


class StatisticsService:
    
    def __init__(self, db: Session):
        self.db = db

    def get_total_users_count(self) -> int:
        """Get total number of users"""
        return self.db.query(User).count()

    def get_total_ads_count(self) -> int:
        """Get total number of ads"""
        return self.db.query(Ad).count()

    def get_ads_count_by_month(self, year: int) -> List[Dict]:
        """Get ads count by month for a specific year"""
        results = self.db.query(
            extract('month', Ad.created_at).label('month'),
            func.count(Ad.id).label('count')
        ).filter(
            extract('year', Ad.created_at) == year
        ).group_by(
            extract('month', Ad.created_at)
        ).order_by('month').all()

        return [
            {
                'month': int(result.month),
                'count': result.count,
                'month_name': self._get_month_name(int(result.month))
            }
            for result in results
        ]

    def get_ads_count_by_year(self) -> List[Dict]:
        """Get ads count by year"""
        results = self.db.query(
            extract('year', Ad.created_at).label('year'),
            func.count(Ad.id).label('count')
        ).group_by(
            extract('year', Ad.created_at)
        ).order_by('year').all()

        return [
            {
                'year': int(result.year),
                'count': result.count
            }
            for result in results
        ]

    def get_ads_count_by_month_and_year(self) -> List[Dict]:
        """Get ads count by month and year"""
        results = self.db.query(
            extract('year', Ad.created_at).label('year'),
            extract('month', Ad.created_at).label('month'),
            func.count(Ad.id).label('count')
        ).group_by(
            extract('year', Ad.created_at),
            extract('month', Ad.created_at)
        ).order_by('year', 'month').all()

        return [
            {
                'year': int(result.year),
                'month': int(result.month),
                'count': result.count,
                'month_name': self._get_month_name(int(result.month))
            }
            for result in results
        ]

    def get_current_month_ads_count(self) -> int:
        """Get ads count for current month"""
        current_date = datetime.now()
        return self.db.query(Ad).filter(
            extract('year', Ad.created_at) == current_date.year,
            extract('month', Ad.created_at) == current_date.month
        ).count()

    def get_current_year_ads_count(self) -> int:
        """Get ads count for current year"""
        current_date = datetime.now()
        return self.db.query(Ad).filter(
            extract('year', Ad.created_at) == current_date.year
        ).count()

    def _get_month_name(self, month: int) -> str:
        """Get month name by number"""
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        return month_names.get(month, 'Unknown')
