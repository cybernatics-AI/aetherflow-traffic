"""
Traffic NFTs Model for AetherFlow Backend
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from enum import Enum

from aetherflow.core.database import Base


class NFTStatus(str, Enum):
    """NFT status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FOR_SALE = "for_sale"
    SOLD = "sold"
    BURNED = "burned"


class TrafficNFT(Base):
    """Traffic NFTs for intersection monetization"""
    
    __tablename__ = "traffic_nfts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # NFT identification
    token_id = Column(String(50), nullable=False, unique=True, index=True)
    serial_number = Column(Integer, nullable=False)
    
    # Associated intersection
    intersection_id = Column(String(100), nullable=False, index=True)
    
    # Ownership
    owner = Column(String(50), nullable=False, index=True)  # Hedera account ID
    previous_owner = Column(String(50), nullable=True)
    
    # Pricing and trading
    current_price = Column(Float, nullable=True)  # Current listing price in HBAR
    last_sale_price = Column(Float, nullable=True)  # Last sale price
    floor_price = Column(Float, nullable=True)  # Floor price for this intersection
    
    # Revenue sharing
    revenue_share_percentage = Column(Float, default=5.0)  # Percentage of fees earned
    total_revenue_earned = Column(Float, default=0.0)  # Total revenue earned
    monthly_revenue = Column(Float, default=0.0)  # Current month revenue
    
    # Performance metrics
    traffic_volume = Column(Integer, default=0)  # Daily traffic volume
    optimization_score = Column(Float, default=0.0)  # AI optimization effectiveness
    congestion_reduction = Column(Float, default=0.0)  # Congestion reduction percentage
    
    # NFT metadata
    metadata = Column(JSON, nullable=True)  # IPFS metadata
    image_url = Column(String(200), nullable=True)  # NFT image URL
    description = Column(String(500), nullable=True)
    
    # Trading status
    status = Column(String(20), nullable=False, default=NFTStatus.ACTIVE)
    is_listed = Column(Boolean, default=False)
    listing_expiry = Column(DateTime, nullable=True)
    
    # Hedera integration
    mint_tx_id = Column(String(100), nullable=True)
    last_transfer_tx_id = Column(String(100), nullable=True)
    
    # Timestamps
    mint_date = Column(DateTime, default=datetime.utcnow)
    last_sale_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "token_id": self.token_id,
            "serial_number": self.serial_number,
            "intersection_id": self.intersection_id,
            "owner": self.owner,
            "previous_owner": self.previous_owner,
            "current_price": self.current_price,
            "last_sale_price": self.last_sale_price,
            "floor_price": self.floor_price,
            "revenue_share_percentage": self.revenue_share_percentage,
            "total_revenue_earned": self.total_revenue_earned,
            "monthly_revenue": self.monthly_revenue,
            "traffic_volume": self.traffic_volume,
            "optimization_score": self.optimization_score,
            "congestion_reduction": self.congestion_reduction,
            "metadata": self.metadata,
            "image_url": self.image_url,
            "description": self.description,
            "status": self.status,
            "is_listed": self.is_listed,
            "listing_expiry": self.listing_expiry.isoformat() if self.listing_expiry else None,
            "mint_tx_id": self.mint_tx_id,
            "mint_date": self.mint_date.isoformat() if self.mint_date else None,
            "last_sale_date": self.last_sale_date.isoformat() if self.last_sale_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def list_for_sale(self, price: float, expiry_hours: int = 24) -> None:
        """List NFT for sale"""
        self.current_price = price
        self.is_listed = True
        self.status = NFTStatus.FOR_SALE
        self.listing_expiry = datetime.utcnow() + datetime.timedelta(hours=expiry_hours)
    
    def complete_sale(self, buyer: str, sale_price: float, tx_id: str) -> None:
        """Complete NFT sale"""
        self.previous_owner = self.owner
        self.owner = buyer
        self.last_sale_price = sale_price
        self.last_sale_date = datetime.utcnow()
        self.last_transfer_tx_id = tx_id
        self.is_listed = False
        self.status = NFTStatus.ACTIVE
        self.listing_expiry = None
    
    def add_revenue(self, amount: float) -> None:
        """Add revenue from fees"""
        self.total_revenue_earned += amount
        self.monthly_revenue += amount
    
    def reset_monthly_revenue(self) -> None:
        """Reset monthly revenue counter"""
        self.monthly_revenue = 0.0
    
    def update_performance_metrics(self, traffic_volume: int, optimization_score: float, congestion_reduction: float) -> None:
        """Update NFT performance metrics"""
        self.traffic_volume = traffic_volume
        self.optimization_score = optimization_score
        self.congestion_reduction = congestion_reduction
