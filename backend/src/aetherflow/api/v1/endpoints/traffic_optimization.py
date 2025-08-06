"""
Traffic Optimization API Endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from aetherflow.core.database import get_async_session
from aetherflow.models.traffic_lights import TrafficLight, TrafficLightStatus
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class TrafficOptimizationRequest(BaseModel):
    """Traffic optimization request schema"""
    area: str = Field(..., description="Geographic area (e.g., 'Manhattan', 'Downtown')")
    time_window: Optional[str] = Field(None, description="Time window for optimization")
    priority_mode: Optional[bool] = Field(False, description="Emergency vehicle priority")


class TrafficLightSettings(BaseModel):
    """Traffic light settings response schema"""
    intersection_id: str
    red_duration: int
    yellow_duration: int
    green_duration: int
    total_cycle_time: int
    optimization_score: float
    estimated_improvement: str


class OptimizationResult(BaseModel):
    """Traffic optimization result schema"""
    status: str
    area: str
    optimized_intersections: int
    total_intersections: int
    average_improvement: float
    estimated_time_savings: str
    estimated_co2_reduction: str
    settings: List[TrafficLightSettings]


class IntersectionCreate(BaseModel):
    """Create intersection schema"""
    intersection_id: str = Field(..., description="Unique intersection identifier")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: str = Field(..., description="City name")
    red_duration: Optional[int] = Field(30, ge=5, le=300)
    yellow_duration: Optional[int] = Field(5, ge=2, le=15)
    green_duration: Optional[int] = Field(25, ge=10, le=300)


class IntersectionResponse(BaseModel):
    """Intersection response schema"""
    id: int
    intersection_id: str
    latitude: float
    longitude: float
    address: Optional[str]
    city: str
    status: str
    red_duration: int
    yellow_duration: int
    green_duration: int
    is_ai_controlled: bool
    manual_override: bool
    priority_mode: bool
    average_wait_time: float
    throughput_vehicles_per_hour: int
    congestion_score: float
    nft_token_id: Optional[str]
    created_at: str


@router.get("/optimize-traffic", response_model=OptimizationResult)
async def optimize_traffic(
    area: str,
    time_window: Optional[str] = None,
    priority_mode: bool = False,
    db: AsyncSession = Depends(get_async_session)
):
    """Fetch optimized traffic light timings for an area"""
    try:
        from sqlalchemy import select
        
        # Get traffic lights in the specified area
        query = select(TrafficLight).where(TrafficLight.city.ilike(f"%{area}%"))
        result = await db.execute(query)
        traffic_lights = result.scalars().all()
        
        if not traffic_lights:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No traffic lights found in area: {area}"
            )
        
        # Simulate AI optimization
        optimized_settings = []
        total_improvement = 0.0
        
        for light in traffic_lights:
            # Mock AI optimization algorithm
            base_improvement = 0.15  # 15% base improvement
            
            # Calculate optimized timings based on current congestion
            congestion_factor = light.congestion_score
            optimization_multiplier = 1.0 + (congestion_factor * 0.3)
            
            # Adjust timings
            optimized_red = max(15, int(light.red_duration * 0.9))
            optimized_green = min(45, int(light.green_duration * optimization_multiplier))
            optimized_yellow = light.yellow_duration  # Keep yellow constant
            
            improvement_score = base_improvement * optimization_multiplier
            total_improvement += improvement_score
            
            # Apply optimization
            light.apply_ai_optimization({
                "red_duration": optimized_red,
                "yellow_duration": optimized_yellow,
                "green_duration": optimized_green
            })
            
            # Update congestion score (simulate improvement)
            light.congestion_score = max(0.0, light.congestion_score - improvement_score)
            
            optimized_settings.append(TrafficLightSettings(
                intersection_id=light.intersection_id,
                red_duration=optimized_red,
                yellow_duration=optimized_yellow,
                green_duration=optimized_green,
                total_cycle_time=optimized_red + optimized_yellow + optimized_green,
                optimization_score=improvement_score,
                estimated_improvement=f"{improvement_score*100:.1f}% faster"
            ))
        
        # Commit changes
        await db.commit()
        
        average_improvement = total_improvement / len(traffic_lights)
        
        # Calculate estimated benefits
        time_savings_minutes = len(traffic_lights) * average_improvement * 2.5  # 2.5 min per intersection
        co2_reduction_kg = time_savings_minutes * 0.2  # 0.2 kg CO2 per minute saved
        
        logger.info(f"Optimized {len(traffic_lights)} intersections in {area}")
        
        return OptimizationResult(
            status="success",
            area=area,
            optimized_intersections=len(traffic_lights),
            total_intersections=len(traffic_lights),
            average_improvement=average_improvement,
            estimated_time_savings=f"{time_savings_minutes:.1f} minutes per day",
            estimated_co2_reduction=f"{co2_reduction_kg:.1f} kg per day",
            settings=optimized_settings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to optimize traffic for area {area}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize traffic"
        )


@router.post("/intersections", response_model=Dict[str, Any])
async def create_intersection(
    intersection: IntersectionCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new traffic intersection"""
    try:
        from sqlalchemy import select
        
        # Check if intersection already exists
        existing_query = select(TrafficLight).where(
            TrafficLight.intersection_id == intersection.intersection_id
        )
        result = await db.execute(existing_query)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Intersection already exists"
            )
        
        # Create new intersection
        traffic_light = TrafficLight(
            intersection_id=intersection.intersection_id,
            latitude=intersection.latitude,
            longitude=intersection.longitude,
            address=intersection.address,
            city=intersection.city,
            red_duration=intersection.red_duration,
            yellow_duration=intersection.yellow_duration,
            green_duration=intersection.green_duration,
            status=TrafficLightStatus.RED
        )
        
        db.add(traffic_light)
        await db.commit()
        await db.refresh(traffic_light)
        
        logger.info(f"Created intersection: {intersection.intersection_id}")
        
        return {
            "status": "success",
            "intersection_id": traffic_light.intersection_id,
            "id": traffic_light.id,
            "message": "Intersection created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create intersection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create intersection"
        )


