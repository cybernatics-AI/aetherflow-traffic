"""
Hedera Client for AetherFlow Backend
"""

import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from hedera import (
        Client, 
        AccountId, 
        PrivateKey,
        TopicCreateTransaction,
        TopicMessageSubmitTransaction,
        TopicInfoQuery,
        AccountBalanceQuery,
        TransferTransaction,
        Hbar,
        Status
    )
except ImportError:
    # Fallback for development without Hedera SDK
    logging.warning("Hedera SDK not available. Using mock client.")
    Client = None
    AccountId = None
    PrivateKey = None

from aetherflow.core.logging import get_logger

logger = get_logger(__name__)


class HederaClient:
    """Hedera network client for HCS and HTS operations"""
    
    def __init__(self, account_id: str, private_key: str, network: str = "testnet"):
        """Initialize Hedera client"""
        self.account_id_str = account_id
        self.private_key_str = private_key
        self.network = network
        
        if Client is None:
            logger.warning("Hedera SDK not available. Using mock mode.")
            self.client = None
            self.account_id = None
            self.private_key = None
            return
        
        try:
            # Initialize client based on network
            if network == "mainnet":
                self.client = Client.forMainnet()
            elif network == "testnet":
                self.client = Client.forTestnet()
            else:
                self.client = Client.forPreviewnet()
            
            # Set operator
            self.account_id = AccountId.fromString(account_id)
            self.private_key = PrivateKey.fromString(private_key)
            self.client.setOperator(self.account_id, self.private_key)
            
            logger.info(f"Hedera client initialized for {network} with account {account_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hedera client: {e}")
            raise
    
    async def create_topic(self, memo: Optional[str] = None, admin_key: bool = True) -> Optional[str]:
        """Create a new HCS topic"""
        if not self.client:
            logger.warning("Mock mode: Returning mock topic ID")
            return "0.0.999999"
        
        try:
            transaction = TopicCreateTransaction()
            
            if memo:
                transaction.setTopicMemo(memo)
            
            if admin_key:
                transaction.setAdminKey(self.private_key.getPublicKey())
                transaction.setSubmitKey(self.private_key.getPublicKey())
            
            # Execute transaction
            tx_response = await transaction.execute(self.client)
            receipt = await tx_response.getReceipt(self.client)
            
            topic_id = receipt.topicId
            logger.info(f"Created HCS topic: {topic_id}")
            
            return str(topic_id)
            
        except Exception as e:
            logger.error(f"Failed to create HCS topic: {e}")
            return None
    
    async def submit_message(self, topic_id: str, message: Dict[str, Any], memo: Optional[str] = None) -> Optional[str]:
        """Submit message to HCS topic"""
        if not self.client:
            logger.warning("Mock mode: Returning mock transaction ID")
            return "0.0.123456@1234567890.123456789"
        
        try:
            # Convert message to JSON string
            message_json = json.dumps(message)
            
            transaction = TopicMessageSubmitTransaction()
            transaction.setTopicId(topic_id)
            transaction.setMessage(message_json)
            
            if memo:
                transaction.setTransactionMemo(memo)
            
            # Execute transaction
            tx_response = await transaction.execute(self.client)
            receipt = await tx_response.getReceipt(self.client)
            
            if receipt.status == Status.Success:
                tx_id = str(tx_response.transactionId)
                logger.info(f"Message submitted to topic {topic_id}: {tx_id}")
                return tx_id
            else:
                logger.error(f"Failed to submit message: {receipt.status}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to submit message to topic {topic_id}: {e}")
            return None
    
    async def get_account_balance(self, account_id: Optional[str] = None) -> Optional[float]:
        """Get account HBAR balance"""
        if not self.client:
            logger.warning("Mock mode: Returning mock balance")
            return 100.0
        
        try:
            target_account = AccountId.fromString(account_id) if account_id else self.account_id
            
            query = AccountBalanceQuery()
            query.setAccountId(target_account)
            
            balance = await query.execute(self.client)
            hbar_balance = balance.hbars.toTinybars() / 100_000_000  # Convert to HBAR
            
            logger.info(f"Account {target_account} balance: {hbar_balance} HBAR")
            return hbar_balance
            
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return None
    
    async def transfer_hbar(self, to_account: str, amount: float, memo: Optional[str] = None) -> Optional[str]:
        """Transfer HBAR to another account"""
        if not self.client:
            logger.warning("Mock mode: Returning mock transaction ID")
            return "0.0.123456@1234567890.123456789"
        
        try:
            to_account_id = AccountId.fromString(to_account)
            hbar_amount = Hbar.fromTinybars(int(amount * 100_000_000))
            
            transaction = TransferTransaction()
            transaction.addHbarTransfer(self.account_id, hbar_amount.negated())
            transaction.addHbarTransfer(to_account_id, hbar_amount)
            
            if memo:
                transaction.setTransactionMemo(memo)
            
            # Execute transaction
            tx_response = await transaction.execute(self.client)
            receipt = await tx_response.getReceipt(self.client)
            
            if receipt.status == Status.Success:
                tx_id = str(tx_response.transactionId)
                logger.info(f"Transferred {amount} HBAR to {to_account}: {tx_id}")
                return tx_id
            else:
                logger.error(f"Failed to transfer HBAR: {receipt.status}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to transfer HBAR: {e}")
            return None
    
    async def get_topic_info(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """Get HCS topic information"""
        if not self.client:
            logger.warning("Mock mode: Returning mock topic info")
            return {
                "topic_id": topic_id,
                "memo": "Mock topic",
                "running_hash": "mock_hash",
                "sequence_number": 1
            }
        
        try:
            query = TopicInfoQuery()
            query.setTopicId(topic_id)
            
            topic_info = await query.execute(self.client)
            
            return {
                "topic_id": str(topic_info.topicId),
                "memo": topic_info.topicMemo,
                "running_hash": topic_info.runningHash.hex() if topic_info.runningHash else None,
                "sequence_number": topic_info.sequenceNumber,
                "expiration_time": topic_info.expirationTime.isoformat() if topic_info.expirationTime else None,
                "admin_key": str(topic_info.adminKey) if topic_info.adminKey else None,
                "submit_key": str(topic_info.submitKey) if topic_info.submitKey else None,
                "auto_renew_period": topic_info.autoRenewPeriod.seconds if topic_info.autoRenewPeriod else None,
                "auto_renew_account": str(topic_info.autoRenewAccountId) if topic_info.autoRenewAccountId else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get topic info for {topic_id}: {e}")
            return None
    
    def close(self):
        """Close Hedera client connection"""
        if self.client:
            self.client.close()
            logger.info("Hedera client connection closed")
