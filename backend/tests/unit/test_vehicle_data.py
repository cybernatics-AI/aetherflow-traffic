"""
Unit tests for vehicle data functionality
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from aetherflow.models.vehicle_data import VehicleData


@pytest.mark.asyncio
async def test_submit_vehicle_data(test_client: AsyncClient, sample_vehicle_data):
    """Test vehicle data submission"""
    response = await test_client.post(
        "/api/v1/vehicle-data/submit",
        json=sample_vehicle_data
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert "data_hash" in data
    assert "reward_amount" in data
    assert data["reward_amount"] > 0


@pytest.mark.asyncio
async def test_submit_vehicle_data_invalid(test_client: AsyncClient):
    """Test vehicle data submission with invalid data"""
    invalid_data = {
        "vehicle_id": "TEST",
        "speed": -10,  # Invalid negative speed
        "latitude": 91,  # Invalid latitude
        "longitude": -74.0060
    }
    
    response = await test_client.post(
        "/api/v1/vehicle-data/submit",
        json=invalid_data
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_vehicle_data(test_client: AsyncClient, sample_vehicle_data):
    """Test retrieving vehicle data"""
    # First submit some data
    await test_client.post(
        "/api/v1/vehicle-data/submit",
        json=sample_vehicle_data
    )
    
    # Then retrieve it
    response = await test_client.get("/api/v1/vehicle-data/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    vehicle_record = data[0]
    assert vehicle_record["vehicle_id"] == sample_vehicle_data["vehicle_id"]
    assert vehicle_record["speed"] == sample_vehicle_data["speed"]


@pytest.mark.asyncio
async def test_get_vehicle_data_by_id(test_client: AsyncClient, sample_vehicle_data):
    """Test retrieving specific vehicle data by ID"""
    # Submit data first
    submit_response = await test_client.post(
        "/api/v1/vehicle-data/submit",
        json=sample_vehicle_data
    )
    
    # Get all data to find the ID
    list_response = await test_client.get("/api/v1/vehicle-data/")
    data_list = list_response.json()
    data_id = data_list[0]["id"]
    
    # Get specific record
    response = await test_client.get(f"/api/v1/vehicle-data/{data_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == data_id
    assert data["vehicle_id"] == sample_vehicle_data["vehicle_id"]


@pytest.mark.asyncio
async def test_get_vehicle_data_not_found(test_client: AsyncClient):
    """Test retrieving non-existent vehicle data"""
    response = await test_client.get("/api/v1/vehicle-data/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_validate_vehicle_data(test_client: AsyncClient, sample_vehicle_data):
    """Test vehicle data validation"""
    # Submit data first
    await test_client.post(
        "/api/v1/vehicle-data/submit",
        json=sample_vehicle_data
    )
    
    # Get the data ID
    list_response = await test_client.get("/api/v1/vehicle-data/")
    data_list = list_response.json()
    data_id = data_list[0]["id"]
    
    # Validate the data
    response = await test_client.post(f"/api/v1/vehicle-data/{data_id}/validate")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["data_id"] == data_id
    assert "quality_score" in data


@pytest.mark.asyncio
async def test_vehicle_data_model(test_session: AsyncSession):
    """Test VehicleData model functionality"""
    vehicle_data = VehicleData(
        vehicle_id="TEST_VEHICLE",
        speed=50.0,
        latitude=40.7128,
        longitude=-74.0060,
        data_hash="test_hash"
    )
    
    test_session.add(vehicle_data)
    await test_session.commit()
    await test_session.refresh(vehicle_data)
    
    assert vehicle_data.id is not None
    assert vehicle_data.vehicle_id == "TEST_VEHICLE"
    assert vehicle_data.location == {"latitude": 40.7128, "longitude": -74.0060}
    
    # Test to_dict method
    data_dict = vehicle_data.to_dict()
    assert isinstance(data_dict, dict)
    assert data_dict["vehicle_id"] == "TEST_VEHICLE"
    assert data_dict["speed"] == 50.0


@pytest.mark.asyncio
async def test_vehicle_data_filtering(test_client: AsyncClient):
    """Test vehicle data filtering by vehicle_id"""
    # Submit data for different vehicles
    vehicle1_data = {
        "vehicle_id": "VEHICLE_001",
        "speed": 45.0,
        "latitude": 40.7128,
        "longitude": -74.0060
    }
    
    vehicle2_data = {
        "vehicle_id": "VEHICLE_002", 
        "speed": 55.0,
        "latitude": 40.7589,
        "longitude": -73.9851
    }
    
    await test_client.post("/api/v1/vehicle-data/submit", json=vehicle1_data)
    await test_client.post("/api/v1/vehicle-data/submit", json=vehicle2_data)
    
    # Filter by vehicle_id
    response = await test_client.get("/api/v1/vehicle-data/?vehicle_id=VEHICLE_001")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["vehicle_id"] == "VEHICLE_001"
