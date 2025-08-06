"""
Traffic NFTs API Endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal

from aetherflow.core.database import get_db_session
from aetherflow.core.logging import get_logger
from aetherflow.models.traffic_nfts import TrafficNFT
from aetherflow.services.tokenomics_service import TokenomicsService
from aetherflow.hedera.client import get_hedera_client

logger = get_logger(__name__)
router = APIRouter(prefix="/traffic-nfts", tags=["traffic-nfts"])


# Pydantic models
class TrafficNFTCreate(BaseModel):
    intersection_id: str
    owner_account_id: str
    performance_metrics: Dict[str, Any]
    pricing_model: Dict[str, Any]


class TrafficNFTResponse(BaseModel):
    id: int
    intersection_id: str
    owner_account_id: str
    token_id: Optional[str]
    current_value: Optional[float]
    performance_metrics: Optional[Dict[str, Any]]
    pricing_model: Optional[Dict[str, Any]]
    status: str
    total_revenue_generated: Optional[float]
    creation_date: str
    last_revenue_distribution: Optional[str]

    class Config:
        from_attributes = True


class RevenueShareRequest(BaseModel):
    total_revenue: float
    period_days: int = 30


@router.post("/", response_model=TrafficNFTResponse, status_code=status.HTTP_201_CREATED)
async def create_traffic_nft(
    nft_data: TrafficNFTCreate,
    db: AsyncSession = Depends(get_db_session),
    hedera_client = Depends(get_hedera_client)
):
    """Create a new Traffic NFT"""
    
    try:
        tokenomics_service = TokenomicsService(hedera_client)
        
        result = await tokenomics_service.create_traffic_nft(
            db=db,
            intersection_id=nft_data.intersection_id,
            owner_account_id=nft_data.owner_account_id,
            performance_metrics=nft_data.performance_metrics,
            pricing_model=nft_data.pricing_model
        )
        
        # Get the created NFT
        from sqlalchemy import select
        nft_result = await db.execute(
            select(TrafficNFT).where(TrafficNFT.id == result["nft_id"])
        )
        nft = nft_result.scalar_one()
        
        return TrafficNFTResponse(
            id=nft.id,
            intersection_id=nft.intersection_id,
            owner_account_id=nft.owner_account_id,
            token_id=nft.token_id,
            current_value=float(nft.current_value or 0),
            performance_metrics=nft.performance_metrics,
            pricing_model=nft.pricing_model,
            status=nft.status,
            total_revenue_generated=float(nft.total_revenue_generated or 0),
            creation_date=nft.creation_date.isoformat(),
            last_revenue_distribution=nft.last_revenue_distribution.isoformat() if nft.last_revenue_distribution else None
        )
        
    except Exception as e:
        logger.error(f"Failed to create Traffic NFT: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Traffic NFT"
        )


@router.get("/{nft_id}", response_model=TrafficNFTResponse)
async def get_traffic_nft(
    nft_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get Traffic NFT by ID"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(TrafficNFT).where(TrafficNFT.id == nft_id)
        )
        nft = result.scalar_one_or_none()
        
        if not nft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Traffic NFT not found"
            )
        
        return TrafficNFTResponse(
            id=nft.id,
            intersection_id=nft.intersection_id,
            owner_account_id=nft.owner_account_id,
            token_id=nft.token_id,
            current_value=float(nft.current_value or 0),
            performance_metrics=nft.performance_metrics,
            pricing_model=nft.pricing_model,
            status=nft.status,
            total_revenue_generated=float(nft.total_revenue_generated or 0),
            creation_date=nft.creation_date.isoformat(),
            last_revenue_distribution=nft.last_revenue_distribution.isoformat() if nft.last_revenue_distribution else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Traffic NFT: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Traffic NFT"
        )


@router.get("/", response_model=List[TrafficNFTResponse])
async def list_traffic_nfts(
    limit: int = 100,
    offset: int = 0,
    owner_account_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List Traffic NFTs with pagination and filters"""
    
    try:
        from sqlalchemy import select
        
        query = select(TrafficNFT)
        
        if owner_account_id:
            query = query.where(TrafficNFT.owner_account_id == owner_account_id)
        
        if status:
            query = query.where(TrafficNFT.status == status)
        
        query = query.order_by(TrafficNFT.creation_date.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        nfts = result.scalars().all()
        
        return [
            TrafficNFTResponse(
                id=nft.id,
                intersection_id=nft.intersection_id,
                owner_account_id=nft.owner_account_id,
                token_id=nft.token_id,
                current_value=float(nft.current_value or 0),
                performance_metrics=nft.performance_metrics,
                pricing_model=nft.pricing_model,
                status=nft.status,
                total_revenue_generated=float(nft.total_revenue_generated or 0),
                creation_date=nft.creation_date.isoformat(),
                last_revenue_distribution=nft.last_revenue_distribution.isoformat() if nft.last_revenue_distribution else None
            )
            for nft in nfts
        ]
        
    except Exception as e:
        logger.error(f"Failed to list Traffic NFTs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list Traffic NFTs"
        )


@router.post("/{nft_id}/revenue-share")
async def calculate_revenue_share(
    nft_id: int,
    revenue_data: RevenueShareRequest,
    db: AsyncSession = Depends(get_db_session),
    hedera_client = Depends(get_hedera_client)
):
    """Calculate and distribute revenue share for Traffic NFT"""
    
    try:
        tokenomics_service = TokenomicsService(hedera_client)
        
        result = await tokenomics_service.calculate_nft_revenue_share(
            db=db,
            nft_id=nft_id,
            total_revenue=Decimal(str(revenue_data.total_revenue)),
            period_days=revenue_data.period_days
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to calculate revenue share: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate revenue share"
        )


@router.get("/intersection/{intersection_id}", response_model=TrafficNFTResponse)
async def get_nft_by_intersection(
    intersection_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get Traffic NFT by intersection ID"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(TrafficNFT).where(TrafficNFT.intersection_id == intersection_id)
        )
        nft = result.scalar_one_or_none()
        
        if not nft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Traffic NFT not found for intersection"
            )
        
        return TrafficNFTResponse(
            id=nft.id,
            intersection_id=nft.intersection_id,
            owner_account_id=nft.owner_account_id,
            token_id=nft.token_id,
            current_value=float(nft.current_value or 0),
            performance_metrics=nft.performance_metrics,
            pricing_model=nft.pricing_model,
            status=nft.status,
            total_revenue_generated=float(nft.total_revenue_generated or 0),
            creation_date=nft.creation_date.isoformat(),
            last_revenue_distribution=nft.last_revenue_distribution.isoformat() if nft.last_revenue_distribution else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Traffic NFT by intersection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Traffic NFT"
        )


