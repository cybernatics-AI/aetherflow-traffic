"""
Cryptographic Utilities for AetherFlow
"""

import hashlib
import hmac
import secrets
import base64
import json
from typing import Dict, Any, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


class CryptoUtils:
    """Cryptographic utilities for data encryption, hashing, and ZK-proofs"""
    
    @staticmethod
    def generate_secure_hash(data: str, algorithm: str = "sha256") -> str:
        """Generate secure hash of data"""
        
        if algorithm == "sha256":
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data.encode()).hexdigest()
        elif algorithm == "blake2b":
            return hashlib.blake2b(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def generate_hmac(data: str, key: str, algorithm: str = "sha256") -> str:
        """Generate HMAC for data integrity"""
        
        key_bytes = key.encode()
        data_bytes = data.encode()
        
        if algorithm == "sha256":
            return hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()
        elif algorithm == "sha512":
            return hmac.new(key_bytes, data_bytes, hashlib.sha512).hexdigest()
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {algorithm}")
    
    @staticmethod
    def verify_hmac(data: str, key: str, expected_hmac: str, algorithm: str = "sha256") -> bool:
        """Verify HMAC for data integrity"""
        
        calculated_hmac = CryptoUtils.generate_hmac(data, key, algorithm)
        return hmac.compare_digest(calculated_hmac, expected_hmac)
    
    @staticmethod
    def generate_encryption_key() -> str:
        """Generate a new encryption key"""
        
        return Fernet.generate_key().decode()
    
    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """Encrypt data using Fernet symmetric encryption"""
        
        try:
            fernet = Fernet(key.encode())
            encrypted_data = fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """Decrypt data using Fernet symmetric encryption"""
        
        try:
            fernet = Fernet(key.encode())
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> Tuple[str, str]:
        """Generate RSA public/private key pair"""
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        
        return public_pem, private_pem
    
    @staticmethod
    def rsa_encrypt(data: str, public_key_pem: str) -> str:
        """Encrypt data using RSA public key"""
        
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            
            encrypted_data = public_key.encrypt(
                data.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"RSA encryption failed: {e}")
            raise
    
    @staticmethod
    def rsa_decrypt(encrypted_data: str, private_key_pem: str) -> str:
        """Decrypt data using RSA private key"""
        
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            decrypted_data = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"RSA decryption failed: {e}")
            raise
    
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        """Generate cryptographic salt"""
        
        return base64.b64encode(secrets.token_bytes(length)).decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: str, iterations: int = 100000) -> str:
        """Derive encryption key from password using PBKDF2"""
        
        salt_bytes = base64.b64decode(salt.encode())
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=iterations
        )
        
        key = kdf.derive(password.encode())
        return base64.b64encode(key).decode()
    
    @staticmethod
    def generate_zk_proof_mock(
        data: Dict[str, Any],
        private_inputs: Dict[str, Any],
        public_inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate mock zero-knowledge proof (placeholder implementation)"""
        
        # This is a mock implementation for development
        # In production, this would use actual ZK-proof libraries like libsnark, circom, etc.
        
        logger.info("Generating mock ZK-proof")
        
        # Create deterministic proof based on inputs
        proof_data = {
            "data_hash": CryptoUtils.generate_secure_hash(json.dumps(data, sort_keys=True)),
            "private_hash": CryptoUtils.generate_secure_hash(json.dumps(private_inputs, sort_keys=True)),
            "public_hash": CryptoUtils.generate_secure_hash(json.dumps(public_inputs, sort_keys=True))
        }
        
        # Generate mock proof components
        proof = {
            "proof": {
                "a": CryptoUtils.generate_secure_hash(proof_data["data_hash"] + "a"),
                "b": CryptoUtils.generate_secure_hash(proof_data["data_hash"] + "b"),
                "c": CryptoUtils.generate_secure_hash(proof_data["data_hash"] + "c")
            },
            "public_inputs": public_inputs,
            "verification_key": {
                "alpha": CryptoUtils.generate_secure_hash(proof_data["public_hash"] + "alpha"),
                "beta": CryptoUtils.generate_secure_hash(proof_data["public_hash"] + "beta"),
                "gamma": CryptoUtils.generate_secure_hash(proof_data["public_hash"] + "gamma")
            },
            "verified": True,  # Mock verification result
            "timestamp": secrets.token_hex(16),
            "circuit_id": "vehicle_data_privacy_v1"
        }
        
        return proof
    
    @staticmethod
    def verify_zk_proof_mock(
        proof: Dict[str, Any],
        public_inputs: Dict[str, Any]
    ) -> bool:
        """Verify mock zero-knowledge proof"""
        
        # Mock verification logic
        # In production, this would use actual ZK-proof verification
        
        logger.info("Verifying mock ZK-proof")
        
        try:
            # Basic structure validation
            required_fields = ["proof", "public_inputs", "verification_key"]
            if not all(field in proof for field in required_fields):
                return False
            
            # Check if public inputs match
            if proof["public_inputs"] != public_inputs:
                return False
            
            # Mock verification (always returns True for valid structure)
            return proof.get("verified", False)
            
        except Exception as e:
            logger.error(f"ZK-proof verification failed: {e}")
            return False
    
    @staticmethod
    def generate_commitment(value: str, nonce: str) -> str:
        """Generate cryptographic commitment"""
        
        commitment_data = f"{value}:{nonce}"
        return CryptoUtils.generate_secure_hash(commitment_data)
    
    @staticmethod
    def verify_commitment(value: str, nonce: str, commitment: str) -> bool:
        """Verify cryptographic commitment"""
        
        expected_commitment = CryptoUtils.generate_commitment(value, nonce)
        return hmac.compare_digest(expected_commitment, commitment)
    
    @staticmethod
    def generate_merkle_root(data_hashes: list) -> str:
        """Generate Merkle root from list of data hashes"""
        
        if not data_hashes:
            return ""
        
        if len(data_hashes) == 1:
            return data_hashes[0]
        
        # Build Merkle tree
        current_level = data_hashes[:]
        
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    # Hash pair
                    combined = current_level[i] + current_level[i + 1]
                    next_level.append(CryptoUtils.generate_secure_hash(combined))
                else:
                    # Odd number, duplicate last hash
                    combined = current_level[i] + current_level[i]
                    next_level.append(CryptoUtils.generate_secure_hash(combined))
            
            current_level = next_level
        
        return current_level[0]
    
    @staticmethod
    def generate_digital_signature_mock(data: str, private_key: str) -> str:
        """Generate mock digital signature"""
        
        # Mock signature using HMAC
        signature_data = f"{data}:{private_key}"
        return CryptoUtils.generate_secure_hash(signature_data)
    
    @staticmethod
    def verify_digital_signature_mock(
        data: str,
        signature: str,
        public_key: str
    ) -> bool:
        """Verify mock digital signature"""
        
        # In a real implementation, this would use actual digital signature verification
        # For now, we'll use a simple hash-based verification
        
        try:
            # Mock verification logic
            expected_signature = CryptoUtils.generate_secure_hash(f"{data}:{public_key}")
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def secure_random_string(length: int = 32) -> str:
        """Generate cryptographically secure random string"""
        
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def secure_random_hex(length: int = 32) -> str:
        """Generate cryptographically secure random hex string"""
        
        return secrets.token_hex(length)
    
    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """Constant-time string comparison to prevent timing attacks"""
        
        return hmac.compare_digest(a, b)
