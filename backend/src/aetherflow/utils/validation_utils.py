"""
Validation Utilities for AetherFlow
"""

import re
import ipaddress
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


class ValidationUtils:
    """Utility functions for data validation"""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    HEDERA_ACCOUNT_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')
    HEX_PATTERN = re.compile(r'^[0-9a-fA-F]+$')
    UUID_PATTERN = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        
        if not email or not isinstance(email, str):
            return False
        
        return bool(ValidationUtils.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_hedera_account_id(account_id: str) -> bool:
        """Validate Hedera account ID format (e.g., 0.0.123456)"""
        
        if not account_id or not isinstance(account_id, str):
            return False
        
        return bool(ValidationUtils.HEDERA_ACCOUNT_PATTERN.match(account_id))
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate geographic coordinates"""
        
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_speed(speed: float, max_speed: float = 300.0) -> bool:
        """Validate vehicle speed (km/h)"""
        
        try:
            speed_val = float(speed)
            return 0.0 <= speed_val <= max_speed
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_heading(heading: float) -> bool:
        """Validate compass heading (0-360 degrees)"""
        
        try:
            heading_val = float(heading)
            return 0.0 <= heading_val <= 360.0
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_altitude(altitude: float, min_alt: float = -500.0, max_alt: float = 10000.0) -> bool:
        """Validate altitude in meters"""
        
        try:
            alt_val = float(altitude)
            return min_alt <= alt_val <= max_alt
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_timestamp(timestamp: Union[str, datetime], max_age_hours: int = 24) -> bool:
        """Validate timestamp and check if it's not too old"""
        
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                dt = timestamp
            else:
                return False
            
            # Check if timestamp is not in the future
            if dt > datetime.utcnow():
                return False
            
            # Check if timestamp is not too old
            max_age = timedelta(hours=max_age_hours)
            if datetime.utcnow() - dt > max_age:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_hash(hash_value: str, expected_length: int = 64) -> bool:
        """Validate hash format (hex string of expected length)"""
        
        if not hash_value or not isinstance(hash_value, str):
            return False
        
        if len(hash_value) != expected_length:
            return False
        
        return bool(ValidationUtils.HEX_PATTERN.match(hash_value))
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """Validate UUID format"""
        
        if not uuid_str or not isinstance(uuid_str, str):
            return False
        
        return bool(ValidationUtils.UUID_PATTERN.match(uuid_str))
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IP address (IPv4 or IPv6)"""
        
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_port(port: Union[int, str]) -> bool:
        """Validate network port number"""
        
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_decimal_amount(amount: Union[str, float, Decimal], min_value: float = 0.0) -> bool:
        """Validate decimal amount (for token amounts)"""
        
        try:
            if isinstance(amount, str):
                decimal_amount = Decimal(amount)
            elif isinstance(amount, (int, float)):
                decimal_amount = Decimal(str(amount))
            elif isinstance(amount, Decimal):
                decimal_amount = amount
            else:
                return False
            
            return decimal_amount >= Decimal(str(min_value))
            
        except (InvalidOperation, TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_json_structure(data: Any, required_fields: List[str]) -> bool:
        """Validate JSON structure has required fields"""
        
        if not isinstance(data, dict):
            return False
        
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_string_length(
        value: str,
        min_length: int = 0,
        max_length: int = 1000
    ) -> bool:
        """Validate string length"""
        
        if not isinstance(value, str):
            return False
        
        return min_length <= len(value) <= max_length
    
    @staticmethod
    def validate_list_length(
        value: List[Any],
        min_length: int = 0,
        max_length: int = 100
    ) -> bool:
        """Validate list length"""
        
        if not isinstance(value, list):
            return False
        
        return min_length <= len(value) <= max_length
    
    @staticmethod
    def validate_enum_value(value: str, allowed_values: List[str]) -> bool:
        """Validate value is in allowed enum values"""
        
        return value in allowed_values
    
    @staticmethod
    def validate_vehicle_id(vehicle_id: str) -> bool:
        """Validate vehicle ID format"""
        
        if not vehicle_id or not isinstance(vehicle_id, str):
            return False
        
        # Vehicle ID should be alphanumeric, 6-50 characters
        if not re.match(r'^[a-zA-Z0-9_-]{6,50}$', vehicle_id):
            return False
        
        return True
    
    @staticmethod
    def validate_intersection_id(intersection_id: str) -> bool:
        """Validate intersection ID format"""
        
        if not intersection_id or not isinstance(intersection_id, str):
            return False
        
        # Intersection ID should be alphanumeric with optional separators
        if not re.match(r'^[a-zA-Z0-9_.-]{3,50}$', intersection_id):
            return False
        
        return True
    
    @staticmethod
    def validate_agent_name(agent_name: str) -> bool:
        """Validate AI agent name format"""
        
        if not agent_name or not isinstance(agent_name, str):
            return False
        
        # Agent name should be alphanumeric with spaces, 3-100 characters
        if not re.match(r'^[a-zA-Z0-9 _.-]{3,100}$', agent_name):
            return False
        
        return True
    
    @staticmethod
    def validate_capabilities(capabilities: List[str]) -> bool:
        """Validate agent capabilities list"""
        
        if not isinstance(capabilities, list):
            return False
        
        if len(capabilities) == 0 or len(capabilities) > 20:
            return False
        
        # Each capability should be a valid string
        for capability in capabilities:
            if not isinstance(capability, str) or len(capability) < 2 or len(capability) > 50:
                return False
        
        return True
    
    @staticmethod
    def validate_performance_metrics(metrics: Dict[str, Any]) -> bool:
        """Validate performance metrics structure"""
        
        if not isinstance(metrics, dict):
            return False
        
        # Check for common metric fields and their types
        numeric_fields = ['success_rate', 'response_time', 'accuracy', 'uptime']
        
        for field in numeric_fields:
            if field in metrics:
                try:
                    value = float(metrics[field])
                    if field in ['success_rate', 'accuracy', 'uptime']:
                        # These should be between 0 and 1
                        if not 0.0 <= value <= 1.0:
                            return False
                    elif field == 'response_time':
                        # Response time should be positive
                        if value < 0:
                            return False
                except (TypeError, ValueError):
                    return False
        
        return True
    
    @staticmethod
    def validate_pricing_model(pricing: Dict[str, Any]) -> bool:
        """Validate pricing model structure"""
        
        if not isinstance(pricing, dict):
            return False
        
        # Check for valid pricing fields
        if 'type' in pricing:
            valid_types = ['fixed', 'per_request', 'subscription', 'auction']
            if pricing['type'] not in valid_types:
                return False
        
        if 'amount' in pricing:
            if not ValidationUtils.validate_decimal_amount(pricing['amount']):
                return False
        
        return True
    
    @staticmethod
    def validate_zk_proof_structure(proof: Dict[str, Any]) -> bool:
        """Validate zero-knowledge proof structure"""
        
        if not isinstance(proof, dict):
            return False
        
        required_fields = ['proof', 'public_inputs', 'verification_key']
        
        if not all(field in proof for field in required_fields):
            return False
        
        # Validate proof components
        if not isinstance(proof['proof'], dict):
            return False
        
        if not isinstance(proof['public_inputs'], dict):
            return False
        
        if not isinstance(proof['verification_key'], dict):
            return False
        
        return True
    
    @staticmethod
    def validate_area_bounds(bounds: Dict[str, float]) -> bool:
        """Validate geographic area bounds"""
        
        required_fields = ['min_lat', 'max_lat', 'min_lon', 'max_lon']
        
        if not ValidationUtils.validate_json_structure(bounds, required_fields):
            return False
        
        try:
            min_lat = float(bounds['min_lat'])
            max_lat = float(bounds['max_lat'])
            min_lon = float(bounds['min_lon'])
            max_lon = float(bounds['max_lon'])
            
            # Validate coordinate ranges
            if not (-90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
                return False
            
            if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0):
                return False
            
            # Validate bounds logic
            if min_lat >= max_lat or min_lon >= max_lon:
                return False
            
            return True
            
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        
        if not isinstance(value, str):
            return ""
        
        # Remove control characters and limit length
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        return sanitized[:max_length]
    
    @staticmethod
    def validate_batch_size(size: int, max_size: int = 1000) -> bool:
        """Validate batch processing size"""
        
        try:
            size_val = int(size)
            return 1 <= size_val <= max_size
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_pagination_params(limit: int, offset: int) -> bool:
        """Validate pagination parameters"""
        
        try:
            limit_val = int(limit)
            offset_val = int(offset)
            
            return 1 <= limit_val <= 1000 and offset_val >= 0
        except (TypeError, ValueError):
            return False
