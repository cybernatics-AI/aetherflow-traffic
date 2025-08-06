"""
Test configuration and fixtures for AetherFlow Backend
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from aetherflow.main import create_app
from aetherflow.core.database import Base, get_async_session
from aetherflow.core.config import get_settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_aetherflow.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_app(test_session):
    """Create test FastAPI application"""
    app = create_app()
    
    # Override database dependency
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_async_session] = override_get_db
    
    return app


@pytest.fixture
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_hedera_client():
    """Mock Hedera client for testing"""
    class MockHederaClient:
        def __init__(self):
            self.account_id_str = "0.0.123456"
            self.network = "testnet"
            self.client = None
        
        async def create_topic(self, memo=None, admin_key=True):
            return "0.0.999999"
        
        async def submit_message(self, topic_id, message, memo=None):
            return "0.0.123456@1234567890.123456789"
        
        async def get_account_balance(self, account_id=None):
            return 100.0
        
        async def transfer_hbar(self, to_account, amount, memo=None):
            return "0.0.123456@1234567890.123456789"
        
        async def get_topic_info(self, topic_id):
            return {
                "topic_id": topic_id,
                "memo": "Test topic",
                "running_hash": "test_hash",
                "sequence_number": 1
            }
    
    return MockHederaClient()


# Sample test data
@pytest.fixture
def sample_vehicle_data():
    """Sample vehicle data for testing"""
    return {
        "vehicle_id": "TEST_VEHICLE_001",
        "speed": 45.5,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "heading": 90.0,
        "altitude": 10.0,
        "device_type": "OBD-II",
        "encrypted_data": {"fuel_level": 0.75},
        "zk_proof": {"proof": "test_proof", "verified": True}
    }


@pytest.fixture
def sample_agent_data():
    """Sample AI agent data for testing"""
    return {
        "agent_name": "TestAgent",
        "agent_type": "traffic_optimizer",
        "account_id": "0.0.123001",
        "capabilities": ["traffic_analysis", "route_optimization"],
        "profile_metadata": {"city": "TestCity"},
        "max_connections": 50
    }


@pytest.fixture
def sample_intersection_data():
    """Sample intersection data for testing"""
    return {
        "intersection_id": "TEST_INTERSECTION_001",
        "latitude": 40.7589,
        "longitude": -73.9851,
        "address": "Test St & Main Ave",
        "city": "TestCity",
        "red_duration": 30,
        "yellow_duration": 5,
        "green_duration": 25
    }
