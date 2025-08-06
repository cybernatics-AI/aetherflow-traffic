"""
Vehicle Data Model for AetherFlow Backend
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid

from aetherflow.core.database import Base


class VehicleData(Base):
    """Vehicle data submissions with encrypted data and ZK-proofs"""
    
    __tablename__ = "vehicle_data"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String(100), index=True, nullable=False)
    speed = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    heading = Column(Float, nullable=True)  # Direction in degrees
    altitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Encrypted and hashed data
    encrypted_data = Column(JSON, nullable=True)  # Encrypted sensitive data
    data_hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash
    zk_proof = Column(JSON, nullable=True)  # Zero-knowledge proof
    
    # Hedera integration
    hcs_message_id = Column(String(100), nullable=True, index=True)
    hcs_topic_id = Column(String(50), nullable=True)
    hedera_tx_id = Column(String(100), nullable=True)
    
    # Additional metadata
    device_type = Column(String(50), nullable=True)  # OBD-II, smartphone, etc.
    data_quality_score = Column(Float, default=1.0)  # 0.0 to 1.0
    is_validated = Column(Boolean, default=False)
    validation_timestamp = Column(DateTime, nullable=True)
    
    # Rewards and tokenomics
    reward_amount = Column(Float, default=0.0)  # $AETHER tokens earned
    reward_tx_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "speed": self.speed,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "heading": self.heading,
            "altitude": self.altitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "data_hash": self.data_hash,
            "hcs_message_id": self.hcs_message_id,
            "hcs_topic_id": self.hcs_topic_id,
            "hedera_tx_id": self.hedera_tx_id,
            "device_type": self.device_type,
            "data_quality_score": self.data_quality_score,
            "is_validated": self.is_validated,
            "reward_amount": self.reward_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def location(self) -> Dict[str, float]:
        """Get location as lat/lng dictionary"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }
