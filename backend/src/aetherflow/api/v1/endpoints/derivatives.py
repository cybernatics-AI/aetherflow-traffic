"""
Derivatives API Endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

from aetherflow.core.database import get_db_session
from aetherflow.core.logging import get_logger
from aetherflow.models.derivatives import Derivative
from aetherflow.services.tokenomics_service import TokenomicsService
from aetherflow.hedera.client import get_hedera_client

logger = get_logger(__name__)
router = APIRouter(prefix="/derivatives", tags=["derivatives"])


# Pydantic models
class DerivativeCreate(BaseModel):
    derivative_type: str = "congestion"
    area_definition: Dict[str, Any]
    contract_terms: Dict[str, Any]
    creator_account_id: str


class DerivativeResponse(BaseModel):
    id: int
    derivative_type: str
    underlying_asset: str
    contract_terms: Dict[str, Any]
    creator_account_id: str
    current_price: Optional[float]
    status: str
    creation_date: str
    expiration_date: str
    last_price_update: Optional[str]
    pricing_history: Optional[List[Dict[str, Any]]]
    settlement_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


@router.post("/", response_model=DerivativeResponse, status_code=status.HTTP_201_CREATED)
async def create_derivative(
    derivative_data: DerivativeCreate,
    db: AsyncSession = Depends(get_db_session),
    hedera_client = Depends(get_hedera_client)
):
    """Create a new derivative contract"""
    
    try:
        tokenomics_service = TokenomicsService(hedera_client)
        
        result = await tokenomics_service.create_congestion_derivative(
            db=db,
            area_definition=derivative_data.area_definition,
            contract_terms=derivative_data.contract_terms,
            creator_account_id=derivative_data.creator_account_id
        )
        
        # Get the created derivative
        from sqlalchemy import select
        derivative_result = await db.execute(
            select(Derivative).where(Derivative.id == result["derivative_id"])
        )
        derivative = derivative_result.scalar_one()
        
        return DerivativeResponse(
            id=derivative.id,
            derivative_type=derivative.derivative_type,
            underlying_asset=derivative.underlying_asset,
            contract_terms=derivative.contract_terms,
            creator_account_id=derivative.creator_account_id,
            current_price=float(derivative.current_price or 0),
            status=derivative.status,
            creation_date=derivative.creation_date.isoformat(),
            expiration_date=derivative.expiration_date.isoformat(),
            last_price_update=derivative.last_price_update.isoformat() if derivative.last_price_update else None,
            pricing_history=derivative.pricing_history,
            settlement_data=derivative.settlement_data
        )
        
    except Exception as e:
        logger.error(f"Failed to create derivative: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create derivative"
        )


@router.get("/{derivative_id}", response_model=DerivativeResponse)
async def get_derivative(
    derivative_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get derivative by ID"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(Derivative).where(Derivative.id == derivative_id)
        )
        derivative = result.scalar_one_or_none()
        
        if not derivative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Derivative not found"
            )
        
        return DerivativeResponse(
            id=derivative.id,
            derivative_type=derivative.derivative_type,
            underlying_asset=derivative.underlying_asset,
            contract_terms=derivative.contract_terms,
            creator_account_id=derivative.creator_account_id,
            current_price=float(derivative.current_price or 0),
            status=derivative.status,
            creation_date=derivative.creation_date.isoformat(),
            expiration_date=derivative.expiration_date.isoformat(),
            last_price_update=derivative.last_price_update.isoformat() if derivative.last_price_update else None,
            pricing_history=derivative.pricing_history,
            settlement_data=derivative.settlement_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get derivative: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve derivative"
        )


@router.get("/", response_model=List[DerivativeResponse])
async def list_derivatives(
    limit: int = 100,
    offset: int = 0,
    derivative_type: Optional[str] = None,
    status: Optional[str] = None,
    creator_account_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List derivatives with pagination and filters"""
    
    try:
        from sqlalchemy import select
        
        query = select(Derivative)
        
        if derivative_type:
            query = query.where(Derivative.derivative_type == derivative_type)
        
        if status:
            query = query.where(Derivative.status == status)
        
        if creator_account_id:
            query = query.where(Derivative.creator_account_id == creator_account_id)
        
        query = query.order_by(Derivative.creation_date.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        derivatives = result.scalars().all()
        
        return [
            DerivativeResponse(
                id=derivative.id,
                derivative_type=derivative.derivative_type,
                underlying_asset=derivative.underlying_asset,
                contract_terms=derivative.contract_terms,
                creator_account_id=derivative.creator_account_id,
                current_price=float(derivative.current_price or 0),
                status=derivative.status,
                creation_date=derivative.creation_date.isoformat(),
                expiration_date=derivative.expiration_date.isoformat(),
                last_price_update=derivative.last_price_update.isoformat() if derivative.last_price_update else None,
                pricing_history=derivative.pricing_history,
                settlement_data=derivative.settlement_data
            )
            for derivative in derivatives
        ]
        
    except Exception as e:
        logger.error(f"Failed to list derivatives: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list derivatives"
        )


@router.post("/{derivative_id}/update-pricing")
async def update_derivative_pricing(
    derivative_id: int,
    db: AsyncSession = Depends(get_db_session),
    hedera_client = Depends(get_hedera_client)
):
    """Update derivative pricing based on current market conditions"""
    
    try:
        tokenomics_service = TokenomicsService(hedera_client)
        
        result = await tokenomics_service.update_derivative_pricing(
            db=db,
            derivative_id=derivative_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update derivative pricing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update derivative pricing"
        )


@router.get("/{derivative_id}/pricing-history")
async def get_pricing_history(
    derivative_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get pricing history for a derivative"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(Derivative).where(Derivative.id == derivative_id)
        )
        derivative = result.scalar_one_or_none()
        
        if not derivative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Derivative not found"
            )
        
        pricing_history = derivative.pricing_history or []
        
        # Limit the history if needed
        if len(pricing_history) > limit:
            pricing_history = pricing_history[-limit:]
        
        return {
            "derivative_id": derivative_id,
            "pricing_history": pricing_history,
            "current_price": float(derivative.current_price or 0),
            "total_records": len(pricing_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pricing history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pricing history"
        )


@router.post("/{derivative_id}/settle")
async def settle_derivative(
    derivative_id: int,
    settlement_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session)
):
    """Settle a derivative contract"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(Derivative).where(Derivative.id == derivative_id)
        )
        derivative = result.scalar_one_or_none()
        
        if not derivative:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Derivative not found"
            )
        
        if derivative.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Derivative is not active"
            )
        
        # Update derivative with settlement data
        derivative.status = "settled"
        derivative.settlement_data = settlement_data
        
        await db.commit()
        
        logger.info(f"Settled derivative {derivative_id}")
        
        return {
            "derivative_id": derivative_id,
            "status": "settled",
            "settlement_data": settlement_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to settle derivative: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to settle derivative"
        )


@router.get("/market/active")
async def get_active_derivatives(
    limit: int = 50,
    derivative_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Get active derivatives for trading"""
    
    try:
        from sqlalchemy import select, and_
        
        query = select(Derivative).where(
            and_(
                Derivative.status == "active",
                Derivative.expiration_date > datetime.utcnow()
            )
        )
        
        if derivative_type:
            query = query.where(Derivative.derivative_type == derivative_type)
        
        query = query.order_by(Derivative.current_price.desc()).limit(limit)
        
        result = await db.execute(query)
        derivatives = result.scalars().all()
        
        active_derivatives = []
        for derivative in derivatives:
            import json
            area_definition = json.loads(derivative.underlying_asset)
            
            active_derivatives.append({
                "derivative_id": derivative.id,
                "derivative_type": derivative.derivative_type,
                "area_definition": area_definition,
                "current_price": float(derivative.current_price or 0),
                "contract_terms": derivative.contract_terms,
                "expiration_date": derivative.expiration_date.isoformat(),
                "time_to_expiry_hours": (derivative.expiration_date - datetime.utcnow()).total_seconds() / 3600,
                "creator_account_id": derivative.creator_account_id
            })
        
        return {
            "active_derivatives": active_derivatives,
            "total_count": len(active_derivatives)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active derivatives: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active derivatives"
        )


