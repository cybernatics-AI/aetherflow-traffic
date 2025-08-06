"""
AetherFlow Backend Main Application
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from aetherflow.core.config import get_settings
from aetherflow.core.database import init_db, close_db
from aetherflow.core.logging import setup_logging
from aetherflow.api.v1.router import api_router
from aetherflow.hedera.client import HederaClient
from aetherflow.hcs10.agent_registry import AgentRegistry


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager"""
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.LOG_LEVEL, settings.LOG_FILE)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AetherFlow Backend...")
    
    # Initialize database
    await init_db()
    
    # Initialize Hedera client
    hedera_client = HederaClient(
        account_id=settings.HEDERA_ACCOUNT_ID,
        private_key=settings.HEDERA_PRIVATE_KEY,
        network=settings.HEDERA_NETWORK
    )
    app.state.hedera_client = hedera_client
    
    # Initialize HCS-10 Agent Registry
    agent_registry = AgentRegistry(hedera_client, settings.HCS_REGISTRY_TOPIC_ID)
    app.state.agent_registry = agent_registry
    
    logger.info("AetherFlow Backend started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down AetherFlow Backend...")
    await close_db()
    logger.info("AetherFlow Backend shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="AetherFlow Backend",
        description="Decentralized Federated AI for Urban Mobility on Hedera with HCS-10 OpenConvAI",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
    )
    
    # Include API router
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")
    
    @app.get("/")
    async def root():
        return {
            "message": "AetherFlow Backend API",
            "version": "0.1.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "aetherflow-backend"}
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger = logging.getLogger(__name__)
        logger.error(f"Global exception handler caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "aetherflow.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