@router.put("/{nft_id}/performance")
async def update_nft_performance(
    nft_id: int,
    performance_metrics: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session)
):
    """Update Traffic NFT performance metrics"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(TrafficNFT).where(TrafficNFT.id == nft_id)
        )
        nft = result.scalar_one_or_none()
        
        if not nft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Traffic NFT not found"
            )
        
        # Update performance metrics
        nft.performance_metrics = performance_metrics
        
        # Recalculate value based on new metrics
        tokenomics_service = TokenomicsService()
        new_value = tokenomics_service._calculate_nft_value(performance_metrics)
        nft.current_value = new_value
        
        await db.commit()
        await db.refresh(nft)
        
        logger.info(f"Updated performance metrics for NFT {nft_id}")
        
        return {
            "nft_id": nft_id,
            "performance_metrics": performance_metrics,
            "new_value": float(new_value),
            "timestamp": nft.creation_date.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update NFT performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update NFT performance"
        )


@router.get("/stats/overview")
async def get_nft_statistics(
    db: AsyncSession = Depends(get_db_session)
):
    """Get Traffic NFT statistics overview"""
    
    try:
        from sqlalchemy import select, func
        from datetime import datetime
        
        # Total NFTs
        total_result = await db.execute(select(func.count(TrafficNFT.id)))
        total_nfts = total_result.scalar()
        
        # Active NFTs
        active_result = await db.execute(
            select(func.count(TrafficNFT.id))
            .where(TrafficNFT.status == "active")
        )
        active_nfts = active_result.scalar()
        
        # Total value
        total_value_result = await db.execute(
            select(func.sum(TrafficNFT.current_value))
            .where(TrafficNFT.current_value.is_not(None))
        )
        total_value = total_value_result.scalar() or 0
        
        # Total revenue generated
        total_revenue_result = await db.execute(
            select(func.sum(TrafficNFT.total_revenue_generated))
            .where(TrafficNFT.total_revenue_generated.is_not(None))
        )
        total_revenue = total_revenue_result.scalar() or 0
        
        # Average value
        avg_value = float(total_value) / total_nfts if total_nfts > 0 else 0
        
        return {
            "total_nfts": total_nfts,
            "active_nfts": active_nfts,
            "total_market_value": float(total_value),
            "total_revenue_generated": float(total_revenue),
            "average_nft_value": round(avg_value, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get NFT statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve NFT statistics"
        )


@router.get("/marketplace/listings")
async def get_marketplace_listings(
    limit: int = 50,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get NFT marketplace listings"""
    
    try:
        from sqlalchemy import select, and_
        
        query = select(TrafficNFT).where(TrafficNFT.status == "active")
        
        if min_price is not None:
            query = query.where(TrafficNFT.current_value >= min_price)
        
        if max_price is not None:
            query = query.where(TrafficNFT.current_value <= max_price)
        
        query = query.order_by(TrafficNFT.current_value.desc()).limit(limit)
        
        result = await db.execute(query)
        nfts = result.scalars().all()
        
        listings = []
        for nft in nfts:
            listings.append({
                "nft_id": nft.id,
                "intersection_id": nft.intersection_id,
                "current_value": float(nft.current_value or 0),
                "performance_metrics": nft.performance_metrics,
                "total_revenue": float(nft.total_revenue_generated or 0),
                "owner_account_id": nft.owner_account_id,
                "creation_date": nft.creation_date.isoformat()
            })
        
        return {
            "listings": listings,
            "total_count": len(listings),
            "filters": {
                "min_price": min_price,
                "max_price": max_price
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get marketplace listings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve marketplace listings"
        )
