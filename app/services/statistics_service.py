from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from typing import Dict, List, Any, Tuple
from datetime import datetime, date, timedelta
from app.models.ad import Ad, GoldVerificationRequest
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

    def get_total_gold_verification_orders_count(self) -> int:
        """Count total gold verification requests (orders)"""
        return self.db.query(func.count(GoldVerificationRequest.id)).scalar() or 0

    def get_timeseries_by_month(
        self,
        start_month: date,
        end_month: date
    ) -> Dict[str, Any]:
        """
        Aggregate monthly counts for ads (by Ad.created_at), users (by User.created_at),
        and orders (by GoldVerificationRequest.requested_at) between inclusive month range.
        """
        # Build month buckets inclusive
        months: List[date] = []
        cursor = date(start_month.year, start_month.month, 1)
        end_cursor = date(end_month.year, end_month.month, 1)
        while cursor <= end_cursor:
            months.append(cursor)
            # advance by one month safely
            year = cursor.year + (1 if cursor.month == 12 else 0)
            month = 1 if cursor.month == 12 else cursor.month + 1
            cursor = date(year, month, 1)

        # Compute absolute date range [range_start, range_end)
        range_start = months[0]
        last_month = months[-1]
        range_end = date(
            last_month.year + (1 if last_month.month == 12 else 0),
            1 if last_month.month == 12 else last_month.month + 1,
            1
        )

        # Helper to key by (year, month)
        def ym_key(y: int, m: int) -> Tuple[int, int]:
            return (int(y), int(m))

        # Ads aggregation
        ads_rows = self.db.query(
            extract('year', Ad.created_at).label('y'),
            extract('month', Ad.created_at).label('m'),
            func.count(Ad.id).label('c')
        ).filter(
            and_(Ad.created_at >= range_start, Ad.created_at < range_end)
        ).group_by(
            extract('year', Ad.created_at), extract('month', Ad.created_at)
        ).all()
        ads_map = {ym_key(r.y, r.m): int(r.c) for r in ads_rows}

        # Users aggregation
        users_rows = self.db.query(
            extract('year', User.created_at).label('y'),
            extract('month', User.created_at).label('m'),
            func.count(User.id).label('c')
        ).filter(
            and_(User.created_at >= range_start, User.created_at < range_end)
        ).group_by(
            extract('year', User.created_at), extract('month', User.created_at)
        ).all()
        users_map = {ym_key(r.y, r.m): int(r.c) for r in users_rows}

        # Orders aggregation
        orders_rows = self.db.query(
            extract('year', GoldVerificationRequest.requested_at).label('y'),
            extract('month', GoldVerificationRequest.requested_at).label('m'),
            func.count(GoldVerificationRequest.id).label('c')
        ).filter(
            and_(GoldVerificationRequest.requested_at >= range_start, GoldVerificationRequest.requested_at < range_end)
        ).group_by(
            extract('year', GoldVerificationRequest.requested_at), extract('month', GoldVerificationRequest.requested_at)
        ).all()
        orders_map = {ym_key(r.y, r.m): int(r.c) for r in orders_rows}

        # Build series
        result_months: List[Dict[str, Any]] = []
        for m in months:
            key = (m.year, m.month)
            result_months.append({
                'year': m.year,
                'month': m.month,
                'label': f"{m.year}-{m.month:02d}",
                'ads': ads_map.get(key, 0),
                'users': users_map.get(key, 0),
                'orders': orders_map.get(key, 0),
                'month_name': self._get_month_name(m.month)
            })

        return {
            'start': f"{range_start.year}-{range_start.month:02d}",
            'end': f"{last_month.year}-{last_month.month:02d}",
            'months': result_months
        }

    def _get_month_name(self, month: int) -> str:
        """Get month name by number"""
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        return month_names.get(month, 'Unknown')
