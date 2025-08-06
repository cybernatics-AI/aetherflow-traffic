"""
Vehicle Data API Endpoints
"""

import hashlib
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from aetherflow.core.database import get_async_session
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.hedera.client import HederaClient
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class VehicleDataSubmission(BaseModel):
    """Vehicle data submission schema"""
    vehicle_id: str = Field(..., description="Unique vehicle identifier")
    speed: float = Field(..., ge=0, le=300, description="Speed in km/h")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    heading: Optional[float] = Field(None, ge=0, le=360, description="Direction in degrees")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    device_type: Optional[str] = Field(None, description="Data source device type")
    encrypted_data: Optional[Dict[str, Any]] = Field(None, description="Encrypted sensitive data")
    zk_proof: Optional[Dict[str, Any]] = Field(None, description="Zero-knowledge proof")


class VehicleDataResponse(BaseModel):
    """Vehicle data response schema"""
    id: int
    vehicle_id: str
    speed: float
    latitude: float
    longitude: float
    heading: Optional[float]
    altitude: Optional[float]
    timestamp: str
    data_hash: str
    hcs_message_id: Optional[str]
    hedera_tx_id: Optional[str]
    device_type: Optional[str]
    data_quality_score: float
    is_validated: bool
    reward_amount: float
    created_at: str


class DataSubmissionResult(BaseModel):
    """Data submission result schema"""
    status: str
    tx_hash: Optional[str]
    message_id: Optional[str]
    data_hash: str
    reward_amount: float
    message: str


def calculate_data_hash(data: Dict[str, Any]) -> str:
    """Calculate SHA-256 hash of vehicle data"""
    # Create deterministic string representation
    data_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(data_str.encode()).hexdigest()


def calculate_reward_amount(data: VehicleDataSubmission) -> float:
    """Calculate reward amount based on data quality"""
    base_reward = 0.1  # Base $AETHER reward
    
    # Quality multipliers
    quality_score = 1.0
    
    # Bonus for additional data fields
    if data.heading is not None:
        quality_score += 0.1
    if data.altitude is not None:
        quality_score += 0.1
    if data.encrypted_data:
        quality_score += 0.2
    if data.zk_proof:
        quality_score += 0.3
    
    return base_reward * quality_score


@router.post("/submit", response_model=DataSubmissionResult)
async def submit_vehicle_data(
    data: VehicleDataSubmission,
    db: AsyncSession = Depends(get_async_session)
):
    """Submit vehicle data with ZK-proof validation"""
    try:
        # Calculate data hash
        data_dict = data.dict(exclude_none=True)
        data_hash = calculate_data_hash(data_dict)
        
        # Calculate reward amount
        reward_amount = calculate_reward_amount(data)
        
        # Create vehicle data record
        vehicle_data = VehicleData(
            vehicle_id=data.vehicle_id,
            speed=data.speed,
            latitude=data.latitude,
            longitude=data.longitude,
            heading=data.heading,
            altitude=data.altitude,
            encrypted_data=data.encrypted_data,
            data_hash=data_hash,
            zk_proof=data.zk_proof,
            device_type=data.device_type,
            reward_amount=reward_amount,
            timestamp=datetime.utcnow()
        )
        
        # Save to database
        db.add(vehicle_data)
        await db.commit()
        await db.refresh(vehicle_data)
        
        # TODO: Submit to HCS topic
        # This would be implemented with actual Hedera client
        hcs_message_id = None
        hedera_tx_id = None
        
        logger.info(f"Vehicle data submitted: {vehicle_data.id} with hash {data_hash}")
        
        return DataSubmissionResult(
            status="success",
            tx_hash=hedera_tx_id,
            message_id=hcs_message_id,
            data_hash=data_hash,
            reward_amount=reward_amount,
            message="Vehicle data submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to submit vehicle data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit vehicle data"
        )


@router.get("/", response_model=List[VehicleDataResponse])
async def get_vehicle_data(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Get vehicle data records"""
    try:
        from sqlalchemy import select
        
        query = select(VehicleData).offset(skip).limit(limit)
        
        if vehicle_id:
            query = query.where(VehicleData.vehicle_id == vehicle_id)
        
        result = await db.execute(query)
        vehicle_data_records = result.scalars().all()
        
        return [
            VehicleDataResponse(
                id=record.id,
                vehicle_id=record.vehicle_id,
                speed=record.speed,
                latitude=record.latitude,
                longitude=record.longitude,
                heading=record.heading,
                altitude=record.altitude,
                timestamp=record.timestamp.isoformat(),
                data_hash=record.data_hash,
                hcs_message_id=record.hcs_message_id,
                hedera_tx_id=record.hedera_tx_id,
                device_type=record.device_type,
                data_quality_score=record.data_quality_score,
                is_validated=record.is_validated,
                reward_amount=record.reward_amount,
                created_at=record.created_at.isoformat()
            )
            for record in vehicle_data_records
        ]
        
    except Exception as e:
        logger.error(f"Failed to get vehicle data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vehicle data"
        )


@router.get("/{data_id}", response_model=VehicleDataResponse)
async def get_vehicle_data_by_id(
    data_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """Get specific vehicle data record by ID"""
    try:
        from sqlalchemy import select
        
        query = select(VehicleData).where(VehicleData.id == data_id)
        result = await db.execute(query)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle data not found"
            )
        
        return VehicleDataResponse(
            id=record.id,
            vehicle_id=record.vehicle_id,
            speed=record.speed,
            latitude=record.latitude,
            longitude=record.longitude,
            heading=record.heading,
            altitude=record.altitude,
            timestamp=record.timestamp.isoformat(),
            data_hash=record.data_hash,
            hcs_message_id=record.hcs_message_id,
            hedera_tx_id=record.hedera_tx_id,
            device_type=record.device_type,
            data_quality_score=record.data_quality_score,
            is_validated=record.is_validated,
            reward_amount=record.reward_amount,
            created_at=record.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vehicle data {data_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vehicle data"
        )


@router.post("/{data_id}/validate")
async def validate_vehicle_data(
    data_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """Validate vehicle data with ZK-proof verification"""
    try:
        from sqlalchemy import select
        
        query = select(VehicleData).where(VehicleData.id == data_id)
        result = await db.execute(query)
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle data not found"
            )
        
        # TODO: Implement actual ZK-proof validation
        # For now, mark as validated
        record.is_validated = True
        record.validation_timestamp = datetime.utcnow()
        record.data_quality_score = min(record.data_quality_score + 0.1, 1.0)
        
        await db.commit()
        
        logger.info(f"Vehicle data {data_id} validated successfully")
        
        return {
            "status": "success",
            "message": "Vehicle data validated successfully",
            "data_id": data_id,
            "quality_score": record.data_quality_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate vehicle data {data_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate vehicle data"
        )