@router.get("/stats/overview")
async def get_derivatives_statistics(
    db: AsyncSession = Depends(get_db_session)
):
    """Get derivatives market statistics"""
    
    try:
        from sqlalchemy import select, func
        
        # Total derivatives
        total_result = await db.execute(select(func.count(Derivative.id)))
        total_derivatives = total_result.scalar()
        
        # Active derivatives
        active_result = await db.execute(
            select(func.count(Derivative.id))
            .where(Derivative.status == "active")
        )
        active_derivatives = active_result.scalar()
        
        # Settled derivatives
        settled_result = await db.execute(
            select(func.count(Derivative.id))
            .where(Derivative.status == "settled")
        )
        settled_derivatives = settled_result.scalar()
        
        # Total market value
        total_value_result = await db.execute(
            select(func.sum(Derivative.current_price))
            .where(Derivative.current_price.is_not(None))
        )
        total_value = total_value_result.scalar() or 0
        
        # Derivatives by type
        type_result = await db.execute(
            select(Derivative.derivative_type, func.count(Derivative.id))
            .group_by(Derivative.derivative_type)
        )
        derivatives_by_type = dict(type_result.all())
        
        return {
            "total_derivatives": total_derivatives,
            "active_derivatives": active_derivatives,
            "settled_derivatives": settled_derivatives,
            "total_market_value": float(total_value),
            "derivatives_by_type": derivatives_by_type,
            "settlement_rate": settled_derivatives / total_derivatives if total_derivatives > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get derivatives statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve derivatives statistics"
        )


