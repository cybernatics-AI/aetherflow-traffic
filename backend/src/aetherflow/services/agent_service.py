"""
Agent Service - Business Logic for AI Agent Management and HCS-10 Integration
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from aetherflow.core.logging import get_logger
from aetherflow.models.ai_agents import AIAgent
from aetherflow.hcs10.agent_registry import HCS10AgentRegistry
from aetherflow.hedera.client import HederaClient

logger = get_logger(__name__)


class AgentService:
    """Service for managing AI agents and HCS-10 operations"""
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        self.hedera_client = hedera_client
        self.hcs10_registry = HCS10AgentRegistry(hedera_client) if hedera_client else None
        
    async def register_agent(
        self,
        db: AsyncSession,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        owner_account_id: str,
        description: Optional[str] = None,
        model_hash: Optional[str] = None,
        pricing_model: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a new AI agent with HCS-10 integration"""
        
        logger.info(f"Registering AI agent: {agent_name}")
        
        # Create agent record
        agent = AIAgent(
            agent_name=agent_name,
            agent_type=agent_type,
            capabilities=capabilities,
            owner_account_id=owner_account_id,
            description=description,
            model_hash=model_hash,
            pricing_model=pricing_model or {},
            status="initializing",
            registration_timestamp=datetime.utcnow()
        )
        
        # Register with HCS-10 if available
        hcs10_registration = None
        if self.hcs10_registry:
            try:
                hcs10_registration = await self.hcs10_registry.register_agent(
                    agent_name=agent_name,
                    agent_type=agent_type,
                    capabilities=capabilities,
                    owner_account_id=owner_account_id,
                    description=description
                )
                
                agent.hcs_topic_id = hcs10_registration.get("inbound_topic_id")
                agent.outbound_topic_id = hcs10_registration.get("outbound_topic_id")
                agent.status = "active"
                
            except Exception as e:
                logger.error(f"Failed to register agent with HCS-10: {e}")
                agent.status = "registration_failed"
        
        # Save to database
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"Agent registered successfully: ID {agent.id}")
        
        return {
            "agent_id": agent.id,
            "agent_name": agent_name,
            "status": agent.status,
            "hcs_topic_id": agent.hcs_topic_id,
            "outbound_topic_id": agent.outbound_topic_id,
            "hcs10_registration": hcs10_registration,
            "timestamp": agent.registration_timestamp.isoformat()
        }
    
    async def get_agent(
        self,
        db: AsyncSession,
        agent_id: int
    ) -> Optional[AIAgent]:
        """Get agent by ID"""
        
        result = await db.execute(
            select(AIAgent).where(AIAgent.id == agent_id)
        )
        return result.scalar_one_or_none()
    
    async def get_agent_by_name(
        self,
        db: AsyncSession,
        agent_name: str
    ) -> Optional[AIAgent]:
        """Get agent by name"""
        
        result = await db.execute(
            select(AIAgent).where(AIAgent.agent_name == agent_name)
        )
        return result.scalar_one_or_none()
    
    async def list_agents(
        self,
        db: AsyncSession,
        agent_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AIAgent]:
        """List agents with optional filters"""
        
        query = select(AIAgent)
        
        if agent_type:
            query = query.where(AIAgent.agent_type == agent_type)
        
        if status:
            query = query.where(AIAgent.status == status)
        
        query = query.order_by(AIAgent.registration_timestamp.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_agent_metrics(
        self,
        db: AsyncSession,
        agent_id: int,
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update agent performance metrics"""
        
        agent = await self.get_agent(db, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Update metrics
        agent.performance_metrics = performance_metrics
        agent.last_activity = datetime.utcnow()
        
        # Update reputation based on performance
        agent.reputation_score = self._calculate_reputation(performance_metrics)
        
        await db.commit()
        
        logger.info(f"Updated metrics for agent {agent_id}")
        
        return {
            "agent_id": agent_id,
            "performance_metrics": performance_metrics,
            "reputation_score": agent.reputation_score,
            "timestamp": agent.last_activity.isoformat()
        }
    
    async def send_message_to_agent(
        self,
        db: AsyncSession,
        agent_id: int,
        message: str,
        sender_id: str,
        message_type: str = "request"
    ) -> Dict[str, Any]:
        """Send message to agent via HCS-10"""
        
        agent = await self.get_agent(db, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        if not agent.hcs_topic_id:
            raise ValueError(f"Agent {agent_id} does not have HCS topic configured")
        
        if not self.hcs10_registry:
            raise ValueError("HCS-10 registry not available")
        
        # Send message via HCS-10
        try:
            message_result = await self.hcs10_registry.send_message(
                target_agent_name=agent.agent_name,
                message=message,
                sender_id=sender_id,
                message_type=message_type
            )
            
            # Update agent activity
            agent.last_activity = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Message sent to agent {agent_id}")
            
            return {
                "agent_id": agent_id,
                "message_id": message_result.get("message_id"),
                "status": "sent",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send message to agent {agent_id}: {e}")
            raise
    
    async def request_agent_connection(
        self,
        db: AsyncSession,
        requester_agent_id: int,
        target_agent_id: int,
        connection_purpose: str
    ) -> Dict[str, Any]:
        """Request connection between two agents"""
        
        requester = await self.get_agent(db, requester_agent_id)
        target = await self.get_agent(db, target_agent_id)
        
        if not requester or not target:
            raise ValueError("One or both agents not found")
        
        if not self.hcs10_registry:
            raise ValueError("HCS-10 registry not available")
        
        try:
            connection_result = await self.hcs10_registry.request_connection(
                requester_agent_name=requester.agent_name,
                target_agent_name=target.agent_name,
                connection_purpose=connection_purpose
            )
            
            logger.info(f"Connection requested between agents {requester_agent_id} and {target_agent_id}")
            
            return {
                "requester_agent_id": requester_agent_id,
                "target_agent_id": target_agent_id,
                "connection_id": connection_result.get("connection_id"),
                "status": "requested",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to request connection: {e}")
            raise
    
    async def get_agent_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get overall agent statistics"""
        
        # Total agents
        total_result = await db.execute(select(func.count(AIAgent.id)))
        total_agents = total_result.scalar()
        
        # Active agents
        active_result = await db.execute(
            select(func.count(AIAgent.id))
            .where(AIAgent.status == "active")
        )
        active_agents = active_result.scalar()
        
        # Agents by type
        type_result = await db.execute(
            select(AIAgent.agent_type, func.count(AIAgent.id))
            .group_by(AIAgent.agent_type)
        )
        agents_by_type = dict(type_result.all())
        
        # Recent registrations (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_result = await db.execute(
            select(func.count(AIAgent.id))
            .where(AIAgent.registration_timestamp >= recent_cutoff)
        )
        recent_registrations = recent_result.scalar()
        
        # Average reputation
        avg_reputation_result = await db.execute(
            select(func.avg(AIAgent.reputation_score))
            .where(AIAgent.reputation_score.is_not(None))
        )
        avg_reputation = avg_reputation_result.scalar() or 0.0
        
        # Total earnings
        total_earnings_result = await db.execute(
            select(func.sum(AIAgent.total_earnings))
            .where(AIAgent.total_earnings.is_not(None))
        )
        total_earnings = total_earnings_result.scalar() or 0.0
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "agents_by_type": agents_by_type,
            "recent_registrations_24h": recent_registrations,
            "average_reputation": round(float(avg_reputation), 3),
            "total_earnings": round(float(total_earnings), 6),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_agent_performance_summary(
        self,
        db: AsyncSession,
        agent_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance summary for an agent"""
        
        agent = await self.get_agent(db, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Calculate performance metrics over time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # This would typically involve querying performance logs
        # For now, we'll use the current metrics
        
        performance_summary = {
            "agent_id": agent_id,
            "agent_name": agent.agent_name,
            "status": agent.status,
            "reputation_score": agent.reputation_score,
            "total_earnings": agent.total_earnings,
            "current_metrics": agent.performance_metrics or {},
            "registration_date": agent.registration_timestamp.isoformat(),
            "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
            "days_active": (datetime.utcnow() - agent.registration_timestamp).days,
            "hcs_integration": {
                "inbound_topic": agent.hcs_topic_id,
                "outbound_topic": agent.outbound_topic_id,
                "has_hcs10": bool(agent.hcs_topic_id)
            }
        }
        
        return performance_summary
    
    async def deactivate_agent(
        self,
        db: AsyncSession,
        agent_id: int,
        reason: str = "user_request"
    ) -> Dict[str, Any]:
        """Deactivate an agent"""
        
        agent = await self.get_agent(db, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Update status
        agent.status = "inactive"
        agent.last_activity = datetime.utcnow()
        
        # TODO: Cleanup HCS-10 registration if needed
        
        await db.commit()
        
        logger.info(f"Deactivated agent {agent_id}: {reason}")
        
        return {
            "agent_id": agent_id,
            "status": "inactive",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_reputation(self, performance_metrics: Dict[str, Any]) -> float:
        """Calculate reputation score based on performance metrics"""
        
        # Base reputation
        reputation = 0.5
        
        # Adjust based on various metrics
        if "success_rate" in performance_metrics:
            success_rate = performance_metrics["success_rate"]
            reputation += (success_rate - 0.5) * 0.4
        
        if "response_time" in performance_metrics:
            # Lower response time is better
            response_time = performance_metrics["response_time"]
            if response_time < 1.0:
                reputation += 0.1
            elif response_time > 5.0:
                reputation -= 0.1
        
        if "accuracy" in performance_metrics:
            accuracy = performance_metrics["accuracy"]
            reputation += (accuracy - 0.5) * 0.3
        
        if "uptime" in performance_metrics:
            uptime = performance_metrics["uptime"]
            reputation += (uptime - 0.9) * 0.2
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, reputation))
    
    async def search_agents(
        self,
        db: AsyncSession,
        capabilities: Optional[List[str]] = None,
        min_reputation: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for agents based on criteria"""
        
        query = select(AIAgent).where(AIAgent.status == "active")
        
        if min_reputation is not None:
            query = query.where(AIAgent.reputation_score >= min_reputation)
        
        # For capabilities and pricing, we'd need more complex queries
        # This is a simplified version
        
        query = query.order_by(AIAgent.reputation_score.desc()).limit(limit)
        
        result = await db.execute(query)
        agents = result.scalars().all()
        
        # Filter by capabilities if specified
        if capabilities:
            filtered_agents = []
            for agent in agents:
                if agent.capabilities and any(cap in agent.capabilities for cap in capabilities):
                    filtered_agents.append(agent)
            agents = filtered_agents
        
        # Convert to dict format
        agent_list = []
        for agent in agents:
            agent_dict = {
                "agent_id": agent.id,
                "agent_name": agent.agent_name,
                "agent_type": agent.agent_type,
                "capabilities": agent.capabilities,
                "reputation_score": agent.reputation_score,
                "pricing_model": agent.pricing_model,
                "description": agent.description,
                "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
            }
            agent_list.append(agent_dict)
        
        return agent_list
