"""
Time Utilities for AetherFlow
"""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict, Any
import calendar

from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


class TimeUtils:
    """Time-related utility functions"""
    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime"""
        return datetime.utcnow().replace(tzinfo=timezone.utc)
    
    @staticmethod
    def to_timestamp(dt: datetime) -> int:
        """Convert datetime to Unix timestamp"""
        return int(dt.timestamp())
    
    @staticmethod
    def from_timestamp(timestamp: Union[int, float]) -> datetime:
        """Convert Unix timestamp to datetime"""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    
    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """Convert datetime to ISO format string"""
        return dt.isoformat()
    
    @staticmethod
    def from_iso_string(iso_string: str) -> datetime:
        """Convert ISO format string to datetime"""
        # Handle various ISO format variations
        iso_string = iso_string.replace('Z', '+00:00')
        return datetime.fromisoformat(iso_string)
    
    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Get human-readable time ago string"""
        
        now = TimeUtils.utc_now()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days < 30:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.days < 365:
            months = int(diff.days / 30)
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = int(diff.days / 365)
            return f"{years} year{'s' if years != 1 else ''} ago"
    
    @staticmethod
    def is_recent(dt: datetime, minutes: int = 60) -> bool:
        """Check if datetime is within recent time window"""
        
        now = TimeUtils.utc_now()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return (now - dt).total_seconds() <= minutes * 60
    
    @staticmethod
    def is_future(dt: datetime) -> bool:
        """Check if datetime is in the future"""
        
        now = TimeUtils.utc_now()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt > now
    
    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """Add hours to datetime"""
        return dt + timedelta(hours=hours)
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Add days to datetime"""
        return dt + timedelta(days=days)
    
    @staticmethod
    def start_of_day(dt: datetime) -> datetime:
        """Get start of day (00:00:00) for given datetime"""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_day(dt: datetime) -> datetime:
        """Get end of day (23:59:59.999999) for given datetime"""
        return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def start_of_week(dt: datetime) -> datetime:
        """Get start of week (Monday 00:00:00) for given datetime"""
        days_since_monday = dt.weekday()
        start_of_week = dt - timedelta(days=days_since_monday)
        return TimeUtils.start_of_day(start_of_week)
    
    @staticmethod
    def start_of_month(dt: datetime) -> datetime:
        """Get start of month for given datetime"""
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @staticmethod
    def end_of_month(dt: datetime) -> datetime:
        """Get end of month for given datetime"""
        last_day = calendar.monthrange(dt.year, dt.month)[1]
        return dt.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    @staticmethod
    def get_time_ranges(
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 60
    ) -> list:
        """Split time range into intervals"""
        
        ranges = []
        current_time = start_time
        
        while current_time < end_time:
            next_time = min(current_time + timedelta(minutes=interval_minutes), end_time)
            ranges.append((current_time, next_time))
            current_time = next_time
        
        return ranges
    
    @staticmethod
    def business_hours_only(dt: datetime) -> bool:
        """Check if datetime falls within business hours (9 AM - 5 PM, Mon-Fri)"""
        
        # Check if it's a weekday (Monday = 0, Sunday = 6)
        if dt.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if it's within business hours
        return 9 <= dt.hour < 17
    
    @staticmethod
    def peak_traffic_hours(dt: datetime) -> bool:
        """Check if datetime falls within typical peak traffic hours"""
        
        # Morning rush: 7-9 AM, Evening rush: 5-7 PM on weekdays
        if dt.weekday() < 5:  # Weekday
            return (7 <= dt.hour < 9) or (17 <= dt.hour < 19)
        
        return False
    
    @staticmethod
    def time_until(target_dt: datetime) -> timedelta:
        """Calculate time until target datetime"""
        
        now = TimeUtils.utc_now()
        if target_dt.tzinfo is None:
            target_dt = target_dt.replace(tzinfo=timezone.utc)
        
        return target_dt - now
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string"""
        
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    @staticmethod
    def get_timezone_offset(timezone_name: str) -> Optional[int]:
        """Get timezone offset in hours (simplified)"""
        
        # This is a simplified implementation
        # In production, use proper timezone libraries like pytz
        
        timezone_offsets = {
            'UTC': 0,
            'EST': -5,
            'PST': -8,
            'CST': -6,
            'MST': -7,
            'GMT': 0,
            'CET': 1,
            'JST': 9,
            'AEST': 10
        }
        
        return timezone_offsets.get(timezone_name.upper())
    
    @staticmethod
    def round_to_nearest_minute(dt: datetime) -> datetime:
        """Round datetime to nearest minute"""
        
        if dt.second >= 30:
            dt = dt + timedelta(minutes=1)
        
        return dt.replace(second=0, microsecond=0)
    
    @staticmethod
    def round_to_nearest_hour(dt: datetime) -> datetime:
        """Round datetime to nearest hour"""
        
        if dt.minute >= 30:
            dt = dt + timedelta(hours=1)
        
        return dt.replace(minute=0, second=0, microsecond=0)
    
    @staticmethod
    def get_age_in_seconds(dt: datetime) -> float:
        """Get age of datetime in seconds"""
        
        now = TimeUtils.utc_now()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return (now - dt).total_seconds()
    
    @staticmethod
    def is_stale(dt: datetime, max_age_minutes: int = 60) -> bool:
        """Check if datetime is stale (older than max age)"""
        
        age_seconds = TimeUtils.get_age_in_seconds(dt)
        return age_seconds > max_age_minutes * 60
    
    @staticmethod
    def get_time_bucket(dt: datetime, bucket_minutes: int = 15) -> datetime:
        """Get time bucket for aggregation (e.g., round to nearest 15 minutes)"""
        
        # Calculate minutes since start of hour
        minutes_in_hour = dt.minute
        
        # Round down to nearest bucket
        bucket_minute = (minutes_in_hour // bucket_minutes) * bucket_minutes
        
        return dt.replace(minute=bucket_minute, second=0, microsecond=0)
    
    @staticmethod
    def performance_timer():
        """Context manager for measuring performance"""
        
        class PerformanceTimer:
            def __init__(self):
                self.start_time = None
                self.end_time = None
            
            def __enter__(self):
                self.start_time = time.perf_counter()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.end_time = time.perf_counter()
            
            @property
            def elapsed_seconds(self) -> float:
                if self.end_time is None:
                    return time.perf_counter() - self.start_time
                return self.end_time - self.start_time
            
            @property
            def elapsed_ms(self) -> float:
                return self.elapsed_seconds * 1000
        
        return PerformanceTimer()
    
    @staticmethod
    def schedule_next_run(
        last_run: datetime,
        interval_minutes: int,
        max_delay_minutes: int = 5
    ) -> datetime:
        """Calculate next scheduled run time"""
        
        next_run = last_run + timedelta(minutes=interval_minutes)
        now = TimeUtils.utc_now()
        
        # If we're behind schedule, don't delay more than max_delay_minutes
        if next_run < now:
            delay = min((now - next_run).total_seconds() / 60, max_delay_minutes)
            next_run = now + timedelta(minutes=delay)
        
        return next_run
    
    @staticmethod
    def get_traffic_analysis_windows() -> Dict[str, Dict[str, Any]]:
        """Get predefined time windows for traffic analysis"""
        
        now = TimeUtils.utc_now()
        
        return {
            "last_hour": {
                "start": now - timedelta(hours=1),
                "end": now,
                "label": "Last Hour"
            },
            "last_4_hours": {
                "start": now - timedelta(hours=4),
                "end": now,
                "label": "Last 4 Hours"
            },
            "today": {
                "start": TimeUtils.start_of_day(now),
                "end": now,
                "label": "Today"
            },
            "yesterday": {
                "start": TimeUtils.start_of_day(now - timedelta(days=1)),
                "end": TimeUtils.end_of_day(now - timedelta(days=1)),
                "label": "Yesterday"
            },
            "this_week": {
                "start": TimeUtils.start_of_week(now),
                "end": now,
                "label": "This Week"
            },
            "last_week": {
                "start": TimeUtils.start_of_week(now - timedelta(weeks=1)),
                "end": TimeUtils.start_of_week(now),
                "label": "Last Week"
            }
        }
    
    @staticmethod
    def is_data_fresh(timestamp: datetime, freshness_minutes: int = 5) -> bool:
        """Check if data timestamp is fresh enough for real-time processing"""
        
        return not TimeUtils.is_stale(timestamp, freshness_minutes)
    
    @staticmethod
    def calculate_uptime_percentage(
        start_time: datetime,
        downtime_periods: list,
        end_time: Optional[datetime] = None
    ) -> float:
        """Calculate uptime percentage given downtime periods"""
        
        if end_time is None:
            end_time = TimeUtils.utc_now()
        
        total_time = (end_time - start_time).total_seconds()
        
        if total_time <= 0:
            return 100.0
        
        total_downtime = 0
        for period in downtime_periods:
            downtime_start = max(period['start'], start_time)
            downtime_end = min(period['end'], end_time)
            
            if downtime_end > downtime_start:
                total_downtime += (downtime_end - downtime_start).total_seconds()
        
        uptime_percentage = ((total_time - total_downtime) / total_time) * 100
        return max(0.0, min(100.0, uptime_percentage))
