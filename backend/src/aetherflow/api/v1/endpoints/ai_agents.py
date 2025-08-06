"""
AI Agents Management API Endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from aetherflow.core.database import get_async_session
from aetherflow.models.ai_agents import AIAgent, AgentStatus, AgentType
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AgentMetrics(BaseModel):
    """Agent metrics response schema"""
    total_agents: int
    active_agents: int
    inactive_agents: int
    agents_by_type: Dict[str, int]
    total_messages: int
    average_reputation: float


@router.get("/metrics", response_model=AgentMetrics)
async def get_agent_metrics(db: AsyncSession = Depends(get_async_session)):
    """Get overall agent metrics and statistics"""
    try:
        from sqlalchemy import select, func
        
        # Get total counts
        total_query = select(func.count(AIAgent.id))
        total_result = await db.execute(total_query)
        total_agents = total_result.scalar()
        
        # Get active agents
        active_query = select(func.count(AIAgent.id)).where(AIAgent.status == AgentStatus.ACTIVE)
        active_result = await db.execute(active_query)
        active_agents = active_result.scalar()
        
        # Get inactive agents
        inactive_query = select(func.count(AIAgent.id)).where(AIAgent.status == AgentStatus.INACTIVE)
        inactive_result = await db.execute(inactive_query)
        inactive_agents = inactive_result.scalar()
        
        # Get counts by type
        type_query = select(AIAgent.agent_type, func.count(AIAgent.id)).group_by(AIAgent.agent_type)
        type_result = await db.execute(type_query)
        agents_by_type = dict(type_result.fetchall())
        
        # Get aggregate metrics
        metrics_query = select(
            func.sum(AIAgent.messages_sent),
            func.avg(AIAgent.reputation_score)
        )
        metrics_result = await db.execute(metrics_query)
        total_messages, avg_reputation = metrics_result.fetchone()
        
        return AgentMetrics(
            total_agents=total_agents or 0,
            active_agents=active_agents or 0,
            inactive_agents=inactive_agents or 0,
            agents_by_type=agents_by_type,
            total_messages=total_messages or 0,
            average_reputation=float(avg_reputation or 0.0)
        )
        
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent metrics"
        )
