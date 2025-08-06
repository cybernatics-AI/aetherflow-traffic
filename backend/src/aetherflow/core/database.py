"""
Database configuration and management for AetherFlow Backend
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from aetherflow.core.config import get_settings

logger = logging.getLogger(__name__)

# Database metadata and base
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Global variables for database engines and sessions
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def get_database_url(async_mode: bool = False) -> str:
    """Get database URL with async driver if needed"""
    settings = get_settings()
    url = settings.DATABASE_URL
    
    if async_mode and url.startswith("sqlite:///"):
        # Convert SQLite URL to async version
        url = url.replace("sqlite:///", "sqlite+aiosqlite:///")
    
    return url


async def init_db() -> None:
    """Initialize database connection and create tables"""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    settings = get_settings()
    
    # Create sync engine for migrations and admin tasks
    engine = create_engine(
        get_database_url(async_mode=False),
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    
    # Create async engine for application use
    async_engine = create_async_engine(
        get_database_url(async_mode=True),
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    
    # Create session factories
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connections"""
    global engine, async_engine
    
    if async_engine:
        await async_engine.dispose()
    
    if engine:
        engine.dispose()
    
    logger.info("Database connections closed")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session (for migrations and admin tasks)"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
