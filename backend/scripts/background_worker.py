#!/usr/bin/env python3
"""
Background Worker for AetherFlow Backend
Handles asynchronous tasks and periodic jobs
"""

import asyncio
import sys
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aetherflow.core.database import get_db_session
from aetherflow.core.logging import get_logger
from aetherflow.core.config import get_settings
from aetherflow.services.vehicle_service import VehicleDataService
from aetherflow.services.traffic_service import TrafficService
from aetherflow.services.tokenomics_service import TokenomicsService
from aetherflow.services.agent_service import AgentService

logger = get_logger(__name__)


class BackgroundWorker:
    """Background worker for periodic tasks"""
    
    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.tasks = []
        
        # Initialize services
        self.vehicle_service = VehicleDataService()
        self.traffic_service = TrafficService()
        self.tokenomics_service = TokenomicsService()
        self.agent_service = AgentService()
        
        # Task intervals (in seconds)
        self.task_intervals = {
            'traffic_optimization': 300,      # 5 minutes
            'reward_distribution': 3600,      # 1 hour
            'data_cleanup': 86400,           # 24 hours
            'agent_health_check': 600,       # 10 minutes
            'nft_valuation_update': 1800,    # 30 minutes
            'derivative_pricing': 900,       # 15 minutes
            'system_metrics': 60,            # 1 minute
            'hedera_sync': 1200              # 20 minutes
        }
        
        # Last execution times
        self.last_execution = {task: datetime.min for task in self.task_intervals.keys()}
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def traffic_optimization_task(self):
        """Periodic traffic optimization task"""
        
        try:
            logger.info("🚦 Running traffic optimization task...")
            
            # Get all active intersections
            async with get_db_session() as db:
                from aetherflow.models.traffic_lights import TrafficLight
                from sqlalchemy import select
                
                result = await db.execute(
                    select(TrafficLight).where(TrafficLight.status == "active")
                )
                active_intersections = result.scalars().all()
            
            optimization_count = 0
            
            for intersection in active_intersections:
                try:
                    # Optimize each intersection
                    result = await self.traffic_service.optimize_intersection(
                        intersection.intersection_id
                    )
                    
                    if result.get("optimization_applied"):
                        optimization_count += 1
                        logger.debug(f"Optimized intersection {intersection.intersection_id}")
                
                except Exception as e:
                    logger.error(f"Failed to optimize intersection {intersection.intersection_id}: {e}")
            
            logger.info(f"✅ Traffic optimization completed: {optimization_count} intersections optimized")
            
        except Exception as e:
            logger.error(f"❌ Traffic optimization task failed: {e}")
    
    async def reward_distribution_task(self):
        """Periodic reward distribution task"""
        
        try:
            logger.info("💰 Running reward distribution task...")
            
            # Get pending rewards from the last hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            async with get_db_session() as db:
                from aetherflow.models.vehicle_data import VehicleData
                from sqlalchemy import select, func
                
                # Get vehicle data submissions that need reward processing
                result = await db.execute(
                    select(VehicleData.submitter_account_id, func.sum(VehicleData.reward_amount))
                    .where(
                        VehicleData.timestamp >= cutoff_time,
                        VehicleData.reward_distributed == False
                    )
                    .group_by(VehicleData.submitter_account_id)
                )
                
                pending_rewards = result.all()
            
            distribution_count = 0
            
            for account_id, total_reward in pending_rewards:
                if account_id and total_reward > 0:
                    try:
                        # Distribute rewards via tokenomics service
                        await self.tokenomics_service.distribute_rewards(
                            account_id, float(total_reward), "vehicle_data_submission"
                        )
                        
                        # Mark rewards as distributed
                        async with get_db_session() as db:
                            from sqlalchemy import update
                            
                            await db.execute(
                                update(VehicleData)
                                .where(
                                    VehicleData.submitter_account_id == account_id,
                                    VehicleData.timestamp >= cutoff_time,
                                    VehicleData.reward_distributed == False
                                )
                                .values(reward_distributed=True)
                            )
                            await db.commit()
                        
                        distribution_count += 1
                        logger.debug(f"Distributed {total_reward} AETHER to {account_id}")
                    
                    except Exception as e:
                        logger.error(f"Failed to distribute rewards to {account_id}: {e}")
            
            logger.info(f"✅ Reward distribution completed: {distribution_count} accounts processed")
            
        except Exception as e:
            logger.error(f"❌ Reward distribution task failed: {e}")
    
    async def data_cleanup_task(self):
        """Periodic data cleanup task"""
        
        try:
            logger.info("🧹 Running data cleanup task...")
            
            # Clean up old vehicle data (older than 90 days)
            cleanup_cutoff = datetime.utcnow() - timedelta(days=90)
            
            async with get_db_session() as db:
                from aetherflow.models.vehicle_data import VehicleData
                from sqlalchemy import delete
                
                # Count records to be deleted
                count_result = await db.execute(
                    select(func.count(VehicleData.id))
                    .where(VehicleData.timestamp < cleanup_cutoff)
                )
                records_to_delete = count_result.scalar()
                
                if records_to_delete > 0:
                    # Delete old records
                    await db.execute(
                        delete(VehicleData)
                        .where(VehicleData.timestamp < cleanup_cutoff)
                    )
                    await db.commit()
                    
                    logger.info(f"🗑️  Cleaned up {records_to_delete} old vehicle data records")
                else:
                    logger.info("No old records to clean up")
            
            # Clean up old log files
            log_dir = Path("logs")
            if log_dir.exists():
                log_cleanup_cutoff = datetime.utcnow() - timedelta(days=30)
                
                cleaned_files = 0
                for log_file in log_dir.glob("*.log.*"):
                    if log_file.stat().st_mtime < log_cleanup_cutoff.timestamp():
                        log_file.unlink()
                        cleaned_files += 1
                
                if cleaned_files > 0:
                    logger.info(f"🗑️  Cleaned up {cleaned_files} old log files")
            
            logger.info("✅ Data cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Data cleanup task failed: {e}")
    
    async def agent_health_check_task(self):
        """Periodic agent health check task"""
        
        try:
            logger.info("🤖 Running agent health check task...")
            
            # Get all registered agents
            async with get_db_session() as db:
                from aetherflow.models.ai_agents import AIAgent
                from sqlalchemy import select
                
                result = await db.execute(
                    select(AIAgent).where(AIAgent.status == "active")
                )
                active_agents = result.scalars().all()
            
            health_check_count = 0
            unhealthy_agents = []
            
            for agent in active_agents:
                try:
                    # Check agent health (this would ping the actual agent)
                    # For now, we'll simulate health checks
                    
                    # Check if agent has been active recently
                    last_activity_cutoff = datetime.utcnow() - timedelta(hours=2)
                    
                    if agent.last_seen and agent.last_seen < last_activity_cutoff:
                        unhealthy_agents.append(agent.agent_id)
                        logger.warning(f"Agent {agent.agent_name} appears inactive")
                    else:
                        health_check_count += 1
                
                except Exception as e:
                    logger.error(f"Health check failed for agent {agent.agent_name}: {e}")
                    unhealthy_agents.append(agent.agent_id)
            
            # Update agent statuses if needed
            if unhealthy_agents:
                async with get_db_session() as db:
                    from sqlalchemy import update
                    
                    await db.execute(
                        update(AIAgent)
                        .where(AIAgent.agent_id.in_(unhealthy_agents))
                        .values(status="inactive", last_health_check=datetime.utcnow())
                    )
                    await db.commit()
            
            logger.info(f"✅ Agent health check completed: {health_check_count} healthy, {len(unhealthy_agents)} unhealthy")
            
        except Exception as e:
            logger.error(f"❌ Agent health check task failed: {e}")
    
    async def nft_valuation_update_task(self):
        """Periodic NFT valuation update task"""
        
        try:
            logger.info("💎 Running NFT valuation update task...")
            
            # Get all active Traffic NFTs
            async with get_db_session() as db:
                from aetherflow.models.traffic_nfts import TrafficNFT
                from sqlalchemy import select
                
                result = await db.execute(
                    select(TrafficNFT).where(TrafficNFT.status == "active")
                )
                active_nfts = result.scalars().all()
            
            valuation_updates = 0
            
            for nft in active_nfts:
                try:
                    # Update NFT valuation based on performance
                    updated_nft = await self.tokenomics_service.update_nft_valuation(
                        nft.id, nft.performance_metrics
                    )
                    
                    if updated_nft:
                        valuation_updates += 1
                        logger.debug(f"Updated valuation for NFT {nft.id}")
                
                except Exception as e:
                    logger.error(f"Failed to update valuation for NFT {nft.id}: {e}")
            
            logger.info(f"✅ NFT valuation update completed: {valuation_updates} NFTs updated")
            
        except Exception as e:
            logger.error(f"❌ NFT valuation update task failed: {e}")
    
    async def derivative_pricing_task(self):
        """Periodic derivative pricing update task"""
        
        try:
            logger.info("📈 Running derivative pricing update task...")
            
            # Get all active derivatives
            async with get_db_session() as db:
                from aetherflow.models.derivatives import Derivative
                from sqlalchemy import select
                
                result = await db.execute(
                    select(Derivative).where(Derivative.status == "active")
                )
                active_derivatives = result.scalars().all()
            
            pricing_updates = 0
            
            for derivative in active_derivatives:
                try:
                    # Update derivative pricing based on current conditions
                    updated_derivative = await self.tokenomics_service.update_derivative_pricing(
                        derivative.id
                    )
                    
                    if updated_derivative:
                        pricing_updates += 1
                        logger.debug(f"Updated pricing for derivative {derivative.id}")
                
                except Exception as e:
                    logger.error(f"Failed to update pricing for derivative {derivative.id}: {e}")
            
            logger.info(f"✅ Derivative pricing update completed: {pricing_updates} derivatives updated")
            
        except Exception as e:
            logger.error(f"❌ Derivative pricing update task failed: {e}")
    
    async def system_metrics_task(self):
        """Collect and log system metrics"""
        
        try:
            # Collect basic system metrics
            async with get_db_session() as db:
                from sqlalchemy import text
                
                # Database metrics
                db_result = await db.execute(text("SELECT 1"))
                db_healthy = db_result.scalar() == 1
                
                # Get record counts
                from aetherflow.models.vehicle_data import VehicleData
                from aetherflow.models.ai_agents import AIAgent
                from aetherflow.models.traffic_lights import TrafficLight
                from sqlalchemy import select, func
                
                vehicle_count = await db.execute(select(func.count(VehicleData.id)))
                agent_count = await db.execute(select(func.count(AIAgent.agent_id)))
                traffic_count = await db.execute(select(func.count(TrafficLight.intersection_id)))
                
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "database_healthy": db_healthy,
                    "vehicle_data_count": vehicle_count.scalar(),
                    "active_agents": agent_count.scalar(),
                    "traffic_lights": traffic_count.scalar()
                }
                
                logger.debug(f"System metrics: {json.dumps(metrics)}")
            
        except Exception as e:
            logger.error(f"❌ System metrics collection failed: {e}")
    
    async def hedera_sync_task(self):
        """Sync with Hedera network"""
        
        try:
            logger.info("🌐 Running Hedera sync task...")
            
            # This would sync with actual Hedera network
            # For now, we'll simulate the sync
            
            # Check account balance
            # Submit pending HCS messages
            # Update token balances
            # Process HTS transactions
            
            logger.info("✅ Hedera sync completed")
            
        except Exception as e:
            logger.error(f"❌ Hedera sync task failed: {e}")
    
    async def should_run_task(self, task_name: str) -> bool:
        """Check if a task should run based on its interval"""
        
        now = datetime.utcnow()
        last_run = self.last_execution[task_name]
        interval = self.task_intervals[task_name]
        
        return (now - last_run).total_seconds() >= interval
    
    async def run_task(self, task_name: str, task_func):
        """Run a task and update its last execution time"""
        
        try:
            await task_func()
            self.last_execution[task_name] = datetime.utcnow()
        except Exception as e:
            logger.error(f"Task {task_name} failed: {e}")
    
    async def run(self):
        """Main worker loop"""
        
        logger.info("🚀 Starting AetherFlow background worker...")
        self.running = True
        
        # Task mapping
        task_functions = {
            'traffic_optimization': self.traffic_optimization_task,
            'reward_distribution': self.reward_distribution_task,
            'data_cleanup': self.data_cleanup_task,
            'agent_health_check': self.agent_health_check_task,
            'nft_valuation_update': self.nft_valuation_update_task,
            'derivative_pricing': self.derivative_pricing_task,
            'system_metrics': self.system_metrics_task,
            'hedera_sync': self.hedera_sync_task
        }
        
        try:
            while self.running:
                # Check and run tasks that are due
                for task_name, task_func in task_functions.items():
                    if await self.should_run_task(task_name):
                        logger.debug(f"Running task: {task_name}")
                        await self.run_task(task_name, task_func)
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"❌ Worker main loop failed: {e}")
        finally:
            logger.info("🛑 Background worker stopped")
    
    async def stop(self):
        """Stop the worker gracefully"""
        
        logger.info("Stopping background worker...")
        self.running = False
        
        # Cancel any running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)


async def main():
    """Main function"""
    
    worker = BackgroundWorker()
    worker.setup_signal_handlers()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
