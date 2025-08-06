"""
HCS-10 OpenConvAI Agent Registry Implementation
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from aetherflow.hedera.client import HederaClient
from aetherflow.models.ai_agents import AIAgent, AgentStatus, AgentType
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """HCS-10 OpenConvAI Agent Registry Manager"""
    
    def __init__(self, hedera_client: HederaClient, registry_topic_id: Optional[str] = None):
        """Initialize agent registry"""
        self.hedera_client = hedera_client
        self.registry_topic_id = registry_topic_id
        self.ttl = 60  # Default TTL for topics
    
    async def initialize_registry(self) -> Optional[str]:
        """Initialize the agent registry topic if not exists"""
        if self.registry_topic_id:
            logger.info(f"Using existing registry topic: {self.registry_topic_id}")
            return self.registry_topic_id
        
        # Create registry topic with HCS-10 memo format
        memo = f"hcs-10:0:{self.ttl}:3:"
        topic_id = await self.hedera_client.create_topic(memo=memo, admin_key=True)
        
        if topic_id:
            self.registry_topic_id = topic_id
            logger.info(f"Created new registry topic: {topic_id}")
        
        return topic_id
    
    async def register_agent(self, agent: AIAgent) -> Optional[str]:
        """Register an AI agent in the HCS-10 registry"""
        if not self.registry_topic_id:
            await self.initialize_registry()
        
        if not self.registry_topic_id:
            logger.error("Failed to initialize registry topic")
            return None
        
        # Create HCS-10 register operation payload
        register_payload = agent.get_hcs10_register_payload()
        
        # Submit registration message to registry topic
        memo = "hcs-10:op:0:0"  # Register operation memo
        tx_id = await self.hedera_client.submit_message(
            topic_id=self.registry_topic_id,
            message=register_payload,
            memo=memo
        )
        
        if tx_id:
            agent.registration_tx_id = tx_id
            agent.status = AgentStatus.ACTIVE
            logger.info(f"Registered agent {agent.account_id} with tx: {tx_id}")
        
        return tx_id
    
    async def delete_agent(self, agent: AIAgent, uid: str) -> Optional[str]:
        """Delete an AI agent from the HCS-10 registry"""
        if not self.registry_topic_id:
            logger.error("Registry topic not initialized")
            return None
        
        # Create HCS-10 delete operation payload
        delete_payload = {
            "p": "hcs-10",
            "op": "delete",
            "uid": uid,
            "m": f"Removing agent {agent.agent_name} from registry."
        }
        
        # Submit delete message to registry topic
        memo = "hcs-10:op:1:0"  # Delete operation memo
        tx_id = await self.hedera_client.submit_message(
            topic_id=self.registry_topic_id,
            message=delete_payload,
            memo=memo
        )
        
        if tx_id:
            agent.status = AgentStatus.DELETED
            logger.info(f"Deleted agent {agent.account_id} with tx: {tx_id}")
        
        return tx_id
    
    async def create_agent_topics(self, agent: AIAgent) -> Dict[str, Optional[str]]:
        """Create inbound and outbound topics for an agent"""
        topics = {
            "inbound": None,
            "outbound": None
        }
        
        # Create inbound topic
        inbound_memo = agent.get_topic_memo("inbound")
        inbound_topic_id = await self.hedera_client.create_topic(
            memo=inbound_memo,
            admin_key=True
        )
        
        if inbound_topic_id:
            topics["inbound"] = inbound_topic_id
            agent.inbound_topic_id = inbound_topic_id
            logger.info(f"Created inbound topic for {agent.account_id}: {inbound_topic_id}")
        
        # Create outbound topic
        outbound_memo = agent.get_topic_memo("outbound")
        outbound_topic_id = await self.hedera_client.create_topic(
            memo=outbound_memo,
            admin_key=True
        )
        
        if outbound_topic_id:
            topics["outbound"] = outbound_topic_id
            agent.outbound_topic_id = outbound_topic_id
            logger.info(f"Created outbound topic for {agent.account_id}: {outbound_topic_id}")
        
        return topics
    
    async def send_connection_request(self, from_agent: AIAgent, to_agent_inbound_topic: str) -> Optional[str]:
        """Send connection request to another agent"""
        if not from_agent.outbound_topic_id:
            logger.error(f"Agent {from_agent.account_id} has no outbound topic")
            return None
        
        # Create connection request payload
        connection_request = {
            "p": "hcs-10",
            "op": "connection_request",
            "operator_id": f"{from_agent.account_id}@{from_agent.inbound_topic_id}",
            "m": f"Requesting connection from {from_agent.agent_name}"
        }
        
        # Submit to target agent's inbound topic
        memo = "hcs-10:op:3:1"  # Connection request memo
        tx_id = await self.hedera_client.submit_message(
            topic_id=to_agent_inbound_topic,
            message=connection_request,
            memo=memo
        )
        
        if tx_id:
            from_agent.increment_messages_sent()
            logger.info(f"Sent connection request from {from_agent.account_id} to {to_agent_inbound_topic}")
        
        return tx_id
    
    async def create_connection_topic(self, agent_a: AIAgent, agent_b: AIAgent, connection_id: int) -> Optional[str]:
        """Create a private connection topic between two agents"""
        # Connection topic memo format
        memo = f"hcs-10:1:{self.ttl}:2:{agent_a.inbound_topic_id}:{connection_id}"
        
        connection_topic_id = await self.hedera_client.create_topic(
            memo=memo,
            admin_key=True
        )
        
        if connection_topic_id:
            logger.info(f"Created connection topic between {agent_a.account_id} and {agent_b.account_id}: {connection_topic_id}")
            
            # Send connection_created message to both agents' inbound topics
            await self._notify_connection_created(agent_a, agent_b, connection_topic_id, connection_id)
            await self._notify_connection_created(agent_b, agent_a, connection_topic_id, connection_id)
        
        return connection_topic_id
    
    async def _notify_connection_created(self, to_agent: AIAgent, from_agent: AIAgent, connection_topic_id: str, connection_id: int) -> Optional[str]:
        """Notify agent that connection has been created"""
        connection_created = {
            "p": "hcs-10",
            "op": "connection_created",
            "connection_topic_id": connection_topic_id,
            "connected_account_id": from_agent.account_id,
            "operator_id": f"{from_agent.account_id}@{from_agent.inbound_topic_id}",
            "connection_id": connection_id,
            "m": f"Connection established with {from_agent.agent_name}"
        }
        
        memo = "hcs-10:op:4:1"  # Connection created memo
        tx_id = await self.hedera_client.submit_message(
            topic_id=to_agent.inbound_topic_id,
            message=connection_created,
            memo=memo
        )
        
        if tx_id:
            to_agent.increment_messages_received()
            to_agent.active_connections += 1
        
        return tx_id
    
    async def send_message(self, from_agent: AIAgent, connection_topic_id: str, message_data: str) -> Optional[str]:
        """Send message through connection topic"""
        message_payload = {
            "p": "hcs-10",
            "op": "message",
            "operator_id": f"{from_agent.account_id}@{from_agent.inbound_topic_id}",
            "data": message_data,
            "m": "Standard communication."
        }
        
        memo = "hcs-10:op:6:3"  # Message operation memo
        tx_id = await self.hedera_client.submit_message(
            topic_id=connection_topic_id,
            message=message_payload,
            memo=memo
        )
        
        if tx_id:
            from_agent.increment_messages_sent()
            logger.info(f"Sent message from {from_agent.account_id} to connection topic {connection_topic_id}")
        
        return tx_id
    
    async def send_transaction_request(self, from_agent: AIAgent, connection_topic_id: str, schedule_id: str, transaction_data: str) -> Optional[str]:
        """Send transaction request requiring approval"""
        transaction_payload = {
            "p": "hcs-10",
            "op": "transaction",
            "operator_id": f"{from_agent.account_id}@{from_agent.inbound_topic_id}",
            "schedule_id": schedule_id,
            "data": transaction_data,
            "m": "For your approval."
        }
        
        memo = "hcs-10:op:7:3"  # Transaction operation memo
        tx_id = await self.hedera_client.submit_message(
            topic_id=connection_topic_id,
            message=transaction_payload,
            memo=memo
        )
        
        if tx_id:
            from_agent.increment_messages_sent()
            logger.info(f"Sent transaction request from {from_agent.account_id} to connection topic {connection_topic_id}")
        
        return tx_id
    
    async def get_registry_info(self) -> Optional[Dict[str, Any]]:
        """Get registry topic information"""
        if not self.registry_topic_id:
            return None
        
        return await self.hedera_client.get_topic_info(self.registry_topic_id)
