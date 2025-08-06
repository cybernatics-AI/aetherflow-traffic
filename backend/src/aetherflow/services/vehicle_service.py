"""
Vehicle Data Service - Business Logic for Vehicle Data Management
"""

import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from aetherflow.core.logging import get_logger
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.ai.data_validator import DataValidator
from aetherflow.hedera.client import HederaClient

logger = get_logger(__name__)


class VehicleDataService:
    """Service for managing vehicle data operations"""
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera_client = hedera_client
        self.data_validator = DataValidator()
        
    async def submit_vehicle_data(
        self,
        db: AsyncSession,
        vehicle_id: str,
        speed: float,
        latitude: float,
        longitude: float,
        heading: Optional[float] = None,
        altitude: Optional[float] = None,
        device_type: str = "smartphone",
        encrypted_data: Optional[str] = None,
        zk_proof: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Submit new vehicle data with validation and rewards"""
        
        logger.info(f"Submitting vehicle data for vehicle {vehicle_id}")
        
        # Create vehicle data record
        vehicle_data = VehicleData(
            vehicle_id=vehicle_id,
            speed=speed,
            latitude=latitude,
            longitude=longitude,
            heading=heading,
            altitude=altitude,
            device_type=device_type,
            encrypted_data=encrypted_data,
            zk_proof=zk_proof,
            timestamp=datetime.utcnow()
        )
        
        # Generate data hash
        vehicle_data.data_hash = self._generate_data_hash(vehicle_data)
        
        # Validate data
        validation_result = await self.data_validator.validate_vehicle_data(vehicle_data)
        vehicle_data.is_validated = validation_result["is_valid"]
        vehicle_data.validation_score = validation_result["overall_score"]
        
        # Calculate reward based on data quality
        reward_amount = self._calculate_reward(validation_result)
        vehicle_data.reward_amount = reward_amount
        
        # Submit to Hedera if client available
        hcs_message_id = None
        if self.hedera_client and validation_result["is_valid"]:
            try:
                hcs_message_id = await self._submit_to_hedera(vehicle_data)
                vehicle_data.hcs_message_id = hcs_message_id
            except Exception as e:
                logger.warning(f"Failed to submit to Hedera: {e}")
        
        # Save to database
        db.add(vehicle_data)
        await db.commit()
        await db.refresh(vehicle_data)
        
        logger.info(f"Vehicle data submitted successfully: ID {vehicle_data.id}, "
                   f"reward: {reward_amount}, HCS: {hcs_message_id}")
        
        return {
            "data_id": vehicle_data.id,
            "vehicle_id": vehicle_id,
            "validation": validation_result,
            "reward_amount": reward_amount,
            "hcs_message_id": hcs_message_id,
            "timestamp": vehicle_data.timestamp.isoformat()
        }
    
    async def get_vehicle_data(
        self,
        db: AsyncSession,
        data_id: int
    ) -> Optional[VehicleData]:
        """Get vehicle data by ID"""
        
        result = await db.execute(
            select(VehicleData).where(VehicleData.id == data_id)
        )
        return result.scalar_one_or_none()
    
    async def get_vehicle_data_by_vehicle(
        self,
        db: AsyncSession,
        vehicle_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[VehicleData]:
        """Get vehicle data for a specific vehicle"""
        
        result = await db.execute(
            select(VehicleData)
            .where(VehicleData.vehicle_id == vehicle_id)
            .order_by(VehicleData.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_recent_vehicle_data(
        self,
        db: AsyncSession,
        minutes: int = 60,
        limit: int = 1000
    ) -> List[VehicleData]:
        """Get recent vehicle data within specified time window"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        result = await db.execute(
            select(VehicleData)
            .where(VehicleData.timestamp >= cutoff_time)
            .order_by(VehicleData.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_vehicle_data_by_area(
        self,
        db: AsyncSession,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        limit: int = 1000
    ) -> List[VehicleData]:
        """Get vehicle data within a geographic bounding box"""
        
        result = await db.execute(
            select(VehicleData)
            .where(
                and_(
                    VehicleData.latitude >= min_lat,
                    VehicleData.latitude <= max_lat,
                    VehicleData.longitude >= min_lon,
                    VehicleData.longitude <= max_lon
                )
            )
            .order_by(VehicleData.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_validated_data(
        self,
        db: AsyncSession,
        min_score: float = 0.7,
        limit: int = 1000
    ) -> List[VehicleData]:
        """Get validated vehicle data above minimum score"""
        
        result = await db.execute(
            select(VehicleData)
            .where(
                and_(
                    VehicleData.is_validated == True,
                    VehicleData.validation_score >= min_score
                )
            )
            .order_by(VehicleData.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def calculate_traffic_metrics(
        self,
        db: AsyncSession,
        area_bounds: Optional[Dict[str, float]] = None,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Calculate traffic metrics for an area and time window"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        # Base query
        query = select(VehicleData).where(
            and_(
                VehicleData.timestamp >= cutoff_time,
                VehicleData.is_validated == True
            )
        )
        
        # Add area filter if provided
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
                "total_vehicles": 0,
                "average_speed": 0.0,
                "congestion_level": "unknown",
                "data_points": 0
            }
        
        # Calculate metrics
        speeds = [vd.speed for vd in vehicle_data if vd.speed is not None]
        unique_vehicles = len(set(vd.vehicle_id for vd in vehicle_data))
        
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
        
        # Simple congestion classification
        if avg_speed > 50:
            congestion_level = "low"
        elif avg_speed > 25:
            congestion_level = "moderate"
        else:
            congestion_level = "high"
        
        return {
            "total_vehicles": unique_vehicles,
            "data_points": len(vehicle_data),
            "average_speed": round(avg_speed, 2),
            "min_speed": min(speeds) if speeds else 0,
            "max_speed": max(speeds) if speeds else 0,
            "congestion_level": congestion_level,
            "time_window_minutes": time_window_minutes,
            "area_bounds": area_bounds,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_vehicle_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get overall vehicle data statistics"""
        
        # Total records
        total_result = await db.execute(select(func.count(VehicleData.id)))
        total_records = total_result.scalar()
        
        # Validated records
        validated_result = await db.execute(
            select(func.count(VehicleData.id))
            .where(VehicleData.is_validated == True)
        )
        validated_records = validated_result.scalar()
        
        # Unique vehicles
        unique_vehicles_result = await db.execute(
            select(func.count(func.distinct(VehicleData.vehicle_id)))
        )
        unique_vehicles = unique_vehicles_result.scalar()
        
        # Recent data (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_result = await db.execute(
            select(func.count(VehicleData.id))
            .where(VehicleData.timestamp >= recent_cutoff)
        )
        recent_records = recent_result.scalar()
        
        # Average validation score
        avg_score_result = await db.execute(
            select(func.avg(VehicleData.validation_score))
            .where(VehicleData.validation_score.is_not(None))
        )
        avg_validation_score = avg_score_result.scalar() or 0.0
        
        # Total rewards
        total_rewards_result = await db.execute(
            select(func.sum(VehicleData.reward_amount))
            .where(VehicleData.reward_amount.is_not(None))
        )
        total_rewards = total_rewards_result.scalar() or 0.0
        
        return {
            "total_records": total_records,
            "validated_records": validated_records,
            "validation_rate": validated_records / total_records if total_records > 0 else 0,
            "unique_vehicles": unique_vehicles,
            "recent_records_24h": recent_records,
            "average_validation_score": round(float(avg_validation_score), 3),
            "total_rewards_distributed": round(float(total_rewards), 6),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_data_hash(self, vehicle_data: VehicleData) -> str:
        """Generate hash for vehicle data integrity"""
        
        hash_data = {
            "vehicle_id": vehicle_data.vehicle_id,
            "speed": vehicle_data.speed,
            "latitude": vehicle_data.latitude,
            "longitude": vehicle_data.longitude,
            "heading": vehicle_data.heading,
            "altitude": vehicle_data.altitude,
            "timestamp": vehicle_data.timestamp.isoformat() if vehicle_data.timestamp else None,
            "device_type": vehicle_data.device_type
        }
        
        data_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _calculate_reward(self, validation_result: Dict[str, Any]) -> float:
        """Calculate reward amount based on data quality"""
        
        base_reward = 0.001  # Base reward in AETHER tokens
        quality_multiplier = validation_result["overall_score"]
        
        # Bonus for perfect validation
        if validation_result["overall_score"] >= 0.95:
            quality_multiplier *= 1.5
        
        # Penalty for low quality
        if validation_result["overall_score"] < 0.5:
            quality_multiplier *= 0.5
        
        return round(base_reward * quality_multiplier, 6)
    
    async def _submit_to_hedera(self, vehicle_data: VehicleData) -> Optional[str]:
        """Submit vehicle data to Hedera Consensus Service"""
        
        if not self.hedera_client:
            return None
        
        # Create HCS message
        message_data = {
            "type": "vehicle_data",
            "vehicle_id": vehicle_data.vehicle_id,
            "data_hash": vehicle_data.data_hash,
            "validation_score": vehicle_data.validation_score,
            "reward_amount": vehicle_data.reward_amount,
            "timestamp": vehicle_data.timestamp.isoformat()
        }
        
        message = json.dumps(message_data, separators=(',', ':'))
        
        try:
            # Submit to HCS topic
            message_id = await self.hedera_client.submit_message(
                topic_id="0.0.123456",  # Vehicle data topic
                message=message
            )
            
            logger.info(f"Submitted vehicle data to HCS: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to submit to HCS: {e}")
            raise
    
    async def batch_validate_data(
        self,
        db: AsyncSession,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Batch validate unvalidated vehicle data"""
        
        # Get unvalidated data
        result = await db.execute(
            select(VehicleData)
            .where(VehicleData.is_validated == False)
            .limit(limit)
        )
        unvalidated_data = result.scalars().all()
        
        if not unvalidated_data:
            return {
                "message": "No unvalidated data found",
                "processed": 0
            }
        
        # Validate batch
        validation_results = await self.data_validator.validate_batch(unvalidated_data)
        
        # Update database records
        updated_count = 0
        for i, vehicle_data in enumerate(unvalidated_data):
            validation_result = validation_results["validation_results"][i]
            
            vehicle_data.is_validated = validation_result["is_valid"]
            vehicle_data.validation_score = validation_result["overall_score"]
            
            # Recalculate reward
            vehicle_data.reward_amount = self._calculate_reward(validation_result)
            
            updated_count += 1
        
        await db.commit()
        
        logger.info(f"Batch validated {updated_count} vehicle data records")
        
        return {
            "processed": updated_count,
            "validation_rate": validation_results["validation_rate"],
            "average_score": validation_results["average_score"],
            "timestamp": datetime.utcnow().isoformat()
        }
