#!/usr/bin/env python3
"""
AetherFlow Backend API Demo Script
Demonstrates the key features of the AetherFlow backend including:
- Vehicle data submission
- AI agent registration and communication (HCS-10)
- Traffic optimization
- Hedera integration
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, List
from datetime import datetime


class AetherFlowAPIDemo:
    """Demo client for AetherFlow Backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        
    async def run_demo(self):
        """Run complete API demonstration"""
        print("🚀 AetherFlow Backend API Demo")
        print("=" * 50)
        
        async with httpx.AsyncClient() as client:
            # Test basic connectivity
            await self.test_health_check(client)
            
            # Demo vehicle data submission
            await self.demo_vehicle_data(client)
            
            # Demo AI agent registration and communication
            await self.demo_ai_agents(client)
            
            # Demo HCS-10 communication
            await self.demo_hcs10_communication(client)
            
            # Demo traffic optimization
            await self.demo_traffic_optimization(client)
            
            # Demo Hedera integration
            await self.demo_hedera_integration(client)
        
        print("\n✅ Demo completed successfully!")
    
    async def test_health_check(self, client: httpx.AsyncClient):
        """Test basic API health"""
        print("\n🔍 Testing API Health...")
        
        try:
            response = await client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API is healthy")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    async def demo_vehicle_data(self, client: httpx.AsyncClient):
        """Demonstrate vehicle data submission"""
        print("\n🚗 Vehicle Data Submission Demo...")
        
        # Sample vehicle data submissions
        vehicle_data_samples = [
            {
                "vehicle_id": "DEMO_VEHICLE_001",
                "speed": 45.5,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "heading": 90.0,
                "altitude": 10.0,
                "device_type": "OBD-II",
                "encrypted_data": {"fuel_level": 0.75, "engine_temp": 90},
                "zk_proof": {"proof": "mock_zk_proof_data", "verified": True}
            },
            {
                "vehicle_id": "DEMO_VEHICLE_002", 
                "speed": 60.2,
                "latitude": 40.7589,
                "longitude": -73.9851,
                "heading": 180.0,
                "device_type": "smartphone"
            },
            {
                "vehicle_id": "DEMO_VEHICLE_003",
                "speed": 35.8,
                "latitude": 40.7505,
                "longitude": -73.9934,
                "heading": 270.0,
                "altitude": 15.0,
                "device_type": "fleet_tracker"
            }
        ]
        
        submitted_ids = []
        
        for i, data in enumerate(vehicle_data_samples, 1):
            try:
                print(f"   Submitting vehicle data {i}/3...")
                response = await client.post(
                    f"{self.api_base}/vehicle-data/submit",
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Vehicle {data['vehicle_id']} data submitted")
                    print(f"      Data hash: {result['data_hash'][:16]}...")
                    print(f"      Reward: {result['reward_amount']} $AETHER")
                else:
                    print(f"   ❌ Failed to submit data: {response.status_code}")
                    print(f"      Error: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error submitting vehicle data: {e}")
        
        # Retrieve submitted data
        try:
            print("   Retrieving vehicle data...")
            response = await client.get(f"{self.api_base}/vehicle-data/")
            
            if response.status_code == 200:
                data_records = response.json()
                print(f"   ✅ Retrieved {len(data_records)} vehicle data records")
                
                for record in data_records[-3:]:  # Show last 3 records
                    print(f"      ID: {record['id']}, Vehicle: {record['vehicle_id']}, "
                          f"Speed: {record['speed']} km/h, Reward: {record['reward_amount']} $AETHER")
            else:
                print(f"   ❌ Failed to retrieve data: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error retrieving vehicle data: {e}")
    
    async def demo_ai_agents(self, client: httpx.AsyncClient):
        """Demonstrate AI agent management"""
        print("\n🤖 AI Agent Management Demo...")
        
        # Sample AI agents
        agents = [
            {
                "agent_name": "TrafficOptimizer_NYC",
                "agent_type": "traffic_optimizer",
                "account_id": "0.0.123001",
                "capabilities": ["traffic_analysis", "route_optimization", "congestion_prediction"],
                "profile_metadata": {
                    "city": "New York",
                    "coverage_area": "Manhattan",
                    "specialization": "urban_traffic"
                },
                "max_connections": 50
            },
            {
                "agent_name": "DataValidator_Global",
                "agent_type": "data_validator", 
                "account_id": "0.0.123002",
                "capabilities": ["zk_proof_validation", "data_quality_assessment", "fraud_detection"],
                "profile_metadata": {
                    "validation_methods": ["zk_proofs", "statistical_analysis"],
                    "accuracy_rate": 0.99
                },
                "max_connections": 100
            },
            {
                "agent_name": "RewardDistributor_Main",
                "agent_type": "reward_distributor",
                "account_id": "0.0.123003", 
                "capabilities": ["token_distribution", "reward_calculation", "payment_processing"],
                "profile_metadata": {
                    "supported_tokens": ["AETHER", "HBAR"],
                    "distribution_frequency": "real_time"
                },
                "max_connections": 200
            }
        ]
        
        registered_agents = []
        
        for i, agent_data in enumerate(agents, 1):
            try:
                print(f"   Registering AI agent {i}/3: {agent_data['agent_name']}...")
                response = await client.post(
                    f"{self.api_base}/hcs10/agents/register",
                    json=agent_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    registered_agents.append(result)
                    print(f"   ✅ Agent registered successfully")
                    print(f"      Account ID: {result['account_id']}")
                    print(f"      Inbound Topic: {result.get('inbound_topic_id', 'N/A')}")
                    print(f"      Outbound Topic: {result.get('outbound_topic_id', 'N/A')}")
                else:
                    print(f"   ❌ Failed to register agent: {response.status_code}")
                    print(f"      Error: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error registering agent: {e}")
        
        # List registered agents
        try:
            print("   Retrieving registered agents...")
            response = await client.get(f"{self.api_base}/hcs10/agents")
            
            if response.status_code == 200:
                agents_list = response.json()
                print(f"   ✅ Retrieved {len(agents_list)} registered agents")
                
                for agent in agents_list[-3:]:  # Show last 3 agents
                    print(f"      {agent['agent_name']} ({agent['agent_type']}) - "
                          f"Status: {agent['status']}, Connections: {agent['active_connections']}")
            else:
                print(f"   ❌ Failed to retrieve agents: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error retrieving agents: {e}")
        
        return registered_agents
    
    async def demo_hcs10_communication(self, client: httpx.AsyncClient):
        """Demonstrate HCS-10 communication features"""
        print("\n💬 HCS-10 Communication Demo...")
        
        # Get registry info
        try:
            print("   Getting registry information...")
            response = await client.get(f"{self.api_base}/hcs10/registry/info")
            
            if response.status_code == 200:
                registry_info = response.json()
                print("   ✅ Registry information retrieved")
                print(f"      Status: {registry_info.get('status', 'unknown')}")
            else:
                print(f"   ❌ Failed to get registry info: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error getting registry info: {e}")
        
        # Demo connection request
        try:
            print("   Simulating agent connection request...")
            connection_request = {
                "from_agent_id": "0.0.123001",
                "to_agent_inbound_topic": "0.0.789102"
            }
            
            response = await client.post(
                f"{self.api_base}/hcs10/connections/request",
                json=connection_request
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Connection request sent")
                print(f"      Status: {result.get('status', 'unknown')}")
                print(f"      TX ID: {result.get('tx_id', 'N/A')}")
            else:
                print(f"   ❌ Failed to send connection request: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error sending connection request: {e}")
        
        # Demo message sending
        try:
            print("   Simulating agent message...")
            message_request = {
                "from_agent_id": "0.0.123001",
                "connection_topic_id": "0.0.567890",
                "message_data": "Hello! Traffic optimization data available for Manhattan area."
            }
            
            response = await client.post(
                f"{self.api_base}/hcs10/messages/send",
                json=message_request
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Message sent successfully")
                print(f"      Status: {result.get('status', 'unknown')}")
            else:
                print(f"   ❌ Failed to send message: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error sending message: {e}")
    
    async def demo_traffic_optimization(self, client: httpx.AsyncClient):
        """Demonstrate traffic optimization features"""
        print("\n🚦 Traffic Optimization Demo...")
        
        # This would be implemented when traffic optimization endpoints are created
        print("   📝 Traffic optimization endpoints coming soon...")
        print("   Features will include:")
        print("      - Real-time traffic light optimization")
        print("      - Route recommendations")
        print("      - Congestion prediction")
        print("      - Emergency vehicle priority routing")
    
    async def demo_hedera_integration(self, client: httpx.AsyncClient):
        """Demonstrate Hedera network integration"""
        print("\n🌐 Hedera Integration Demo...")
        
        # This would be implemented when Hedera endpoints are created
        print("   📝 Hedera integration endpoints coming soon...")
        print("   Features will include:")
        print("      - HCS topic management")
        print("      - HTS token operations")
        print("      - Account balance queries")
        print("      - Transaction status tracking")
        print("      - Smart contract interactions")


async def main():
    """Main demo function"""
    demo = AetherFlowAPIDemo()
    
    print("Starting AetherFlow Backend API Demo...")
    print("Make sure the backend server is running on http://localhost:8000")
    print("\nPress Ctrl+C to stop the demo at any time.")
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
