"""
Federated Learning Coordinator for AetherFlow
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

from aetherflow.core.logging import get_logger
from aetherflow.models.ai_agents import AIAgent, AgentType

logger = get_logger(__name__)


class FederatedLearningCoordinator:
    """Coordinates federated learning across multiple AI agents"""
    
    def __init__(self):
        self.participants: Dict[str, AIAgent] = {}
        self.current_round = 0
        self.global_model_weights: Optional[Dict[str, Any]] = None
        self.learning_rate = 0.01
        self.min_participants = 3
        
    async def register_participant(self, agent: AIAgent) -> bool:
        """Register an AI agent as federated learning participant"""
        if agent.agent_type != AgentType.FEDERATED_LEARNER:
            logger.warning(f"Agent {agent.account_id} is not a federated learner")
            return False
        
        self.participants[agent.account_id] = agent
        logger.info(f"Registered federated learning participant: {agent.account_id}")
        return True
    
    async def start_training_round(self) -> Dict[str, Any]:
        """Start a new federated learning training round"""
        if len(self.participants) < self.min_participants:
            raise ValueError(f"Need at least {self.min_participants} participants, got {len(self.participants)}")
        
        self.current_round += 1
        logger.info(f"Starting federated learning round {self.current_round}")
        
        # Initialize global model if first round
        if self.global_model_weights is None:
            self.global_model_weights = self._initialize_global_model()
        
        # Send global model to participants
        training_tasks = []
        for agent_id, agent in self.participants.items():
            task = self._send_model_to_agent(agent, self.global_model_weights)
            training_tasks.append(task)
        
        # Wait for all participants to complete local training
        local_updates = await asyncio.gather(*training_tasks, return_exceptions=True)
        
        # Filter successful updates
        valid_updates = [
            update for update in local_updates 
            if not isinstance(update, Exception) and update is not None
        ]
        
        if len(valid_updates) < self.min_participants:
            logger.error(f"Not enough valid updates: {len(valid_updates)}")
            return {"status": "failed", "reason": "insufficient_participants"}
        
        # Aggregate local updates
        new_global_weights = self._aggregate_updates(valid_updates)
        self.global_model_weights = new_global_weights
        
        logger.info(f"Completed federated learning round {self.current_round}")
        
        return {
            "status": "success",
            "round": self.current_round,
            "participants": len(valid_updates),
            "global_model_version": f"v{self.current_round}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_model_to_agent(self, agent: AIAgent, model_weights: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send global model to agent for local training"""
        try:
            # Simulate sending model and receiving local update
            # In real implementation, this would use HCS-10 communication
            
            # Mock local training simulation
            await asyncio.sleep(0.1)  # Simulate training time
            
            # Generate mock local update
            local_update = self._simulate_local_training(agent.account_id, model_weights)
            
            logger.debug(f"Received local update from {agent.account_id}")
            return local_update
            
        except Exception as e:
            logger.error(f"Failed to get update from agent {agent.account_id}: {e}")
            return None
    
    def _simulate_local_training(self, agent_id: str, global_weights: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate local training and return weight updates"""
        # Mock local training with random updates
        local_weights = {}
        
        for layer_name, weights in global_weights.items():
            if isinstance(weights, list):
                # Add small random updates to simulate local training
                noise = np.random.normal(0, 0.01, len(weights))
                local_weights[layer_name] = [w + n for w, n in zip(weights, noise)]
            else:
                local_weights[layer_name] = weights
        
        return {
            "agent_id": agent_id,
            "weights": local_weights,
            "samples": np.random.randint(100, 1000),  # Mock number of training samples
            "loss": np.random.uniform(0.1, 0.5),  # Mock training loss
            "accuracy": np.random.uniform(0.7, 0.95)  # Mock accuracy
        }
    
    def _initialize_global_model(self) -> Dict[str, Any]:
        """Initialize global model weights"""
        # Mock neural network weights for traffic prediction
        return {
            "input_layer": [0.1] * 10,  # 10 input features (speed, location, time, etc.)
            "hidden_layer_1": [0.05] * 20,  # 20 hidden neurons
            "hidden_layer_2": [0.02] * 15,  # 15 hidden neurons
            "output_layer": [0.01] * 5,  # 5 output classes (traffic levels)
            "bias_1": [0.0] * 20,
            "bias_2": [0.0] * 15,
            "bias_output": [0.0] * 5
        }
    
    def _aggregate_updates(self, local_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate local model updates using federated averaging"""
        total_samples = sum(update["samples"] for update in local_updates)
        aggregated_weights = {}
        
        # Get layer names from first update
        layer_names = local_updates[0]["weights"].keys()
        
        for layer_name in layer_names:
            # Weighted average based on number of samples
            weighted_sum = None
            
            for update in local_updates:
                weight = update["samples"] / total_samples
                layer_weights = update["weights"][layer_name]
                
                if weighted_sum is None:
                    weighted_sum = [w * weight for w in layer_weights]
                else:
                    weighted_sum = [ws + w * weight for ws, w in zip(weighted_sum, layer_weights)]
            
            aggregated_weights[layer_name] = weighted_sum
        
        logger.info(f"Aggregated weights from {len(local_updates)} participants")
        return aggregated_weights
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get current global model performance metrics"""
        if not self.participants:
            return {"status": "no_participants"}
        
        # Mock performance metrics
        return {
            "round": self.current_round,
            "participants": len(self.participants),
            "global_accuracy": np.random.uniform(0.8, 0.95),
            "global_loss": np.random.uniform(0.05, 0.2),
            "convergence_rate": np.random.uniform(0.01, 0.05),
            "model_size_mb": 2.5,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def predict_traffic(self, features: List[float]) -> Dict[str, Any]:
        """Use global model to predict traffic conditions"""
        if self.global_model_weights is None:
            raise ValueError("Global model not initialized")
        
        # Mock prediction using global model
        # In real implementation, this would use actual neural network inference
        
        # Simulate forward pass
        prediction_scores = [
            0.1,  # Very Light Traffic
            0.2,  # Light Traffic  
            0.4,  # Moderate Traffic
            0.25, # Heavy Traffic
            0.05  # Very Heavy Traffic
        ]
        
        predicted_class = np.argmax(prediction_scores)
        confidence = max(prediction_scores)
        
        traffic_levels = ["Very Light", "Light", "Moderate", "Heavy", "Very Heavy"]
        
        return {
            "predicted_traffic_level": traffic_levels[predicted_class],
            "confidence": confidence,
            "prediction_scores": prediction_scores,
            "model_version": f"v{self.current_round}",
            "timestamp": datetime.utcnow().isoformat()
        }
