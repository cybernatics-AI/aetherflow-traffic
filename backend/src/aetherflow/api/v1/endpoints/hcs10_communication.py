"""
HCS-10 OpenConvAI Communication API Endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from aetherflow.core.database import get_async_session
from aetherflow.models.ai_agents import AIAgent, AgentStatus, AgentType
from aetherflow.hcs10.agent_registry import AgentRegistry
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AgentRegistrationRequest(BaseModel):
    """Agent registration request schema"""
    agent_name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(default=AgentType.GENERAL_PURPOSE, description="Agent type")
    account_id: str = Field(..., description="Hedera account ID")
    capabilities: Optional[List[str]] = Field(None, description="Agent capabilities")
    profile_metadata: Optional[Dict[str, Any]] = Field(None, description="Profile metadata")
    max_connections: Optional[int] = Field(100, description="Maximum connections")


class AgentResponse(BaseModel):
    """Agent response schema"""
    id: int
    account_id: str
    agent_name: str
    agent_type: str
    status: str
    inbound_topic_id: Optional[str]
    outbound_topic_id: Optional[str]
    capabilities: Optional[List[str]]
    ttl: int
    max_connections: int
    active_connections: int
    reputation_score: float
    trust_level: str
    aether_balance: float
    last_activity: Optional[str]
    created_at: str


class ConnectionRequest(BaseModel):
    """Connection request schema"""
    from_agent_id: str = Field(..., description="Requesting agent account ID")
    to_agent_inbound_topic: str = Field(..., description="Target agent inbound topic ID")


class MessageRequest(BaseModel):
    """Message request schema"""
    from_agent_id: str = Field(..., description="Sender agent account ID")
    connection_topic_id: str = Field(..., description="Connection topic ID")
    message_data: str = Field(..., description="Message content")


class TransactionRequest(BaseModel):
    """Transaction request schema"""
    from_agent_id: str = Field(..., description="Requesting agent account ID")
    connection_topic_id: str = Field(..., description="Connection topic ID")
    schedule_id: str = Field(..., description="Hedera schedule ID")
    transaction_data: str = Field(..., description="Transaction description")


@router.post("/agents/register", response_model=Dict[str, Any])
async def register_agent(
    request: AgentRegistrationRequest,
    req: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Register a new AI agent in HCS-10 registry"""
    try:
        # Check if agent already exists
        from sqlalchemy import select
        
        existing_query = select(AIAgent).where(AIAgent.account_id == request.account_id)
        result = await db.execute(existing_query)
        existing_agent = result.scalar_one_or_none()
        
        if existing_agent:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Agent with this account ID already exists"
            )
        
        # Create new agent
        agent = AIAgent(
            account_id=request.account_id,
            agent_name=request.agent_name,
            agent_type=request.agent_type,
            capabilities=request.capabilities,
            profile_metadata=request.profile_metadata,
            max_connections=request.max_connections or 100,
            status=AgentStatus.INACTIVE  # Will be activated after registration
        )
        
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        
        # Get agent registry from app state
        agent_registry: AgentRegistry = req.app.state.agent_registry
        
        # Create agent topics
        topics = await agent_registry.create_agent_topics(agent)
        
        # Register agent in HCS-10 registry
        registration_tx_id = await agent_registry.register_agent(agent)
        
        if registration_tx_id:
            agent.registration_tx_id = registration_tx_id
            agent.status = AgentStatus.ACTIVE
            await db.commit()
        
        logger.info(f"Registered agent {agent.account_id} with topics: {topics}")
        
        return {
            "status": "success",
            "agent_id": agent.id,
            "account_id": agent.account_id,
            "registration_tx_id": registration_tx_id,
            "inbound_topic_id": agent.inbound_topic_id,
            "outbound_topic_id": agent.outbound_topic_id,
            "message": "Agent registered successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register agent"
        )


