"""
Integration Tests for AetherFlow API
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
from decimal import Decimal

from aetherflow.main import app
from aetherflow.core.database import get_db_session
from aetherflow.models.user_accounts import UserAccount
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.models.traffic_lights import TrafficLight


@pytest.mark.asyncio
class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    async def test_complete_user_workflow(self, test_client: AsyncClient):
        """Test complete user workflow from registration to rewards"""
        
        # 1. Create user account
        user_data = {
            "hedera_account_id": "0.0.999999",
            "email": "test@example.com",
            "username": "test_user",
            "role": "user"
        }
        
        response = await test_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        user_response = response.json()
        assert user_response["hedera_account_id"] == user_data["hedera_account_id"]
        
        # 2. Submit vehicle data
        vehicle_data = {
            "vehicle_id": "TEST_VEHICLE_001",
            "speed": 45.5,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "heading": 180.0,
            "device_type": "smartphone"
        }
        
        response = await test_client.post("/api/v1/vehicle-data/", json=vehicle_data)
        assert response.status_code == 201
        vehicle_response = response.json()
        assert vehicle_response["vehicle_id"] == vehicle_data["vehicle_id"]
        assert "reward_amount" in vehicle_response
        
        # 3. Check user portfolio
        response = await test_client.get(f"/api/v1/users/{user_data['hedera_account_id']}/portfolio")
        assert response.status_code == 200
        portfolio = response.json()
        assert "aether_balance" in portfolio
        assert "total_rewards_earned" in portfolio
        
        # 4. Get user account details
        response = await test_client.get(f"/api/v1/users/{user_data['hedera_account_id']}")
        assert response.status_code == 200
        user_details = response.json()
        assert user_details["hedera_account_id"] == user_data["hedera_account_id"]
    
    async def test_traffic_optimization_workflow(self, test_client: AsyncClient):
        """Test traffic optimization workflow"""
        
        # 1. Register traffic light
        traffic_light_data = {
            "intersection_id": "INT_TEST_001",
            "latitude": 40.7589,
            "longitude": -73.9851,
            "light_phases": ["red", "yellow", "green"],
            "current_phase": "red",
            "timing_config": {
                "red_duration": 30,
                "yellow_duration": 5,
                "green_duration": 25
            }
        }
        
        # First create the traffic light in database
        async with get_db_session() as db:
            traffic_light = TrafficLight(
                intersection_id=traffic_light_data["intersection_id"],
                latitude=traffic_light_data["latitude"],
                longitude=traffic_light_data["longitude"],
                light_phases=traffic_light_data["light_phases"],
                current_phase=traffic_light_data["current_phase"],
                timing_config=traffic_light_data["timing_config"],
                status="active",
                installation_date=datetime.utcnow()
            )
            db.add(traffic_light)
            await db.commit()
        
        # 2. Submit vehicle data near intersection
        vehicle_data_list = [
            {
                "vehicle_id": f"TRAFFIC_TEST_{i:03d}",
                "speed": 25.0 + (i * 2),
                "latitude": 40.7589 + (i * 0.0001),
                "longitude": -73.9851 + (i * 0.0001),
                "device_type": "gps_tracker"
            }
            for i in range(5)
        ]
        
        for vd in vehicle_data_list:
            response = await test_client.post("/api/v1/vehicle-data/", json=vd)
            assert response.status_code == 201
        
        # 3. Optimize intersection
        response = await test_client.post(
            f"/api/v1/traffic/optimize-intersection/{traffic_light_data['intersection_id']}"
        )
        assert response.status_code == 200
        optimization_result = response.json()
        assert "optimization_result" in optimization_result
        
        # 4. Get traffic analytics
        response = await test_client.get("/api/v1/traffic/analytics")
        assert response.status_code == 200
        analytics = response.json()
        assert "vehicle_metrics" in analytics
    
    async def test_ai_agent_workflow(self, test_client: AsyncClient):
        """Test AI agent registration and communication workflow"""
        
        # 1. Register AI agent
        agent_data = {
            "agent_name": "Test Traffic Optimizer",
            "agent_type": "traffic_optimizer",
            "capabilities": ["intersection_optimization", "traffic_prediction"],
            "owner_account_id": "0.0.888888",
            "description": "Test agent for integration testing"
        }
        
        response = await test_client.post("/api/v1/agents/register", json=agent_data)
        assert response.status_code == 201
        agent_response = response.json()
        agent_id = agent_response["agent_id"]
        
        # 2. Update agent metrics
        metrics_data = {
            "performance_metrics": {
                "success_rate": 0.95,
                "response_time": 1.2,
                "accuracy": 0.88,
                "uptime": 0.99
            }
        }
        
        response = await test_client.put(f"/api/v1/agents/{agent_id}/metrics", json=metrics_data)
        assert response.status_code == 200
        
        # 3. Get agent details
        response = await test_client.get(f"/api/v1/agents/{agent_id}")
        assert response.status_code == 200
        agent_details = response.json()
        assert agent_details["agent_name"] == agent_data["agent_name"]
        assert "reputation_score" in agent_details
    
    async def test_tokenomics_workflow(self, test_client: AsyncClient):
        """Test tokenomics and NFT workflow"""
        
        # 1. Create user account
        user_data = {
            "hedera_account_id": "0.0.777777",
            "email": "nft_user@example.com",
            "username": "nft_user",
            "role": "traffic_operator"
        }
        
        response = await test_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        
        # 2. Create Traffic NFT
        nft_data = {
            "intersection_id": "INT_NFT_001",
            "owner_account_id": user_data["hedera_account_id"],
            "performance_metrics": {
                "efficiency_score": 0.85,
                "traffic_volume": 1500,
                "average_wait_time": 45
            },
            "pricing_model": {
                "type": "revenue_share",
                "base_price": 100.0,
                "revenue_percentage": 0.7
            }
        }
        
        response = await test_client.post("/api/v1/traffic-nfts/", json=nft_data)
        assert response.status_code == 201
        nft_response = response.json()
        nft_id = nft_response["id"]
        
        # 3. Calculate revenue share
        revenue_data = {
            "total_revenue": 50.0,
            "period_days": 30
        }
        
        response = await test_client.post(
            f"/api/v1/traffic-nfts/{nft_id}/revenue-share",
            json=revenue_data
        )
        assert response.status_code == 200
        revenue_response = response.json()
        assert "nft_share" in revenue_response
        
        # 4. Check updated portfolio
        response = await test_client.get(f"/api/v1/users/{user_data['hedera_account_id']}/portfolio")
        assert response.status_code == 200
        portfolio = response.json()
        assert portfolio["nfts"]["count"] > 0
    
    async def test_derivatives_workflow(self, test_client: AsyncClient):
        """Test derivatives trading workflow"""
        
        # 1. Create derivative contract
        derivative_data = {
            "derivative_type": "congestion",
            "area_definition": {
                "min_lat": 40.7000,
                "max_lat": 40.8000,
                "min_lon": -74.1000,
                "max_lon": -74.0000
            },
            "contract_terms": {
                "base_price": 25.0,
                "strike_congestion_level": 0.6,
                "expiration_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "creator_account_id": "0.0.666666"
        }
        
        response = await test_client.post("/api/v1/derivatives/", json=derivative_data)
        assert response.status_code == 201
        derivative_response = response.json()
        derivative_id = derivative_response["id"]
        
        # 2. Update pricing
        response = await test_client.post(f"/api/v1/derivatives/{derivative_id}/update-pricing")
        assert response.status_code == 200
        pricing_response = response.json()
        assert "new_price" in pricing_response
        
        # 3. Get pricing history
        response = await test_client.get(f"/api/v1/derivatives/{derivative_id}/pricing-history")
        assert response.status_code == 200
        history_response = response.json()
        assert "pricing_history" in history_response
        
        # 4. Get active derivatives
        response = await test_client.get("/api/v1/derivatives/market/active")
        assert response.status_code == 200
        market_response = response.json()
        assert "active_derivatives" in market_response
    
    async def test_hcs10_communication_workflow(self, test_client: AsyncClient):
        """Test HCS-10 communication workflow"""
        
        # 1. Register agent with HCS-10
        agent_data = {
            "agent_name": "HCS10 Test Agent",
            "agent_type": "data_validator",
            "capabilities": ["data_validation", "quality_scoring"],
            "owner_account_id": "0.0.555555"
        }
        
        response = await test_client.post("/api/v1/hcs10/register-agent", json=agent_data)
        assert response.status_code == 201
        registration_response = response.json()
        
        # 2. Get registry info
        response = await test_client.get("/api/v1/hcs10/registry-info")
        assert response.status_code == 200
        registry_info = response.json()
        assert "total_agents" in registry_info
        
        # 3. Send message (would normally require actual HCS setup)
        message_data = {
            "target_agent_name": agent_data["agent_name"],
            "message": "Test message for integration testing",
            "sender_id": "0.0.444444",
            "message_type": "request"
        }
        
        # This might fail without actual HCS setup, but we test the endpoint
        response = await test_client.post("/api/v1/hcs10/send-message", json=message_data)
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
    
    async def test_data_validation_workflow(self, test_client: AsyncClient):
        """Test data validation and quality scoring"""
        
        # 1. Submit high-quality vehicle data
        high_quality_data = {
            "vehicle_id": "QUALITY_TEST_001",
            "speed": 35.0,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "heading": 90.0,
            "altitude": 10.0,
            "device_type": "professional_gps",
            "zk_proof": {
                "proof": {"a": "test", "b": "test", "c": "test"},
                "public_inputs": {"speed_range": "valid"},
                "verification_key": {"alpha": "test"},
                "verified": True
            }
        }
        
        response = await test_client.post("/api/v1/vehicle-data/", json=high_quality_data)
        assert response.status_code == 201
        high_quality_response = response.json()
        
        # 2. Submit low-quality vehicle data
        low_quality_data = {
            "vehicle_id": "QUALITY_TEST_002",
            "speed": 200.0,  # Unrealistic speed
            "latitude": 91.0,  # Invalid latitude
            "longitude": -74.0060,
            "device_type": "unknown"
        }
        
        response = await test_client.post("/api/v1/vehicle-data/", json=low_quality_data)
        # Should still accept but with low validation score
        assert response.status_code == 201
        low_quality_response = response.json()
        
        # 3. Compare validation scores
        assert high_quality_response["validation"]["overall_score"] > low_quality_response["validation"]["overall_score"]
        assert high_quality_response["reward_amount"] > low_quality_response["reward_amount"]
        
        # 4. Get validation statistics
        response = await test_client.get("/api/v1/vehicle-data/validation-stats")
        assert response.status_code == 200
        validation_stats = response.json()
        assert "validation_rate" in validation_stats
    
    async def test_system_health_endpoints(self, test_client: AsyncClient):
        """Test system health and monitoring endpoints"""
        
        # 1. Health check
        response = await test_client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        # 2. API statistics
        endpoints_to_test = [
            "/api/v1/vehicle-data/stats",
            "/api/v1/agents/stats",
            "/api/v1/traffic/stats",
            "/api/v1/users/stats/overview",
            "/api/v1/traffic-nfts/stats/overview",
            "/api/v1/derivatives/stats/overview"
        ]
        
        for endpoint in endpoints_to_test:
            response = await test_client.get(endpoint)
            assert response.status_code == 200
            stats_data = response.json()
            assert "timestamp" in stats_data
    
    async def test_error_handling(self, test_client: AsyncClient):
        """Test API error handling"""
        
        # 1. Test 404 errors
        response = await test_client.get("/api/v1/users/0.0.nonexistent")
        assert response.status_code == 404
        
        response = await test_client.get("/api/v1/traffic-nfts/99999")
        assert response.status_code == 404
        
        response = await test_client.get("/api/v1/derivatives/99999")
        assert response.status_code == 404
        
        # 2. Test validation errors
        invalid_user_data = {
            "hedera_account_id": "invalid_format",
            "email": "not_an_email",
            "role": "invalid_role"
        }
        
        response = await test_client.post("/api/v1/users/", json=invalid_user_data)
        assert response.status_code == 422  # Validation error
        
        # 3. Test invalid vehicle data
        invalid_vehicle_data = {
            "vehicle_id": "",  # Empty vehicle ID
            "speed": -10,  # Negative speed
            "latitude": 200,  # Invalid latitude
            "longitude": -200  # Invalid longitude
        }
        
        response = await test_client.post("/api/v1/vehicle-data/", json=invalid_vehicle_data)
        assert response.status_code == 422
    
    async def test_pagination_and_filtering(self, test_client: AsyncClient):
        """Test pagination and filtering functionality"""
        
        # Create multiple records for testing
        for i in range(15):
            user_data = {
                "hedera_account_id": f"0.0.{800000 + i}",
                "email": f"user{i}@example.com",
                "username": f"user_{i}",
                "role": "user" if i % 2 == 0 else "admin"
            }
            
            response = await test_client.post("/api/v1/users/", json=user_data)
            assert response.status_code == 201
        
        # Test pagination
        response = await test_client.get("/api/v1/users/?limit=5&offset=0")
        assert response.status_code == 200
        users_page1 = response.json()
        assert len(users_page1) <= 5
        
        response = await test_client.get("/api/v1/users/?limit=5&offset=5")
        assert response.status_code == 200
        users_page2 = response.json()
        assert len(users_page2) <= 5
        
        # Test filtering
        response = await test_client.get("/api/v1/users/?role=admin")
        assert response.status_code == 200
        admin_users = response.json()
        for user in admin_users:
            assert user["role"] == "admin"


@pytest.mark.asyncio
class TestPerformanceIntegration:
    """Performance and load testing"""
    
    async def test_concurrent_vehicle_data_submission(self, test_client: AsyncClient):
        """Test concurrent vehicle data submissions"""
        
        async def submit_vehicle_data(vehicle_id: str):
            data = {
                "vehicle_id": vehicle_id,
                "speed": 45.0,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "device_type": "smartphone"
            }
            response = await test_client.post("/api/v1/vehicle-data/", json=data)
            return response.status_code == 201
        
        # Submit 20 concurrent requests
        tasks = [submit_vehicle_data(f"CONCURRENT_{i:03d}") for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Most should succeed
        success_count = sum(1 for result in results if result is True)
        assert success_count >= 15  # Allow for some failures under load
    
    async def test_large_data_batch_processing(self, test_client: AsyncClient):
        """Test processing of large data batches"""
        
        # Submit a batch of vehicle data
        batch_data = []
        for i in range(100):
            data = {
                "vehicle_id": f"BATCH_{i:03d}",
                "speed": 30.0 + (i % 50),
                "latitude": 40.7128 + (i * 0.0001),
                "longitude": -74.0060 + (i * 0.0001),
                "device_type": "gps_tracker"
            }
            batch_data.append(data)
        
        # Submit data in smaller batches to avoid timeout
        batch_size = 10
        success_count = 0
        
        for i in range(0, len(batch_data), batch_size):
            batch = batch_data[i:i + batch_size]
            
            for data in batch:
                response = await test_client.post("/api/v1/vehicle-data/", json=data)
                if response.status_code == 201:
                    success_count += 1
        
        # Most submissions should succeed
        assert success_count >= 80  # Allow for some failures
        
        # Check that data was processed
        response = await test_client.get("/api/v1/vehicle-data/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_records"] >= success_count
