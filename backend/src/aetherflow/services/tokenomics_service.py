"""
Tokenomics Service - Business Logic for Token Economics and Rewards
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from aetherflow.core.logging import get_logger
from aetherflow.models.user_accounts import UserAccount
from aetherflow.models.traffic_nfts import TrafficNFT
from aetherflow.models.derivatives import Derivative
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.hedera.client import HederaClient

logger = get_logger(__name__)


class TokenomicsService:
    """Service for managing tokenomics, rewards, and NFT operations"""
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera_client = hedera_client
        self.aether_token_id = "0.0.123457"  # AETHER token ID
        self.traffic_nft_token_id = "0.0.123458"  # Traffic NFT collection ID
        
        # Tokenomics parameters
        self.base_data_reward = Decimal("0.001")  # Base reward for data submission
        self.quality_multiplier_max = Decimal("2.0")  # Max multiplier for high quality
        self.staking_apy = Decimal("0.12")  # 12% APY for staking
        self.nft_revenue_share = Decimal("0.7")  # 70% revenue share to NFT holders
        
    async def calculate_data_rewards(
        self,
        db: AsyncSession,
        vehicle_data_id: int,
        validation_score: float,
        data_quality_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate rewards for vehicle data submission"""
        
        logger.info(f"Calculating rewards for vehicle data {vehicle_data_id}")
        
        # Base reward calculation
        base_reward = self.base_data_reward
        
        # Quality multiplier (0.5x to 2.0x based on validation score)
        quality_multiplier = Decimal(str(max(0.5, min(2.0, validation_score * 2))))
        
        # Bonus multipliers
        bonus_multiplier = Decimal("1.0")
        
        # Freshness bonus (data submitted within 5 minutes)
        if data_quality_metrics.get("freshness_minutes", 60) <= 5:
            bonus_multiplier += Decimal("0.2")
        
        # Accuracy bonus (high GPS accuracy)
        if data_quality_metrics.get("gps_accuracy", 10) <= 3:
            bonus_multiplier += Decimal("0.1")
        
        # ZK-proof bonus
        if data_quality_metrics.get("has_zk_proof", False):
            bonus_multiplier += Decimal("0.3")
        
        # Calculate final reward
        final_reward = base_reward * quality_multiplier * bonus_multiplier
        
        # Network congestion multiplier (higher rewards during peak times)
        congestion_multiplier = await self._get_congestion_multiplier(db)
        final_reward *= congestion_multiplier
        
        reward_breakdown = {
            "base_reward": float(base_reward),
            "quality_multiplier": float(quality_multiplier),
            "bonus_multiplier": float(bonus_multiplier),
            "congestion_multiplier": float(congestion_multiplier),
            "final_reward": float(final_reward),
            "currency": "AETHER"
        }
        
        logger.info(f"Calculated reward: {final_reward} AETHER for data {vehicle_data_id}")
        
        return reward_breakdown
    
    async def distribute_rewards(
        self,
        db: AsyncSession,
        user_account_id: str,
        reward_amount: Decimal,
        reward_type: str = "data_submission",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Distribute AETHER token rewards to user"""
        
        # Get user account
        result = await db.execute(
            select(UserAccount).where(UserAccount.hedera_account_id == user_account_id)
        )
        user_account = result.scalar_one_or_none()
        
        if not user_account:
            raise ValueError(f"User account {user_account_id} not found")
        
        # Update user balance
        user_account.aether_balance = (user_account.aether_balance or Decimal("0")) + reward_amount
        user_account.total_rewards_earned = (user_account.total_rewards_earned or Decimal("0")) + reward_amount
        
        # Transfer tokens via Hedera if client available
        transaction_id = None
        if self.hedera_client:
            try:
                transaction_id = await self.hedera_client.transfer_tokens(
                    token_id=self.aether_token_id,
                    to_account_id=user_account_id,
                    amount=int(reward_amount * 100000000)  # Convert to smallest unit
                )
            except Exception as e:
                logger.warning(f"Failed to transfer tokens via Hedera: {e}")
        
        await db.commit()
        
        logger.info(f"Distributed {reward_amount} AETHER to {user_account_id}")
        
        return {
            "user_account_id": user_account_id,
            "reward_amount": float(reward_amount),
            "reward_type": reward_type,
            "transaction_id": transaction_id,
            "new_balance": float(user_account.aether_balance),
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_traffic_nft(
        self,
        db: AsyncSession,
        intersection_id: str,
        owner_account_id: str,
        performance_metrics: Dict[str, Any],
        pricing_model: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a Traffic NFT for an intersection"""
        
        logger.info(f"Creating Traffic NFT for intersection {intersection_id}")
        
        # Calculate initial valuation based on performance
        initial_value = self._calculate_nft_value(performance_metrics)
        
        # Create NFT record
        traffic_nft = TrafficNFT(
            intersection_id=intersection_id,
            owner_account_id=owner_account_id,
            token_id=None,  # Will be set after minting
            current_value=initial_value,
            performance_metrics=performance_metrics,
            pricing_model=pricing_model,
            status="pending_mint",
            creation_date=datetime.utcnow()
        )
        
        # Mint NFT via Hedera if client available
        nft_token_id = None
        if self.hedera_client:
            try:
                # Create NFT metadata
                nft_metadata = {
                    "name": f"Traffic Intersection #{intersection_id}",
                    "description": f"Traffic optimization NFT for intersection {intersection_id}",
                    "intersection_id": intersection_id,
                    "performance_metrics": performance_metrics,
                    "creation_date": datetime.utcnow().isoformat()
                }
                
                nft_token_id = await self.hedera_client.mint_nft(
                    token_id=self.traffic_nft_token_id,
                    metadata=json.dumps(nft_metadata),
                    to_account_id=owner_account_id
                )
                
                traffic_nft.token_id = nft_token_id
                traffic_nft.status = "active"
                
            except Exception as e:
                logger.error(f"Failed to mint NFT: {e}")
                traffic_nft.status = "mint_failed"
        
        # Save to database
        db.add(traffic_nft)
        await db.commit()
        await db.refresh(traffic_nft)
        
        logger.info(f"Traffic NFT created: ID {traffic_nft.id}, Token ID: {nft_token_id}")
        
        return {
            "nft_id": traffic_nft.id,
            "intersection_id": intersection_id,
            "token_id": nft_token_id,
            "owner_account_id": owner_account_id,
            "initial_value": float(initial_value),
            "status": traffic_nft.status,
            "timestamp": traffic_nft.creation_date.isoformat()
        }
    
    async def calculate_nft_revenue_share(
        self,
        db: AsyncSession,
        nft_id: int,
        total_revenue: Decimal,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate revenue share for Traffic NFT holders"""
        
        # Get NFT
        result = await db.execute(
            select(TrafficNFT).where(TrafficNFT.id == nft_id)
        )
        traffic_nft = result.scalar_one_or_none()
        
        if not traffic_nft:
            raise ValueError(f"Traffic NFT {nft_id} not found")
        
        # Calculate revenue share
        nft_share = total_revenue * self.nft_revenue_share
        
        # Update NFT metrics
        traffic_nft.total_revenue_generated = (traffic_nft.total_revenue_generated or Decimal("0")) + nft_share
        traffic_nft.last_revenue_distribution = datetime.utcnow()
        
        # Distribute to owner
        if traffic_nft.owner_account_id:
            await self.distribute_rewards(
                db=db,
                user_account_id=traffic_nft.owner_account_id,
                reward_amount=nft_share,
                reward_type="nft_revenue_share",
                metadata={
                    "nft_id": nft_id,
                    "intersection_id": traffic_nft.intersection_id,
                    "period_days": period_days
                }
            )
        
        await db.commit()
        
        logger.info(f"Distributed {nft_share} AETHER revenue share for NFT {nft_id}")
        
        return {
            "nft_id": nft_id,
            "total_revenue": float(total_revenue),
            "nft_share": float(nft_share),
            "share_percentage": float(self.nft_revenue_share * 100),
            "owner_account_id": traffic_nft.owner_account_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def create_congestion_derivative(
        self,
        db: AsyncSession,
        area_definition: Dict[str, Any],
        contract_terms: Dict[str, Any],
        creator_account_id: str
    ) -> Dict[str, Any]:
        """Create a congestion derivative contract"""
        
        logger.info(f"Creating congestion derivative for area {area_definition}")
        
        # Calculate initial pricing
        current_congestion = await self._get_area_congestion_level(db, area_definition)
        initial_price = self._calculate_derivative_price(current_congestion, contract_terms)
        
        # Create derivative record
        derivative = Derivative(
            derivative_type="congestion",
            underlying_asset=json.dumps(area_definition),
            contract_terms=contract_terms,
            creator_account_id=creator_account_id,
            current_price=initial_price,
            status="active",
            creation_date=datetime.utcnow(),
            expiration_date=datetime.fromisoformat(contract_terms["expiration_date"])
        )
        
        # Save to database
        db.add(derivative)
        await db.commit()
        await db.refresh(derivative)
        
        logger.info(f"Congestion derivative created: ID {derivative.id}")
        
        return {
            "derivative_id": derivative.id,
            "derivative_type": "congestion",
            "area_definition": area_definition,
            "initial_price": float(initial_price),
            "contract_terms": contract_terms,
            "creator_account_id": creator_account_id,
            "timestamp": derivative.creation_date.isoformat()
        }
    
    async def update_derivative_pricing(
        self,
        db: AsyncSession,
        derivative_id: int
    ) -> Dict[str, Any]:
        """Update derivative pricing based on current conditions"""
        
        # Get derivative
        result = await db.execute(
            select(Derivative).where(Derivative.id == derivative_id)
        )
        derivative = result.scalar_one_or_none()
        
        if not derivative:
            raise ValueError(f"Derivative {derivative_id} not found")
        
        if derivative.derivative_type == "congestion":
            # Get current congestion level
            area_definition = json.loads(derivative.underlying_asset)
            current_congestion = await self._get_area_congestion_level(db, area_definition)
            
            # Calculate new price
            old_price = derivative.current_price
            new_price = self._calculate_derivative_price(current_congestion, derivative.contract_terms)
            
            # Update derivative
            derivative.current_price = new_price
            derivative.last_price_update = datetime.utcnow()
            
            # Update pricing history
            if not derivative.pricing_history:
                derivative.pricing_history = []
            
            derivative.pricing_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "price": float(new_price),
                "congestion_level": current_congestion
            })
            
            await db.commit()
            
            price_change = ((new_price - old_price) / old_price * 100) if old_price > 0 else 0
            
            logger.info(f"Updated derivative {derivative_id} price: {old_price} -> {new_price} ({price_change:+.2f}%)")
            
            return {
                "derivative_id": derivative_id,
                "old_price": float(old_price),
                "new_price": float(new_price),
                "price_change_percent": float(price_change),
                "congestion_level": current_congestion,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        else:
            raise ValueError(f"Unsupported derivative type: {derivative.derivative_type}")
    
    async def get_user_portfolio(
        self,
        db: AsyncSession,
        user_account_id: str
    ) -> Dict[str, Any]:
        """Get user's tokenomics portfolio"""
        
        # Get user account
        result = await db.execute(
            select(UserAccount).where(UserAccount.hedera_account_id == user_account_id)
        )
        user_account = result.scalar_one_or_none()
        
        if not user_account:
            raise ValueError(f"User account {user_account_id} not found")
        
        # Get user's NFTs
        nfts_result = await db.execute(
            select(TrafficNFT).where(TrafficNFT.owner_account_id == user_account_id)
        )
        user_nfts = nfts_result.scalars().all()
        
        # Get user's derivatives
        derivatives_result = await db.execute(
            select(Derivative).where(Derivative.creator_account_id == user_account_id)
        )
        user_derivatives = derivatives_result.scalars().all()
        
        # Calculate portfolio value
        nft_value = sum(nft.current_value or Decimal("0") for nft in user_nfts)
        derivative_value = sum(der.current_price or Decimal("0") for der in user_derivatives)
        total_portfolio_value = user_account.aether_balance + nft_value + derivative_value
        
        return {
            "user_account_id": user_account_id,
            "aether_balance": float(user_account.aether_balance or 0),
            "total_rewards_earned": float(user_account.total_rewards_earned or 0),
            "nfts": {
                "count": len(user_nfts),
                "total_value": float(nft_value),
                "details": [
                    {
                        "nft_id": nft.id,
                        "intersection_id": nft.intersection_id,
                        "current_value": float(nft.current_value or 0),
                        "total_revenue": float(nft.total_revenue_generated or 0)
                    }
                    for nft in user_nfts
                ]
            },
            "derivatives": {
                "count": len(user_derivatives),
                "total_value": float(derivative_value),
                "details": [
                    {
                        "derivative_id": der.id,
                        "type": der.derivative_type,
                        "current_price": float(der.current_price or 0),
                        "status": der.status
                    }
                    for der in user_derivatives
                ]
            },
            "total_portfolio_value": float(total_portfolio_value),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_tokenomics_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get overall tokenomics statistics"""
        
        # Total AETHER distributed
        total_rewards_result = await db.execute(
            select(func.sum(UserAccount.total_rewards_earned))
        )
        total_rewards = total_rewards_result.scalar() or Decimal("0")
        
        # Active NFTs
        active_nfts_result = await db.execute(
            select(func.count(TrafficNFT.id))
            .where(TrafficNFT.status == "active")
        )
        active_nfts = active_nfts_result.scalar()
        
        # Total NFT value
        total_nft_value_result = await db.execute(
            select(func.sum(TrafficNFT.current_value))
            .where(TrafficNFT.current_value.is_not(None))
        )
        total_nft_value = total_nft_value_result.scalar() or Decimal("0")
        
        # Active derivatives
        active_derivatives_result = await db.execute(
            select(func.count(Derivative.id))
            .where(Derivative.status == "active")
        )
        active_derivatives = active_derivatives_result.scalar()
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_rewards_result = await db.execute(
            select(func.count(VehicleData.id))
            .where(
                and_(
                    VehicleData.timestamp >= recent_cutoff,
                    VehicleData.reward_amount.is_not(None)
                )
            )
        )
        recent_reward_events = recent_rewards_result.scalar()
        
        return {
            "total_aether_distributed": float(total_rewards),
            "active_nfts": active_nfts,
            "total_nft_value": float(total_nft_value),
            "active_derivatives": active_derivatives,
            "recent_reward_events_24h": recent_reward_events,
            "tokenomics_health": {
                "reward_distribution_rate": "healthy" if recent_reward_events > 0 else "low",
                "nft_market_activity": "active" if active_nfts > 0 else "inactive",
                "derivative_market": "active" if active_derivatives > 0 else "inactive"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_congestion_multiplier(self, db: AsyncSession) -> Decimal:
        """Get network congestion multiplier for rewards"""
        
        # Get recent traffic data to determine congestion
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        result = await db.execute(
            select(func.avg(VehicleData.speed))
            .where(
                and_(
                    VehicleData.timestamp >= cutoff_time,
                    VehicleData.is_validated == True,
                    VehicleData.speed.is_not(None)
                )
            )
        )
        avg_speed = result.scalar()
        
        if avg_speed is None:
            return Decimal("1.0")  # Default multiplier
        
        # Higher multiplier during congestion (lower speeds)
        if avg_speed < 15:
            return Decimal("1.5")  # High congestion
        elif avg_speed < 30:
            return Decimal("1.2")  # Moderate congestion
        else:
            return Decimal("1.0")  # Low congestion
    
    def _calculate_nft_value(self, performance_metrics: Dict[str, Any]) -> Decimal:
        """Calculate initial NFT value based on performance metrics"""
        
        base_value = Decimal("100.0")  # Base value in AETHER
        
        # Adjust based on performance metrics
        if "efficiency_score" in performance_metrics:
            efficiency = performance_metrics["efficiency_score"]
            base_value *= Decimal(str(max(0.5, min(2.0, efficiency))))
        
        if "traffic_volume" in performance_metrics:
            volume = performance_metrics["traffic_volume"]
            volume_multiplier = Decimal(str(min(1.5, 1.0 + volume / 1000)))
            base_value *= volume_multiplier
        
        return base_value
    
    async def _get_area_congestion_level(
        self,
        db: AsyncSession,
        area_definition: Dict[str, Any]
    ) -> float:
        """Get current congestion level for an area"""
        
        # Get recent vehicle data in the area
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        
        result = await db.execute(
            select(func.avg(VehicleData.speed))
            .where(
                and_(
                    VehicleData.timestamp >= cutoff_time,
                    VehicleData.latitude >= area_definition["min_lat"],
                    VehicleData.latitude <= area_definition["max_lat"],
                    VehicleData.longitude >= area_definition["min_lon"],
                    VehicleData.longitude <= area_definition["max_lon"],
                    VehicleData.is_validated == True,
                    VehicleData.speed.is_not(None)
                )
            )
        )
        avg_speed = result.scalar()
        
        if avg_speed is None:
            return 0.5  # Default moderate congestion
        
        # Convert speed to congestion level (0-1, where 1 is high congestion)
        if avg_speed < 10:
            return 0.9  # High congestion
        elif avg_speed < 25:
            return 0.6  # Moderate congestion
        else:
            return 0.3  # Low congestion
    
    def _calculate_derivative_price(
        self,
        congestion_level: float,
        contract_terms: Dict[str, Any]
    ) -> Decimal:
        """Calculate derivative price based on congestion level"""
        
        base_price = Decimal(str(contract_terms.get("base_price", 10.0)))
        strike_level = contract_terms.get("strike_congestion_level", 0.5)
        
        # Simple pricing model: price increases with congestion deviation from strike
        deviation = abs(congestion_level - strike_level)
        price_multiplier = Decimal(str(1.0 + deviation))
        
        return base_price * price_multiplier