@router.get("/agents", response_model=List[AgentResponse])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[AgentStatus] = None,
    agent_type_filter: Optional[AgentType] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Get list of registered AI agents"""
    try:
        from sqlalchemy import select
        
        query = select(AIAgent).offset(skip).limit(limit)
        
        if status_filter:
            query = query.where(AIAgent.status == status_filter)
        
        if agent_type_filter:
            query = query.where(AIAgent.agent_type == agent_type_filter)
        
        result = await db.execute(query)
        agents = result.scalars().all()
        
        return [
            AgentResponse(
                id=agent.id,
                account_id=agent.account_id,
                agent_name=agent.agent_name,
                agent_type=agent.agent_type,
                status=agent.status,
                inbound_topic_id=agent.inbound_topic_id,
                outbound_topic_id=agent.outbound_topic_id,
                capabilities=agent.capabilities,
                ttl=agent.ttl,
                max_connections=agent.max_connections,
                active_connections=agent.active_connections,
                reputation_score=agent.reputation_score,
                trust_level=agent.trust_level,
                aether_balance=agent.aether_balance,
                last_activity=agent.last_activity.isoformat() if agent.last_activity else None,
                created_at=agent.created_at.isoformat()
            )
            for agent in agents
        ]
        
    except Exception as e:
        logger.error(f"Failed to get agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agents"
        )


@router.get("/agents/{account_id}", response_model=AgentResponse)
async def get_agent(
    account_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Get specific AI agent by account ID"""
    try:
        from sqlalchemy import select
        
        query = select(AIAgent).where(AIAgent.account_id == account_id)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        return AgentResponse(
            id=agent.id,
            account_id=agent.account_id,
            agent_name=agent.agent_name,
            agent_type=agent.agent_type,
            status=agent.status,
            inbound_topic_id=agent.inbound_topic_id,
            outbound_topic_id=agent.outbound_topic_id,
            capabilities=agent.capabilities,
            ttl=agent.ttl,
            max_connections=agent.max_connections,
            active_connections=agent.active_connections,
            reputation_score=agent.reputation_score,
            trust_level=agent.trust_level,
            aether_balance=agent.aether_balance,
            last_activity=agent.last_activity.isoformat() if agent.last_activity else None,
            created_at=agent.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {account_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent"
        )


@router.post("/connections/request")
async def request_connection(
    request: ConnectionRequest,
    req: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Send connection request to another agent"""
    try:
        from sqlalchemy import select
        
        # Get requesting agent
        query = select(AIAgent).where(AIAgent.account_id == request.from_agent_id)
        result = await db.execute(query)
        from_agent = result.scalar_one_or_none()
        
        if not from_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requesting agent not found"
            )
        
        # Get agent registry from app state
        agent_registry: AgentRegistry = req.app.state.agent_registry
        
        # Send connection request
        tx_id = await agent_registry.send_connection_request(
            from_agent=from_agent,
            to_agent_inbound_topic=request.to_agent_inbound_topic
        )
        
        if tx_id:
            await db.commit()
            logger.info(f"Connection request sent from {request.from_agent_id}")
        
        return {
            "status": "success" if tx_id else "failed",
            "tx_id": tx_id,
            "message": "Connection request sent" if tx_id else "Failed to send connection request"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send connection request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send connection request"
        )


@router.post("/messages/send")
async def send_message(
    request: MessageRequest,
    req: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Send message through connection topic"""
    try:
        from sqlalchemy import select
        
        # Get sending agent
        query = select(AIAgent).where(AIAgent.account_id == request.from_agent_id)
        result = await db.execute(query)
        from_agent = result.scalar_one_or_none()
        
        if not from_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sending agent not found"
            )
        
        # Get agent registry from app state
        agent_registry: AgentRegistry = req.app.state.agent_registry
        
        # Send message
        tx_id = await agent_registry.send_message(
            from_agent=from_agent,
            connection_topic_id=request.connection_topic_id,
            message_data=request.message_data
        )
        
        if tx_id:
            await db.commit()
            logger.info(f"Message sent from {request.from_agent_id}")
        
        return {
            "status": "success" if tx_id else "failed",
            "tx_id": tx_id,
            "message": "Message sent successfully" if tx_id else "Failed to send message"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.post("/transactions/request")
async def request_transaction(
    request: TransactionRequest,
    req: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Send transaction request requiring approval"""
    try:
        from sqlalchemy import select
        
        # Get requesting agent
        query = select(AIAgent).where(AIAgent.account_id == request.from_agent_id)
        result = await db.execute(query)
        from_agent = result.scalar_one_or_none()
        
        if not from_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requesting agent not found"
            )
        
        # Get agent registry from app state
        agent_registry: AgentRegistry = req.app.state.agent_registry
        
        # Send transaction request
        tx_id = await agent_registry.send_transaction_request(
            from_agent=from_agent,
            connection_topic_id=request.connection_topic_id,
            schedule_id=request.schedule_id,
            transaction_data=request.transaction_data
        )
        
        if tx_id:
            from_agent.increment_messages_sent()
            await db.commit()
            logger.info(f"Transaction request sent from {request.from_agent_id}")
        
        return {
            "status": "success" if tx_id else "failed",
            "tx_id": tx_id,
            "schedule_id": request.schedule_id,
            "message": "Transaction request sent" if tx_id else "Failed to send transaction request"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send transaction request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send transaction request"
        )


@router.get("/registry/info")
async def get_registry_info(req: Request):
    """Get HCS-10 registry information"""
    try:
        # Get agent registry from app state
        agent_registry: AgentRegistry = req.app.state.agent_registry
        
        registry_info = await agent_registry.get_registry_info()
        
        return {
            "status": "success",
            "registry_info": registry_info,
            "message": "Registry information retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get registry info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve registry information"
        )
