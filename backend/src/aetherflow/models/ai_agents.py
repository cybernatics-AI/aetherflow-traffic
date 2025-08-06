"""
AI Agents Model for HCS-10 OpenConvAI Integration
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float
from enum import Enum

from aetherflow.core.database import Base


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class AgentType(str, Enum):
    """Agent type enumeration"""
    TRAFFIC_OPTIMIZER = "traffic_optimizer"
    DATA_VALIDATOR = "data_validator"
    REWARD_DISTRIBUTOR = "reward_distributor"
    FEDERATED_LEARNER = "federated_learner"
    MARKET_MAKER = "market_maker"
    GENERAL_PURPOSE = "general_purpose"


class AIAgent(Base):
    """AI Agents for HCS-10 OpenConvAI communication"""
    
    __tablename__ = "ai_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # HCS-10 OpenConvAI fields
    account_id = Column(String(50), nullable=False, unique=True, index=True)  # Hedera account ID
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False, default=AgentType.GENERAL_PURPOSE)
    status = Column(String(20), nullable=False, default=AgentStatus.ACTIVE)
    
    # HCS Topics
    registry_topic_id = Column(String(50), nullable=True)
    inbound_topic_id = Column(String(50), nullable=True, index=True)
    outbound_topic_id = Column(String(50), nullable=True, index=True)
    
    # Agent capabilities and metadata
    capabilities = Column(JSON, nullable=True)  # List of agent capabilities
    profile_metadata = Column(JSON, nullable=True)  # HCS-11 Profile Standard data
    
    # Communication settings
    ttl = Column(Integer, default=60)  # Time-to-live for messages
    max_connections = Column(Integer, default=100)
    active_connections = Column(Integer, default=0)
    
    # Performance metrics
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    
    # Reputation and trust
    reputation_score = Column(Float, default=1.0)  # 0.0 to 1.0
    trust_level = Column(String(20), default="basic")  # basic, trusted, verified
    
    # Economic data
    aether_balance = Column(Float, default=0.0)
    total_rewards_earned = Column(Float, default=0.0)
    total_fees_paid = Column(Float, default=0.0)
    
    # Registration and lifecycle
    registration_tx_id = Column(String(100), nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "account_id": self.account_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "status": self.status,
            "inbound_topic_id": self.inbound_topic_id,
            "outbound_topic_id": self.outbound_topic_id,
            "capabilities": self.capabilities,
            "ttl": self.ttl,
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "reputation_score": self.reputation_score,
            "trust_level": self.trust_level,
            "aether_balance": self.aether_balance,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def get_hcs10_register_payload(self) -> Dict[str, Any]:
        """Get HCS-10 register operation payload"""
        return {
            "p": "hcs-10",
            "op": "register",
            "account_id": self.account_id,
            "m": f"Registering {self.agent_type} agent: {self.agent_name}"
        }
    
    def get_topic_memo(self, topic_type: str) -> str:
        """Generate HCS-10 topic memo format"""
        type_map = {
            "registry": "3",
            "inbound": "0",
            "outbound": "1",
            "connection": "2"
        }
        
        if topic_type == "registry":
            return f"hcs-10:0:{self.ttl}:3:{self.registry_topic_id or ''}"
        elif topic_type == "inbound":
            return f"hcs-10:0:{self.ttl}:0:{self.account_id}"
        elif topic_type == "outbound":
            return f"hcs-10:0:{self.ttl}:1"
        else:
            return f"hcs-10:0:{self.ttl}:{type_map.get(topic_type, '0')}"
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def increment_messages_sent(self) -> None:
        """Increment messages sent counter"""
        self.messages_sent += 1
        self.update_activity()
    
    def increment_messages_received(self) -> None:
        """Increment messages received counter"""
        self.messages_received += 1
        self.update_activity()