@router.get("/analytics/congestion-trends")
async def get_congestion_trends(
    area_bounds: Optional[Dict[str, float]] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db_session)
):
    """Get congestion trends for derivative pricing"""
    
    try:
        from datetime import timedelta
        from sqlalchemy import select, and_
        from aetherflow.models.vehicle_data import VehicleData
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Get vehicle data for trend analysis
        query = select(VehicleData).where(
            and_(
                VehicleData.timestamp >= cutoff_time,
                VehicleData.is_validated == True,
                VehicleData.speed.is_not(None)
            )
        )
        
        if area_bounds:
            query = query.where(
                and_(
                    VehicleData.latitude >= area_bounds["min_lat"],
                    VehicleData.latitude <= area_bounds["max_lat"],
                    VehicleData.longitude >= area_bounds["min_lon"],
                    VehicleData.longitude <= area_bounds["max_lon"]
                )
            )
        
        result = await db.execute(query)
        vehicle_data = result.scalars().all()
        
        if not vehicle_data:
            return {
                "message": "No vehicle data available for trend analysis",
                "days": days,
                "area_bounds": area_bounds
            }
        
        # Calculate daily congestion levels
        daily_congestion = {}
        for vd in vehicle_data:
            day_key = vd.timestamp.date().isoformat()
            if day_key not in daily_congestion:
                daily_congestion[day_key] = []
            daily_congestion[day_key].append(vd.speed)
        
        # Calculate average speeds and congestion levels
        trends = []
        for day, speeds in daily_congestion.items():
            avg_speed = sum(speeds) / len(speeds)
            
            # Convert to congestion level (0-1, where 1 is high congestion)
            if avg_speed < 15:
                congestion_level = 0.8
            elif avg_speed < 30:
                congestion_level = 0.5
            else:
                congestion_level = 0.2
            
            trends.append({
                "date": day,
                "average_speed": round(avg_speed, 2),
                "congestion_level": congestion_level,
                "data_points": len(speeds)
            })
        
        # Sort by date
        trends.sort(key=lambda x: x["date"])
        
        return {
            "trends": trends,
            "analysis_period_days": days,
            "area_bounds": area_bounds,
            "total_data_points": len(vehicle_data),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get congestion trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve congestion trends"
        )