@router.get("/intersections", response_model=List[IntersectionResponse])
async def get_intersections(
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Get traffic intersections"""
    try:
        from sqlalchemy import select
        
        query = select(TrafficLight).offset(skip).limit(limit)
        
        if city:
            query = query.where(TrafficLight.city.ilike(f"%{city}%"))
        
        result = await db.execute(query)
        intersections = result.scalars().all()
        
        return [
            IntersectionResponse(
                id=intersection.id,
                intersection_id=intersection.intersection_id,
                latitude=intersection.latitude,
                longitude=intersection.longitude,
                address=intersection.address,
                city=intersection.city,
                status=intersection.status,
                red_duration=intersection.red_duration,
                yellow_duration=intersection.yellow_duration,
                green_duration=intersection.green_duration,
                is_ai_controlled=intersection.is_ai_controlled,
                manual_override=intersection.manual_override,
                priority_mode=intersection.priority_mode,
                average_wait_time=intersection.average_wait_time,
                throughput_vehicles_per_hour=intersection.throughput_vehicles_per_hour,
                congestion_score=intersection.congestion_score,
                nft_token_id=intersection.nft_token_id,
                created_at=intersection.created_at.isoformat()
            )
            for intersection in intersections
        ]
        
    except Exception as e:
        logger.error(f"Failed to get intersections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve intersections"
        )


@router.post("/intersections/{intersection_id}/control")
async def control_traffic_light(
    intersection_id: str,
    new_status: TrafficLightStatus,
    duration: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Manually control traffic light status"""
    try:
        from sqlalchemy import select
        
        query = select(TrafficLight).where(TrafficLight.intersection_id == intersection_id)
        result = await db.execute(query)
        traffic_light = result.scalar_one_or_none()
        
        if not traffic_light:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intersection not found"
            )
        
        # Update status
        traffic_light.update_status(new_status)
        traffic_light.manual_override = True
        
        # Update duration if provided
        if duration:
            if new_status == TrafficLightStatus.RED:
                traffic_light.red_duration = duration
            elif new_status == TrafficLightStatus.GREEN:
                traffic_light.green_duration = duration
            elif new_status == TrafficLightStatus.YELLOW:
                traffic_light.yellow_duration = duration
        
        await db.commit()
        
        logger.info(f"Traffic light {intersection_id} status changed to {new_status}")
        
        return {
            "status": "success",
            "intersection_id": intersection_id,
            "new_status": new_status,
            "duration": duration,
            "message": "Traffic light status updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control traffic light {intersection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to control traffic light"
        )


@router.get("/intersections/{intersection_id}/analytics")
async def get_intersection_analytics(
    intersection_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Get analytics for a specific intersection"""
    try:
        from sqlalchemy import select
        
        query = select(TrafficLight).where(TrafficLight.intersection_id == intersection_id)
        result = await db.execute(query)
        traffic_light = result.scalar_one_or_none()
        
        if not traffic_light:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intersection not found"
            )
        
        # Mock analytics data
        analytics = {
            "intersection_id": intersection_id,
            "current_status": traffic_light.status,
            "performance_metrics": {
                "average_wait_time": traffic_light.average_wait_time,
                "throughput_vehicles_per_hour": traffic_light.throughput_vehicles_per_hour,
                "congestion_score": traffic_light.congestion_score,
                "optimization_score": traffic_light.optimized_timing.get("optimization_score", 0.0) if traffic_light.optimized_timing else 0.0
            },
            "timing_configuration": {
                "red_duration": traffic_light.red_duration,
                "yellow_duration": traffic_light.yellow_duration,
                "green_duration": traffic_light.green_duration,
                "total_cycle_time": traffic_light.total_cycle_time
            },
            "ai_optimization": {
                "is_ai_controlled": traffic_light.is_ai_controlled,
                "last_optimization": traffic_light.last_optimization.isoformat() if traffic_light.last_optimization else None,
                "optimization_history": traffic_light.optimized_timing
            },
            "nft_integration": {
                "nft_token_id": traffic_light.nft_token_id,
                "nft_owner": traffic_light.nft_owner
            }
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for intersection {intersection_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve intersection analytics"
        )
