"""
AetherFlow API v1 Router
"""

from fastapi import APIRouter

from .endpoints import (
    vehicle_data,
    traffic_optimization,
    ai_agents,
    hedera_integration,
    hcs10_communication,
    user_accounts,
    traffic_nfts,
    derivatives
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(vehicle_data.router)
api_router.include_router(traffic_optimization.router)
api_router.include_router(ai_agents.router)
api_router.include_router(hedera_integration.router)
api_router.include_router(hcs10_communication.router)
api_router.include_router(user_accounts.router)
api_router.include_router(traffic_nfts.router)
api_router.include_router(derivatives.router)
