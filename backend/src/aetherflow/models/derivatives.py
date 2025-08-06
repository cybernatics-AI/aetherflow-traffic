"""
Derivatives Model for AetherFlow Backend
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from enum import Enum

from aetherflow.core.database import Base


class DerivativeType(str, Enum):
    """Derivative type enumeration"""
    CONGESTION_FUTURE = "congestion_future"
    TRAFFIC_OPTION = "traffic_option"
    CARBON_CREDIT = "carbon_credit"
    SPEED_SWAP = "speed_swap"


class DerivativeStatus(str, Enum):
    """Derivative status enumeration"""
    ACTIVE = "active"
    SETTLED = "settled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Derivative(Base):
    """Congestion derivatives contracts"""
    
    __tablename__ = "derivatives"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Contract identification
    contract_id = Column(String(100), nullable=False, unique=True, index=True)
    derivative_type = Column(String(30), nullable=False, default=DerivativeType.CONGESTION_FUTURE)
    
    # Contract parties
    creator = Column(String(50), nullable=False, index=True)  # Hedera account ID
    counterparty = Column(String(50), nullable=True, index=True)  # Hedera account ID
    
    # Contract terms
    underlying_asset = Column(String(100), nullable=False)  # e.g., "Manhattan_Traffic_Index"
    strike_price = Column(Float, nullable=False)  # Strike price or target value
    contract_size = Column(Float, nullable=False)  # Contract size/multiplier
    premium = Column(Float, nullable=False)  # Premium paid
    
    # Pricing
    current_price = Column(Float, nullable=True)  # Current market price
    mark_to_market = Column(Float, default=0.0)  # Current P&L
    
    # Settlement terms
    settlement_date = Column(DateTime, nullable=False)
    settlement_price = Column(Float, nullable=True)  # Final settlement price
    settlement_amount = Column(Float, nullable=True)  # Final settlement amount
    
    # Contract specifications
    contract_terms = Column(JSON, nullable=True)  # Detailed contract terms
    oracle_source = Column(String(100), nullable=True)  # Data oracle source
    
    # Status and lifecycle
    status = Column(String(20), nullable=False, default=DerivativeStatus.ACTIVE)
    is_exercised = Column(Boolean, default=False)
    exercise_date = Column(DateTime, nullable=True)
    
    # Risk management
    margin_requirement = Column(Float, default=0.0)  # Margin required
    collateral_posted = Column(Float, default=0.0)  # Collateral posted
    
    # Performance tracking
    realized_pnl = Column(Float, default=0.0)  # Realized profit/loss
    unrealized_pnl = Column(Float, default=0.0)  # Unrealized profit/loss
    
    # Hedera integration
    creation_tx_id = Column(String(100), nullable=True)
    settlement_tx_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "derivative_type": self.derivative_type,
            "creator": self.creator,
            "counterparty": self.counterparty,
            "underlying_asset": self.underlying_asset,
            "strike_price": self.strike_price,
            "contract_size": self.contract_size,
            "premium": self.premium,
            "current_price": self.current_price,
            "mark_to_market": self.mark_to_market,
            "settlement_date": self.settlement_date.isoformat() if self.settlement_date else None,
            "settlement_price": self.settlement_price,
            "settlement_amount": self.settlement_amount,
            "contract_terms": self.contract_terms,
            "oracle_source": self.oracle_source,
            "status": self.status,
            "is_exercised": self.is_exercised,
            "exercise_date": self.exercise_date.isoformat() if self.exercise_date else None,
            "margin_requirement": self.margin_requirement,
            "collateral_posted": self.collateral_posted,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "creation_tx_id": self.creation_tx_id,
            "settlement_tx_id": self.settlement_tx_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def update_mark_to_market(self, current_market_price: float) -> None:
        """Update mark-to-market valuation"""
        self.current_price = current_market_price
        
        # Calculate unrealized P&L based on derivative type
        if self.derivative_type == DerivativeType.CONGESTION_FUTURE:
            # For futures: (current_price - strike_price) * contract_size
            self.unrealized_pnl = (current_market_price - self.strike_price) * self.contract_size
        elif self.derivative_type == DerivativeType.TRAFFIC_OPTION:
            # For options: max(0, current_price - strike_price) * contract_size - premium
            intrinsic_value = max(0, current_market_price - self.strike_price)
            self.unrealized_pnl = (intrinsic_value * self.contract_size) - self.premium
        
        self.mark_to_market = self.unrealized_pnl
    
    def settle_contract(self, final_price: float, tx_id: str) -> None:
        """Settle the derivative contract"""
        self.settlement_price = final_price
        self.settlement_tx_id = tx_id
        self.status = DerivativeStatus.SETTLED
        
        # Calculate final settlement amount
        if self.derivative_type == DerivativeType.CONGESTION_FUTURE:
            self.settlement_amount = (final_price - self.strike_price) * self.contract_size
        elif self.derivative_type == DerivativeType.TRAFFIC_OPTION:
            intrinsic_value = max(0, final_price - self.strike_price)
            self.settlement_amount = (intrinsic_value * self.contract_size) - self.premium
        
        # Move unrealized to realized P&L
        self.realized_pnl = self.unrealized_pnl
        self.unrealized_pnl = 0.0
    
    def exercise_option(self, exercise_price: float, tx_id: str) -> None:
        """Exercise an option contract"""
        if self.derivative_type != DerivativeType.TRAFFIC_OPTION:
            raise ValueError("Only options can be exercised")
        
        self.is_exercised = True
        self.exercise_date = datetime.utcnow()
        self.settlement_price = exercise_price
        self.settlement_tx_id = tx_id
        
        # Calculate exercise value
        intrinsic_value = max(0, exercise_price - self.strike_price)
        self.settlement_amount = (intrinsic_value * self.contract_size) - self.premium
        
        self.status = DerivativeStatus.SETTLED
        self.realized_pnl = self.settlement_amount
        self.unrealized_pnl = 0.0
    
    def is_expired(self) -> bool:
        """Check if contract is expired"""
        return datetime.utcnow() > self.settlement_date and self.status == DerivativeStatus.ACTIVE
    
    def days_to_expiry(self) -> int:
        """Get days to contract expiry"""
        if self.settlement_date:
            delta = self.settlement_date - datetime.utcnow()
            return max(0, delta.days)
        return 0
