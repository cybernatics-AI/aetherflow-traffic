"""
Traffic Light Model for AetherFlow Backend
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from enum import Enum

from aetherflow.core.database import Base


class TrafficLightStatus(str, Enum):
    """Traffic light status enumeration"""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    FLASHING_RED = "flashing_red"
    FLASHING_YELLOW = "flashing_yellow"
    OFF = "off"


class TrafficLight(Base):
    """Traffic light configurations and control"""
    
    __tablename__ = "traffic_lights"
    
    id = Column(Integer, primary_key=True, index=True)
    intersection_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(200), nullable=True)
    city = Column(String(100), nullable=False)
    
    # Current status
    status = Column(String(20), nullable=False, default=TrafficLightStatus.RED)
    
    # Timing configuration (in seconds)
    red_duration = Column(Integer, default=30)
    yellow_duration = Column(Integer, default=5)
    green_duration = Column(Integer, default=25)
    
    # AI optimization data
    optimized_timing = Column(JSON, nullable=True)  # AI-suggested timings
    traffic_flow_data = Column(JSON, nullable=True)  # Historical traffic data
    
    # Control settings
    is_ai_controlled = Column(Boolean, default=False)
    manual_override = Column(Boolean, default=False)
    priority_mode = Column(Boolean, default=False)  # Emergency vehicle priority
    
    # Performance metrics
    average_wait_time = Column(Float, default=0.0)  # Average wait time in seconds
    throughput_vehicles_per_hour = Column(Integer, default=0)
    congestion_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # NFT integration
    nft_token_id = Column(String(50), nullable=True)  # Associated Traffic NFT
    nft_owner = Column(String(50), nullable=True)  # NFT owner account ID
    
    # Timestamps
    last_status_change = Column(DateTime, default=datetime.utcnow)
    last_optimization = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "intersection_id": self.intersection_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "city": self.city,
            "status": self.status,
            "red_duration": self.red_duration,
            "yellow_duration": self.yellow_duration,
            "green_duration": self.green_duration,
            "optimized_timing": self.optimized_timing,
            "is_ai_controlled": self.is_ai_controlled,
            "manual_override": self.manual_override,
            "priority_mode": self.priority_mode,
            "average_wait_time": self.average_wait_time,
            "throughput_vehicles_per_hour": self.throughput_vehicles_per_hour,
            "congestion_score": self.congestion_score,
            "nft_token_id": self.nft_token_id,
            "nft_owner": self.nft_owner,
            "last_status_change": self.last_status_change.isoformat() if self.last_status_change else None,
            "last_optimization": self.last_optimization.isoformat() if self.last_optimization else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def location(self) -> Dict[str, float]:
        """Get location as lat/lng dictionary"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }
    
    @property
    def total_cycle_time(self) -> int:
        """Get total traffic light cycle time"""
        return self.red_duration + self.yellow_duration + self.green_duration
    
    def update_status(self, new_status: TrafficLightStatus) -> None:
        """Update traffic light status"""
        if self.status != new_status:
            self.status = new_status
            self.last_status_change = datetime.utcnow()
    
    def apply_ai_optimization(self, optimized_timings: Dict[str, int]) -> None:
        """Apply AI-optimized timings"""
        if "red_duration" in optimized_timings:
            self.red_duration = optimized_timings["red_duration"]
        if "yellow_duration" in optimized_timings:
            self.yellow_duration = optimized_timings["yellow_duration"]
        if "green_duration" in optimized_timings:
            self.green_duration = optimized_timings["green_duration"]
        
        self.optimized_timing = optimized_timings
        self.last_optimization = datetime.utcnow()
        self.is_ai_controlled = True
