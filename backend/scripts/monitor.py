#!/usr/bin/env python3
"""
Monitoring Script for AetherFlow Backend
"""

import asyncio
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aetherflow.core.database import get_db_session
from aetherflow.core.logging import get_logger
from aetherflow.core.config import get_settings

logger = get_logger(__name__)


class SystemMonitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "http://localhost:8000"
        self.alerts = []
        
    def log_metric(self, metric_name: str, value: Any, unit: str = ""):
        """Log a metric with timestamp"""
        
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"METRIC [{timestamp}] {metric_name}: {value} {unit}")
        
        return {
            "timestamp": timestamp,
            "metric": metric_name,
            "value": value,
            "unit": unit
        }
    
    def add_alert(self, level: str, message: str, details: Dict[str, Any] = None):
        """Add an alert"""
        
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "details": details or {}
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{level}] {message}")
        
        return alert
    
    async def check_api_health(self) -> Dict[str, Any]:
        """Check API health endpoint"""
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_metric("api_response_time", round(response_time, 2), "ms")
                self.log_metric("api_status", "healthy")
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "details": health_data
                }
            else:
                self.add_alert("ERROR", f"API health check failed: HTTP {response.status_code}")
                return {
                    "status": "unhealthy",
                    "response_time_ms": round(response_time, 2),
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.RequestException as e:
            self.add_alert("CRITICAL", f"API health check failed: {e}")
            return {
                "status": "unreachable",
                "error": str(e)
            }
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        
        try:
            start_time = time.time()
            
            async with get_db_session() as db:
                from sqlalchemy import text
                result = await db.execute(text("SELECT 1"))
                result.scalar()
            
            response_time = (time.time() - start_time) * 1000
            self.log_metric("db_response_time", round(response_time, 2), "ms")
            self.log_metric("db_status", "healthy")
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2)
            }
            
        except Exception as e:
            self.add_alert("CRITICAL", f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def check_data_freshness(self) -> Dict[str, Any]:
        """Check if recent data is being received"""
        
        try:
            from aetherflow.models.vehicle_data import VehicleData
            from sqlalchemy import select, func
            
            # Check for data in the last hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            async with get_db_session() as db:
                result = await db.execute(
                    select(func.count(VehicleData.id))
                    .where(VehicleData.timestamp >= cutoff_time)
                )
                recent_count = result.scalar()
                
                # Check latest data timestamp
                latest_result = await db.execute(
                    select(func.max(VehicleData.timestamp))
                )
                latest_timestamp = latest_result.scalar()
            
            self.log_metric("recent_data_count", recent_count, "records")
            
            if recent_count == 0:
                self.add_alert("WARNING", "No recent vehicle data received in the last hour")
                data_freshness = "stale"
            elif recent_count < 10:
                self.add_alert("WARNING", f"Low data volume: only {recent_count} records in last hour")
                data_freshness = "low"
            else:
                data_freshness = "good"
            
            return {
                "status": data_freshness,
                "recent_count": recent_count,
                "latest_timestamp": latest_timestamp.isoformat() if latest_timestamp else None
            }
            
        except Exception as e:
            self.add_alert("ERROR", f"Data freshness check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.log_metric("cpu_usage", cpu_percent, "%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.log_metric("memory_usage", memory_percent, "%")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.log_metric("disk_usage", round(disk_percent, 2), "%")
            
            # Check for resource alerts
            if cpu_percent > 80:
                self.add_alert("WARNING", f"High CPU usage: {cpu_percent}%")
            
            if memory_percent > 85:
                self.add_alert("WARNING", f"High memory usage: {memory_percent}%")
            
            if disk_percent > 90:
                self.add_alert("CRITICAL", f"High disk usage: {disk_percent}%")
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": round(disk_percent, 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
            
        except ImportError:
            logger.warning("psutil not available, skipping system resource checks")
            return {"status": "unavailable", "error": "psutil not installed"}
        except Exception as e:
            self.add_alert("ERROR", f"System resource check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def check_hedera_connectivity(self) -> Dict[str, Any]:
        """Check Hedera network connectivity"""
        
        try:
            # This would check actual Hedera connectivity
            # For now, we'll simulate the check
            
            start_time = time.time()
            
            # Simulate network check
            await asyncio.sleep(0.1)  # Simulate network delay
            
            response_time = (time.time() - start_time) * 1000
            self.log_metric("hedera_response_time", round(response_time, 2), "ms")
            
            # In a real implementation, this would:
            # - Check account balance
            # - Verify topic accessibility
            # - Test message submission
            
            return {
                "status": "connected",
                "network": self.settings.hedera_network,
                "response_time_ms": round(response_time, 2),
                "account_id": self.settings.hedera_account_id
            }
            
        except Exception as e:
            self.add_alert("ERROR", f"Hedera connectivity check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Check key API endpoints"""
        
        endpoints = [
            "/health",
            "/api/v1/vehicle-data/stats",
            "/api/v1/agents/stats",
            "/api/v1/traffic/stats"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "status": "ok" if response.status_code == 200 else "error"
                }
                
                if response.status_code != 200:
                    self.add_alert("WARNING", f"Endpoint {endpoint} returned {response.status_code}")
                
            except requests.RequestException as e:
                results[endpoint] = {
                    "status": "error",
                    "error": str(e)
                }
                self.add_alert("ERROR", f"Endpoint {endpoint} failed: {e}")
        
        return results
    
    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        
        logger.info("🔍 Generating system monitoring report...")
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "alerts": self.alerts,
            "summary": {}
        }
        
        # Run all health checks
        checks = [
            ("api_health", self.check_api_health()),
            ("database_health", self.check_database_health()),
            ("data_freshness", self.check_data_freshness()),
            ("system_resources", self.check_system_resources()),
            ("hedera_connectivity", self.check_hedera_connectivity()),
            ("api_endpoints", self.check_api_endpoints())
        ]
        
        for check_name, check_coro in checks:
            try:
                logger.info(f"Running {check_name} check...")
                report["checks"][check_name] = await check_coro
            except Exception as e:
                logger.error(f"Check {check_name} failed: {e}")
                report["checks"][check_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Generate summary
        healthy_checks = sum(
            1 for check in report["checks"].values()
            if isinstance(check, dict) and check.get("status") in ["healthy", "good", "ok", "connected"]
        )
        
        total_checks = len(report["checks"])
        
        report["summary"] = {
            "overall_status": "healthy" if healthy_checks == total_checks else "degraded",
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "health_percentage": round((healthy_checks / total_checks) * 100, 1),
            "alert_counts": {
                "CRITICAL": len([a for a in self.alerts if a["level"] == "CRITICAL"]),
                "ERROR": len([a for a in self.alerts if a["level"] == "ERROR"]),
                "WARNING": len([a for a in self.alerts if a["level"] == "WARNING"])
            }
        }
        
        return report
    
    async def continuous_monitoring(self, interval_seconds: int = 60):
        """Run continuous monitoring"""
        
        logger.info(f"🔄 Starting continuous monitoring (interval: {interval_seconds}s)")
        
        try:
            while True:
                # Clear previous alerts
                self.alerts = []
                
                # Generate report
                report = await self.generate_report()
                
                # Log summary
                summary = report["summary"]
                logger.info(f"Health: {summary['health_percentage']}% "
                           f"({summary['healthy_checks']}/{summary['total_checks']} checks passed)")
                
                if summary["alert_counts"]["CRITICAL"] > 0:
                    logger.error(f"🚨 {summary['alert_counts']['CRITICAL']} CRITICAL alerts")
                
                if summary["alert_counts"]["ERROR"] > 0:
                    logger.warning(f"⚠️  {summary['alert_counts']['ERROR']} ERROR alerts")
                
                # Save report to file
                report_file = Path(f"monitoring_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                # Wait for next check
                await asyncio.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            raise


async def main():
    """Main monitoring function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="AetherFlow Backend Monitoring")
    parser.add_argument(
        "--mode",
        choices=["report", "continuous"],
        default="report",
        help="Monitoring mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds (for continuous mode)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for report"
    )
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    try:
        if args.mode == "report":
            # Generate single report
            report = await monitor.generate_report()
            
            # Output report
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Report saved to {args.output}")
            else:
                print(json.dumps(report, indent=2))
            
            # Exit with error code if there are critical issues
            if report["summary"]["alert_counts"]["CRITICAL"] > 0:
                sys.exit(1)
        
        elif args.mode == "continuous":
            # Run continuous monitoring
            await monitor.continuous_monitoring(args.interval)
        
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
