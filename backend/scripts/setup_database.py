#!/usr/bin/env python3
"""
Database Setup Script for AetherFlow Backend
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aetherflow.core.database import engine, Base
from aetherflow.core.logging import get_logger
from aetherflow.core.config import get_settings

# Import all models to ensure they're registered
from aetherflow.models import (
    vehicle_data,
    traffic_lights,
    user_accounts,
    traffic_nfts,
    derivatives,
    ai_agents
)

logger = get_logger(__name__)


async def create_tables():
    """Create all database tables"""
    
    logger.info("Creating database tables...")
    
    try:
        async with engine.begin() as conn:
            # Drop all tables (use with caution!)
            if "--drop" in sys.argv:
                logger.warning("Dropping all existing tables...")
                await conn.run_sync(Base.metadata.drop_all)
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully!")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def seed_sample_data():
    """Seed database with sample data for development"""
    
    if "--seed" not in sys.argv:
        return
    
    logger.info("Seeding sample data...")
    
    try:
        from aetherflow.core.database import get_db_session
        from aetherflow.models.user_accounts import UserAccount
        from aetherflow.models.traffic_lights import TrafficLight
        from datetime import datetime
        
        async with get_db_session() as db:
            # Create sample user accounts
            sample_users = [
                UserAccount(
                    hedera_account_id="0.0.123456",
                    email="alice@example.com",
                    username="alice_driver",
                    role="user"
                ),
                UserAccount(
                    hedera_account_id="0.0.123457",
                    email="bob@example.com",
                    username="bob_admin",
                    role="admin"
                ),
                UserAccount(
                    hedera_account_id="0.0.123458",
                    email="charlie@example.com",
                    username="charlie_operator",
                    role="traffic_operator"
                )
            ]
            
            for user in sample_users:
                db.add(user)
            
            # Create sample traffic lights
            sample_lights = [
                TrafficLight(
                    intersection_id="INT_001",
                    latitude=40.7128,
                    longitude=-74.0060,
                    light_phases=["red", "yellow", "green"],
                    current_phase="red",
                    timing_config={
                        "red_duration": 30,
                        "yellow_duration": 5,
                        "green_duration": 25
                    },
                    status="active",
                    installation_date=datetime.utcnow()
                ),
                TrafficLight(
                    intersection_id="INT_002",
                    latitude=40.7589,
                    longitude=-73.9851,
                    light_phases=["red", "yellow", "green"],
                    current_phase="green",
                    timing_config={
                        "red_duration": 35,
                        "yellow_duration": 5,
                        "green_duration": 30
                    },
                    status="active",
                    installation_date=datetime.utcnow()
                )
            ]
            
            for light in sample_lights:
                db.add(light)
            
            await db.commit()
            
        logger.info("Sample data seeded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to seed sample data: {e}")
        raise


async def main():
    """Main setup function"""
    
    settings = get_settings()
    logger.info(f"Setting up database: {settings.database_url}")
    
    # Create tables
    await create_tables()
    
    # Seed sample data if requested
    await seed_sample_data()
    
    logger.info("Database setup completed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_database.py [--drop] [--seed]")
        print("  --drop: Drop existing tables before creating new ones")
        print("  --seed: Seed database with sample data")
        sys.exit(1)
    
    asyncio.run(main())
