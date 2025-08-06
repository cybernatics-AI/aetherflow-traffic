"""
Traffic Service - Business Logic for Traffic Management and Optimization
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from aetherflow.core.logging import get_logger
from aetherflow.models.traffic_lights import TrafficLight
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.ai.traffic_optimizer import TrafficOptimizer
from aetherflow.hedera.client import HederaClient

logger = get_logger(__name__)


class TrafficService:
    """Service for traffic management and optimization"""
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera_client = hedera_client
        self.traffic_optimizer = TrafficOptimizer()
        
    async def register_traffic_light(
        self,
        db: AsyncSession,
        intersection_id: str,
        latitude: float,
        longitude: float,
        light_phases: List[str],
        current_phase: str = "red",
        timing_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a new traffic light"""
        
        logger.info(f"Registering traffic light at intersection {intersection_id}")
        
        # Create traffic light record
        traffic_light = TrafficLight(
            intersection_id=intersection_id,
            latitude=latitude,
            longitude=longitude,
            light_phases=light_phases,
            current_phase=current_phase,
            timing_config=timing_config or {},
            status="active",
            installation_date=datetime.utcnow()
        )
        
        # Save to database
        db.add(traffic_light)
        await db.commit()
        await db.refresh(traffic_light)
        
        logger.info(f"Traffic light registered: ID {traffic_light.id}")
        
        return {
            "light_id": traffic_light.id,
            "intersection_id": intersection_id,
            "status": traffic_light.status,
            "current_phase": current_phase,
            "timestamp": traffic_light.installation_date.isoformat()
        }
    
    async def get_traffic_light(
        self,
        db: AsyncSession,
        light_id: int
    ) -> Optional[TrafficLight]:
        """Get traffic light by ID"""
        
        result = await db.execute(
            select(TrafficLight).where(TrafficLight.id == light_id)
        )
        return result.scalar_one_or_none()
    
    async def get_traffic_lights_in_area(
        self,
        db: AsyncSession,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> List[TrafficLight]:
        """Get traffic lights within a geographic area"""
        
        result = await db.execute(
            select(TrafficLight)
            .where(
                and_(
                    TrafficLight.latitude >= min_lat,
                    TrafficLight.latitude <= max_lat,
                    TrafficLight.longitude >= min_lon,
                    TrafficLight.longitude <= max_lon,
                    TrafficLight.status == "active"
                )
            )
        )
        return result.scalars().all()
    
    async def optimize_intersection(
        self,
        db: AsyncSession,
        intersection_id: str,
        time_window_minutes: int = 30
    ) -> Dict[str, Any]:
        """Optimize traffic light timing for an intersection"""
        
        # Get traffic light
        result = await db.execute(
            select(TrafficLight).where(TrafficLight.intersection_id == intersection_id)
        )
        traffic_light = result.scalar_one_or_none()
        
        if not traffic_light:
            raise ValueError(f"Traffic light not found for intersection {intersection_id}")
        
        # Get recent vehicle data near the intersection
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        # Define area around intersection (roughly 200m radius)
        lat_delta = 0.002  # Approximately 200m
        lon_delta = 0.002
        
        vehicle_data_result = await db.execute(
            select(VehicleData)
            .where(
                and_(
                    VehicleData.timestamp >= cutoff_time,
                    VehicleData.latitude >= traffic_light.latitude - lat_delta,
                    VehicleData.latitude <= traffic_light.latitude + lat_delta,
                    VehicleData.longitude >= traffic_light.longitude - lon_delta,
                    VehicleData.longitude <= traffic_light.longitude + lon_delta,
                    VehicleData.is_validated == True
                )
            )
        )
        vehicle_data = vehicle_data_result.scalars().all()
        
        # Use AI optimizer to calculate optimal timing
        optimization_result = await self.traffic_optimizer.optimize_intersection(
            intersection_id=intersection_id,
            vehicle_data=vehicle_data,
            current_timing=traffic_light.timing_config
        )
        
        # Update traffic light with new timing
        traffic_light.timing_config = optimization_result["optimal_timing"]
        traffic_light.ai_optimization_data = optimization_result
        traffic_light.last_optimization = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Optimized intersection {intersection_id}: "
                   f"improvement={optimization_result.get('improvement_percentage', 0):.1f}%")
        
        return {
            "intersection_id": intersection_id,
            "optimization_result": optimization_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def optimize_corridor(
        self,
        db: AsyncSession,
        corridor_intersections: List[str],
        time_window_minutes: int = 30
    ) -> Dict[str, Any]:
        """Optimize multiple intersections as a corridor"""
        
        logger.info(f"Optimizing corridor with {len(corridor_intersections)} intersections")
        
        # Get all traffic lights in corridor
        traffic_lights = []
        for intersection_id in corridor_intersections:
            result = await db.execute(
                select(TrafficLight).where(TrafficLight.intersection_id == intersection_id)
            )
            light = result.scalar_one_or_none()
            if light:
                traffic_lights.append(light)
        
        if not traffic_lights:
            raise ValueError("No traffic lights found for corridor")
        
        # Get vehicle data for entire corridor area
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        # Calculate bounding box for all intersections
        min_lat = min(light.latitude for light in traffic_lights) - 0.005
        max_lat = max(light.latitude for light in traffic_lights) + 0.005
        min_lon = min(light.longitude for light in traffic_lights) - 0.005
        max_lon = max(light.longitude for light in traffic_lights) + 0.005
        
        vehicle_data_result = await db.execute(
            select(VehicleData)
            .where(
                and_(
                    VehicleData.timestamp >= cutoff_time,
                    VehicleData.latitude >= min_lat,
                    VehicleData.latitude <= max_lat,
                    VehicleData.longitude >= min_lon,
                    VehicleData.longitude <= max_lon,
                    VehicleData.is_validated == True
                )
            )
        )
        vehicle_data = vehicle_data_result.scalars().all()
        
        # Use AI optimizer for corridor optimization
        corridor_result = await self.traffic_optimizer.optimize_corridor(
            intersections=[light.intersection_id for light in traffic_lights],
            vehicle_data=vehicle_data,
            current_timings={light.intersection_id: light.timing_config for light in traffic_lights}
        )
        
        # Update all traffic lights with new timings
        updated_lights = []
        for light in traffic_lights:
            if light.intersection_id in corridor_result["optimal_timings"]:
                light.timing_config = corridor_result["optimal_timings"][light.intersection_id]
                light.ai_optimization_data = corridor_result
                light.last_optimization = datetime.utcnow()
                updated_lights.append(light.intersection_id)
        
        await db.commit()
        
        logger.info(f"Optimized corridor: {len(updated_lights)} intersections updated")
        
        return {
            "corridor_intersections": corridor_intersections,
            "updated_intersections": updated_lights,
            "optimization_result": corridor_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def update_traffic_light_phase(
        self,
        db: AsyncSession,
        light_id: int,
        new_phase: str
    ) -> Dict[str, Any]:
        """Update traffic light phase"""
        
        traffic_light = await self.get_traffic_light(db, light_id)
        if not traffic_light:
            raise ValueError(f"Traffic light {light_id} not found")
        
        if new_phase not in traffic_light.light_phases:
            raise ValueError(f"Invalid phase {new_phase} for traffic light {light_id}")
        
        old_phase = traffic_light.current_phase
        traffic_light.current_phase = new_phase
        traffic_light.last_phase_change = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Traffic light {light_id} phase changed: {old_phase} -> {new_phase}")
        
        return {
            "light_id": light_id,
            "old_phase": old_phase,
            "new_phase": new_phase,
            "timestamp": traffic_light.last_phase_change.isoformat()
        }
    
    async def get_traffic_analytics(
        self,
        db: AsyncSession,
        area_bounds: Optional[Dict[str, float]] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get traffic analytics for an area"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Get vehicle data
        vehicle_query = select(VehicleData).where(
            and_(
                VehicleData.timestamp >= cutoff_time,
                VehicleData.is_validated == True
            )
        )
        
        if area_bounds:
            vehicle_query = vehicle_query.where(
                and_(
                    VehicleData.latitude >= area_bounds["min_lat"],
                    VehicleData.latitude <= area_bounds["max_lat"],
                    VehicleData.longitude >= area_bounds["min_lon"],
                    VehicleData.longitude <= area_bounds["max_lon"]
                )
            )
        
        vehicle_result = await db.execute(vehicle_query)
        vehicle_data = vehicle_result.scalars().all()
        
        # Get traffic lights in area
        if area_bounds:
            lights_result = await db.execute(
                select(TrafficLight)
                .where(
                    and_(
                        TrafficLight.latitude >= area_bounds["min_lat"],
                        TrafficLight.latitude <= area_bounds["max_lat"],
                        TrafficLight.longitude >= area_bounds["min_lon"],
                        TrafficLight.longitude <= area_bounds["max_lon"],
                        TrafficLight.status == "active"
                    )
                )
            )
        else:
            lights_result = await db.execute(
                select(TrafficLight).where(TrafficLight.status == "active")
            )
        
        traffic_lights = lights_result.scalars().all()
        
        # Calculate analytics
        if not vehicle_data:
            return {
                "message": "No vehicle data available for analysis",
                "traffic_lights_count": len(traffic_lights),
                "time_window_hours": time_window_hours
            }
        
        # Traffic flow metrics
        unique_vehicles = len(set(vd.vehicle_id for vd in vehicle_data))
        speeds = [vd.speed for vd in vehicle_data if vd.speed is not None]
        avg_speed = sum(speeds) / len(speeds) if speeds else 0
        
        # Congestion analysis
        congestion_levels = []
        for speed in speeds:
            if speed < 15:
                congestion_levels.append("high")
            elif speed < 35:
                congestion_levels.append("moderate")
            else:
                congestion_levels.append("low")
        
        congestion_distribution = {
            level: congestion_levels.count(level) / len(congestion_levels)
            for level in ["low", "moderate", "high"]
        } if congestion_levels else {}
        
        # Traffic light performance
        optimized_lights = sum(1 for light in traffic_lights if light.last_optimization)
        
        return {
            "time_window_hours": time_window_hours,
            "area_bounds": area_bounds,
            "vehicle_metrics": {
                "total_data_points": len(vehicle_data),
                "unique_vehicles": unique_vehicles,
                "average_speed": round(avg_speed, 2),
                "speed_range": {
                    "min": min(speeds) if speeds else 0,
                    "max": max(speeds) if speeds else 0
                }
            },
            "congestion_analysis": {
                "distribution": congestion_distribution,
                "overall_level": max(congestion_distribution.items(), key=lambda x: x[1])[0] if congestion_distribution else "unknown"
            },
            "traffic_light_metrics": {
                "total_lights": len(traffic_lights),
                "optimized_lights": optimized_lights,
                "optimization_rate": optimized_lights / len(traffic_lights) if traffic_lights else 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_intersection_performance(
        self,
        db: AsyncSession,
        intersection_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get performance metrics for a specific intersection"""
        
        traffic_light = await db.execute(
            select(TrafficLight).where(TrafficLight.intersection_id == intersection_id)
        )
        light = traffic_light.scalar_one_or_none()
        
        if not light:
            raise ValueError(f"Traffic light not found for intersection {intersection_id}")
        
        # Get vehicle data near intersection for the time period
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        lat_delta = 0.002
        lon_delta = 0.002
        
        vehicle_data_result = await db.execute(
            select(VehicleData)
            .where(
                and_(
                    VehicleData.timestamp >= cutoff_time,
                    VehicleData.latitude >= light.latitude - lat_delta,
                    VehicleData.latitude <= light.latitude + lat_delta,
                    VehicleData.longitude >= light.longitude - lon_delta,
                    VehicleData.longitude <= light.longitude + lon_delta,
                    VehicleData.is_validated == True
                )
            )
        )
        vehicle_data = vehicle_data_result.scalars().all()
        
        # Calculate performance metrics
        if not vehicle_data:
            return {
                "intersection_id": intersection_id,
                "message": "No vehicle data available for analysis",
                "days": days
            }
        
        # Traffic flow analysis
        daily_counts = {}
        daily_speeds = {}
        
        for vd in vehicle_data:
            day_key = vd.timestamp.date().isoformat()
            if day_key not in daily_counts:
                daily_counts[day_key] = 0
                daily_speeds[day_key] = []
            
            daily_counts[day_key] += 1
            if vd.speed is not None:
                daily_speeds[day_key].append(vd.speed)
        
        # Calculate daily averages
        daily_avg_speeds = {
            day: sum(speeds) / len(speeds) if speeds else 0
            for day, speeds in daily_speeds.items()
        }
        
        # Overall metrics
        all_speeds = [vd.speed for vd in vehicle_data if vd.speed is not None]
        avg_speed = sum(all_speeds) / len(all_speeds) if all_speeds else 0
        
        return {
            "intersection_id": intersection_id,
            "analysis_period_days": days,
            "traffic_light_info": {
                "current_phase": light.current_phase,
                "last_optimization": light.last_optimization.isoformat() if light.last_optimization else None,
                "timing_config": light.timing_config
            },
            "traffic_metrics": {
                "total_data_points": len(vehicle_data),
                "unique_vehicles": len(set(vd.vehicle_id for vd in vehicle_data)),
                "average_speed": round(avg_speed, 2),
                "daily_traffic_counts": daily_counts,
                "daily_average_speeds": {k: round(v, 2) for k, v in daily_avg_speeds.items()}
            },
            "performance_indicators": {
                "has_recent_optimization": bool(light.last_optimization and 
                                              light.last_optimization > datetime.utcnow() - timedelta(days=7)),
                "optimization_data": light.ai_optimization_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def schedule_optimization(
        self,
        db: AsyncSession,
        intersection_ids: List[str],
        schedule_time: datetime
    ) -> Dict[str, Any]:
        """Schedule optimization for intersections"""
        
        # This would typically integrate with a job scheduler
        # For now, we'll just log the schedule
        
        logger.info(f"Scheduled optimization for {len(intersection_ids)} intersections at {schedule_time}")
        
        return {
            "intersection_ids": intersection_ids,
            "scheduled_time": schedule_time.isoformat(),
            "status": "scheduled",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_traffic_predictions(
        self,
        db: AsyncSession,
        intersection_id: str,
        prediction_hours: int = 2
    ) -> Dict[str, Any]:
        """Get traffic predictions for an intersection"""
        
        # Get historical data for pattern analysis
        cutoff_time = datetime.utcnow() - timedelta(days=7)  # Last week for patterns
        
        traffic_light = await db.execute(
            select(TrafficLight).where(TrafficLight.intersection_id == intersection_id)
        )
        light = traffic_light.scalar_one_or_none()
        
        if not light:
            raise ValueError(f"Traffic light not found for intersection {intersection_id}")
        
        # Use AI optimizer for predictions
        prediction_result = await self.traffic_optimizer.predict_traffic_patterns(
            intersection_id=intersection_id,
            prediction_hours=prediction_hours
        )
        
        return {
            "intersection_id": intersection_id,
            "prediction_hours": prediction_hours,
            "predictions": prediction_result,
            "timestamp": datetime.utcnow().isoformat()
        }
