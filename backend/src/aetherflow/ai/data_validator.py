"""
Data Validator for AetherFlow - ZK-Proof and Quality Validation
"""

import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

from aetherflow.core.logging import get_logger
from aetherflow.models.vehicle_data import VehicleData

logger = get_logger(__name__)


class DataValidator:
    """Validates vehicle data using ZK-proofs and quality metrics"""
    
    def __init__(self):
        self.validation_history: List[Dict[str, Any]] = []
        self.quality_thresholds = {
            "min_speed": 0.0,
            "max_speed": 200.0,  # km/h
            "min_latitude": -90.0,
            "max_latitude": 90.0,
            "min_longitude": -180.0,
            "max_longitude": 180.0,
            "max_acceleration": 10.0,  # m/s²
            "min_data_freshness_minutes": 60
        }
        
    async def validate_vehicle_data(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Comprehensive validation of vehicle data"""
        
        validation_result = {
            "data_id": vehicle_data.id,
            "vehicle_id": vehicle_data.vehicle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "validations": {},
            "overall_score": 0.0,
            "is_valid": False,
            "issues": []
        }
        
        # Basic data validation
        basic_validation = self._validate_basic_data(vehicle_data)
        validation_result["validations"]["basic"] = basic_validation
        
        # Geospatial validation
        geo_validation = self._validate_geospatial_data(vehicle_data)
        validation_result["validations"]["geospatial"] = geo_validation
        
        # Temporal validation
        temporal_validation = self._validate_temporal_data(vehicle_data)
        validation_result["validations"]["temporal"] = temporal_validation
        
        # Physics validation
        physics_validation = self._validate_physics_constraints(vehicle_data)
        validation_result["validations"]["physics"] = physics_validation
        
        # ZK-proof validation
        zk_validation = self._validate_zk_proof(vehicle_data)
        validation_result["validations"]["zk_proof"] = zk_validation
        
        # Data hash validation
        hash_validation = self._validate_data_hash(vehicle_data)
        validation_result["validations"]["hash"] = hash_validation
        
        # Calculate overall score
        validation_scores = [
            basic_validation["score"],
            geo_validation["score"],
            temporal_validation["score"],
            physics_validation["score"],
            zk_validation["score"],
            hash_validation["score"]
        ]
        
        validation_result["overall_score"] = np.mean(validation_scores)
        validation_result["is_valid"] = validation_result["overall_score"] >= 0.7
        
        # Collect all issues
        for validation in validation_result["validations"].values():
            validation_result["issues"].extend(validation.get("issues", []))
        
        # Record validation
        self.validation_history.append(validation_result)
        
        logger.info(f"Validated vehicle data {vehicle_data.id}: "
                   f"score={validation_result['overall_score']:.2f}, "
                   f"valid={validation_result['is_valid']}")
        
        return validation_result
    
    def _validate_basic_data(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Validate basic data fields"""
        
        issues = []
        score = 1.0
        
        # Check required fields
        if not vehicle_data.vehicle_id:
            issues.append("Missing vehicle_id")
            score -= 0.3
        
        if vehicle_data.speed is None:
            issues.append("Missing speed data")
            score -= 0.3
        elif not (self.quality_thresholds["min_speed"] <= vehicle_data.speed <= self.quality_thresholds["max_speed"]):
            issues.append(f"Speed out of range: {vehicle_data.speed}")
            score -= 0.2
        
        if vehicle_data.latitude is None or vehicle_data.longitude is None:
            issues.append("Missing location data")
            score -= 0.4
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "checks_passed": len(issues) == 0
        }
    
    def _validate_geospatial_data(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Validate geospatial data"""
        
        issues = []
        score = 1.0
        
        # Validate latitude
        if vehicle_data.latitude is not None:
            if not (self.quality_thresholds["min_latitude"] <= vehicle_data.latitude <= self.quality_thresholds["max_latitude"]):
                issues.append(f"Latitude out of range: {vehicle_data.latitude}")
                score -= 0.3
        
        # Validate longitude
        if vehicle_data.longitude is not None:
            if not (self.quality_thresholds["min_longitude"] <= vehicle_data.longitude <= self.quality_thresholds["max_longitude"]):
                issues.append(f"Longitude out of range: {vehicle_data.longitude}")
                score -= 0.3
        
        # Validate heading
        if vehicle_data.heading is not None:
            if not (0 <= vehicle_data.heading <= 360):
                issues.append(f"Heading out of range: {vehicle_data.heading}")
                score -= 0.2
        
        # Check for impossible locations (e.g., middle of ocean for urban traffic)
        if vehicle_data.latitude is not None and vehicle_data.longitude is not None:
            if self._is_invalid_location(vehicle_data.latitude, vehicle_data.longitude):
                issues.append("Location appears to be in invalid area for urban traffic")
                score -= 0.2
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "checks_passed": len(issues) == 0
        }
    
    def _validate_temporal_data(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Validate temporal aspects of data"""
        
        issues = []
        score = 1.0
        
        if vehicle_data.timestamp:
            # Check data freshness
            age_minutes = (datetime.utcnow() - vehicle_data.timestamp).total_seconds() / 60
            
            if age_minutes > self.quality_thresholds["min_data_freshness_minutes"]:
                issues.append(f"Data is stale: {age_minutes:.1f} minutes old")
                score -= 0.2
            
            # Check for future timestamps
            if vehicle_data.timestamp > datetime.utcnow():
                issues.append("Timestamp is in the future")
                score -= 0.3
        else:
            issues.append("Missing timestamp")
            score -= 0.4
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "checks_passed": len(issues) == 0
        }
    
    def _validate_physics_constraints(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Validate physics constraints"""
        
        issues = []
        score = 1.0
        
        # Check for reasonable speed changes (if we have previous data)
        # This would require access to previous data points for the same vehicle
        # For now, we'll do basic physics checks
        
        # Check altitude reasonableness for urban areas
        if vehicle_data.altitude is not None:
            if vehicle_data.altitude < -100 or vehicle_data.altitude > 3000:
                issues.append(f"Altitude seems unreasonable for urban traffic: {vehicle_data.altitude}m")
                score -= 0.1
        
        # Speed vs heading consistency (if both available)
        if vehicle_data.speed is not None and vehicle_data.speed > 0:
            if vehicle_data.heading is None:
                issues.append("Moving vehicle should have heading information")
                score -= 0.1
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "checks_passed": len(issues) == 0
        }
    
    def _validate_zk_proof(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Validate zero-knowledge proof"""
        
        issues = []
        score = 1.0
        
        if vehicle_data.zk_proof is None:
            issues.append("No ZK-proof provided")
            score = 0.5  # Partial score for missing proof
        else:
            # Mock ZK-proof validation
            # In a real implementation, this would use actual ZK-proof libraries
            
            if not isinstance(vehicle_data.zk_proof, dict):
                issues.append("Invalid ZK-proof format")
                score -= 0.4
            else:
                # Check for required proof fields
                required_fields = ["proof", "public_inputs", "verification_key"]
                for field in required_fields:
                    if field not in vehicle_data.zk_proof:
                        issues.append(f"Missing ZK-proof field: {field}")
                        score -= 0.2
                
                # Mock proof verification
                if "verified" in vehicle_data.zk_proof:
                    if not vehicle_data.zk_proof["verified"]:
                        issues.append("ZK-proof verification failed")
                        score -= 0.5
                else:
                    # Simulate proof verification
                    verification_success = self._simulate_zk_verification(vehicle_data.zk_proof)
                    if not verification_success:
                        issues.append("ZK-proof verification failed")
                        score -= 0.5
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "checks_passed": len(issues) == 0
        }
    
    def _validate_data_hash(self, vehicle_data: VehicleData) -> Dict[str, Any]:
        """Validate data hash integrity"""
        
        issues = []
        score = 1.0
        
        if not vehicle_data.data_hash:
            issues.append("Missing data hash")
            score -= 0.5
        else:
            # Recalculate hash and compare
            expected_hash = self._calculate_data_hash(vehicle_data)
            
            if vehicle_data.data_hash != expected_hash:
                issues.append("Data hash mismatch - data may have been tampered with")
                score -= 0.8
            
            # Check hash format (should be 64 character hex string for SHA-256)
            if len(vehicle_data.data_hash) != 64:
                issues.append("Invalid hash format")
                score -= 0.3
            
            try:
                int(vehicle_data.data_hash, 16)  # Should be valid hex
            except ValueError:
                issues.append("Hash contains invalid characters")
                score -= 0.3
        
        return {
            "score": max(0.0, score),
            "issues": issues,
            "checks_passed": len(issues) == 0
        }
    
    def _is_invalid_location(self, latitude: float, longitude: float) -> bool:
        """Check if location is in an invalid area for urban traffic"""
        
        # Simple checks for obviously invalid locations
        # In a real implementation, this would use geospatial databases
        
        # Check if in middle of ocean (very rough approximation)
        if abs(latitude) < 5 and abs(longitude) < 5:
            return True  # Near equator/prime meridian intersection (likely ocean)
        
        # Add more sophisticated location validation as needed
        return False
    
    def _simulate_zk_verification(self, zk_proof: Dict[str, Any]) -> bool:
        """Simulate ZK-proof verification"""
        
        # Mock verification logic
        # In reality, this would use libraries like libsnark, circom, etc.
        
        if "proof" not in zk_proof:
            return False
        
        # Simulate verification with random success rate (for demo)
        # In production, this would be deterministic based on actual proof
        return np.random.random() > 0.1  # 90% success rate for demo
    
    def _calculate_data_hash(self, vehicle_data: VehicleData) -> str:
        """Calculate expected data hash"""
        
        # Create deterministic data representation for hashing
        hash_data = {
            "vehicle_id": vehicle_data.vehicle_id,
            "speed": vehicle_data.speed,
            "latitude": vehicle_data.latitude,
            "longitude": vehicle_data.longitude,
            "heading": vehicle_data.heading,
            "altitude": vehicle_data.altitude,
            "timestamp": vehicle_data.timestamp.isoformat() if vehicle_data.timestamp else None,
            "device_type": vehicle_data.device_type
        }
        
        # Convert to JSON string with sorted keys
        data_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def validate_batch(self, vehicle_data_list: List[VehicleData]) -> Dict[str, Any]:
        """Validate a batch of vehicle data"""
        
        logger.info(f"Validating batch of {len(vehicle_data_list)} vehicle data records")
        
        validation_results = []
        for vehicle_data in vehicle_data_list:
            result = await self.validate_vehicle_data(vehicle_data)
            validation_results.append(result)
        
        # Calculate batch statistics
        valid_count = sum(1 for r in validation_results if r["is_valid"])
        invalid_count = len(validation_results) - valid_count
        average_score = np.mean([r["overall_score"] for r in validation_results])
        
        # Collect all unique issues
        all_issues = []
        for result in validation_results:
            all_issues.extend(result["issues"])
        
        unique_issues = list(set(all_issues))
        
        batch_result = {
            "batch_size": len(vehicle_data_list),
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "validation_rate": valid_count / len(validation_results) if validation_results else 0,
            "average_score": average_score,
            "unique_issues": unique_issues,
            "validation_results": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Batch validation complete: {valid_count}/{len(validation_results)} valid "
                   f"(rate: {batch_result['validation_rate']:.1%})")
        
        return batch_result
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics from history"""
        
        if not self.validation_history:
            return {"message": "No validation history available"}
        
        total_validations = len(self.validation_history)
        valid_count = sum(1 for v in self.validation_history if v["is_valid"])
        
        scores = [v["overall_score"] for v in self.validation_history]
        
        # Count issue types
        issue_counts = {}
        for validation in self.validation_history:
            for issue in validation["issues"]:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return {
            "total_validations": total_validations,
            "valid_count": valid_count,
            "invalid_count": total_validations - valid_count,
            "validation_rate": valid_count / total_validations,
            "average_score": np.mean(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "common_issues": sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "last_validation": self.validation_history[-1]["timestamp"]
        }
