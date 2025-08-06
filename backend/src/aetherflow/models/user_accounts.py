"""
User Accounts Model for AetherFlow Backend
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from enum import Enum

from aetherflow.core.database import Base


class UserRole(str, Enum):
    """User role enumeration"""
    DRIVER = "driver"
    ADMIN = "admin"
    TRADER = "trader"
    CITY_OFFICIAL = "city_official"
    FLEET_MANAGER = "fleet_manager"
    DEVELOPER = "developer"


class UserAccount(Base):
    """User accounts and roles"""
    
    __tablename__ = "user_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Hedera account information
    wallet_address = Column(String(50), nullable=False, unique=True, index=True)
    public_key = Column(String(200), nullable=True)
    
    # User profile
    username = Column(String(50), nullable=True, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    full_name = Column(String(100), nullable=True)
    
    # Role and permissions
    role = Column(String(20), nullable=False, default=UserRole.DRIVER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Tokenomics and rewards
    aether_balance = Column(Float, default=0.0)
    total_rewards_earned = Column(Float, default=0.0)
    total_data_submissions = Column(Integer, default=0)
    
    # Reputation and trust
    reputation_score = Column(Float, default=1.0)  # 0.0 to 1.0
    trust_level = Column(String(20), default="basic")  # basic, trusted, verified
    
    # Activity tracking
    last_login = Column(DateTime, nullable=True)
    last_data_submission = Column(DateTime, nullable=True)
    
    # Privacy settings
    data_sharing_consent = Column(Boolean, default=False)
    location_tracking_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    
    # KYC/Verification
    kyc_status = Column(String(20), default="pending")  # pending, approved, rejected
    kyc_document_hash = Column(String(64), nullable=True)
    verification_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "wallet_address": self.wallet_address,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "aether_balance": self.aether_balance,
            "total_rewards_earned": self.total_rewards_earned,
            "total_data_submissions": self.total_data_submissions,
            "reputation_score": self.reputation_score,
            "trust_level": self.trust_level,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_data_submission": self.last_data_submission.isoformat() if self.last_data_submission else None,
            "data_sharing_consent": self.data_sharing_consent,
            "location_tracking_consent": self.location_tracking_consent,
            "kyc_status": self.kyc_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def update_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    def update_data_submission(self) -> None:
        """Update data submission tracking"""
        self.last_data_submission = datetime.utcnow()
        self.total_data_submissions += 1
    
    def add_reward(self, amount: float) -> None:
        """Add reward to user balance"""
        self.aether_balance += amount
        self.total_rewards_earned += amount
    
    def can_submit_data(self) -> bool:
        """Check if user can submit data"""
        return (
            self.is_active and 
            self.data_sharing_consent and 
            self.location_tracking_consent
        )
    
    def can_trade_nfts(self) -> bool:
        """Check if user can trade NFTs"""
        return (
            self.is_active and 
            self.is_verified and 
            self.role in [UserRole.TRADER, UserRole.ADMIN, UserRole.CITY_OFFICIAL]
        )
