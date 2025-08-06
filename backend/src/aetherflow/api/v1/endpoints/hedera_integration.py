"""
Hedera Integration API Endpoints
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from aetherflow.core.database import get_async_session
from aetherflow.hedera.client import HederaClient
from aetherflow.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class TopicCreateRequest(BaseModel):
    """Topic creation request schema"""
    memo: Optional[str] = Field(None, description="Topic memo")
    admin_key: bool = Field(True, description="Set admin key")


class MessageSubmitRequest(BaseModel):
    """Message submission request schema"""
    topic_id: str = Field(..., description="HCS topic ID")
    message: Dict[str, Any] = Field(..., description="Message content")
    memo: Optional[str] = Field(None, description="Transaction memo")


class TransferRequest(BaseModel):
    """HBAR transfer request schema"""
    to_account: str = Field(..., description="Recipient account ID")
    amount: float = Field(..., gt=0, description="Amount in HBAR")
    memo: Optional[str] = Field(None, description="Transfer memo")


@router.post("/topics/create")
async def create_topic(
    request: TopicCreateRequest,
    req: Request
):
    """Create a new HCS topic"""
    try:
        hedera_client: HederaClient = req.app.state.hedera_client
        
        topic_id = await hedera_client.create_topic(
            memo=request.memo,
            admin_key=request.admin_key
        )
        
        if topic_id:
            logger.info(f"Created HCS topic: {topic_id}")
            return {
                "status": "success",
                "topic_id": topic_id,
                "memo": request.memo,
                "message": "Topic created successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create topic"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create topic: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create topic"
        )


@router.post("/topics/submit-message")
async def submit_message(
    request: MessageSubmitRequest,
    req: Request
):
    """Submit message to HCS topic"""
    try:
        hedera_client: HederaClient = req.app.state.hedera_client
        
        tx_id = await hedera_client.submit_message(
            topic_id=request.topic_id,
            message=request.message,
            memo=request.memo
        )
        
        if tx_id:
            logger.info(f"Message submitted to topic {request.topic_id}: {tx_id}")
            return {
                "status": "success",
                "transaction_id": tx_id,
                "topic_id": request.topic_id,
                "message": "Message submitted successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit message"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit message"
        )


@router.get("/topics/{topic_id}/info")
async def get_topic_info(
    topic_id: str,
    req: Request
):
    """Get HCS topic information"""
    try:
        hedera_client: HederaClient = req.app.state.hedera_client
        
        topic_info = await hedera_client.get_topic_info(topic_id)
        
        if topic_info:
            return {
                "status": "success",
                "topic_info": topic_info,
                "message": "Topic information retrieved successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topic not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get topic info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve topic information"
        )


@router.get("/account/balance")
async def get_account_balance(
    account_id: Optional[str] = None,
    req: Request = None
):
    """Get account HBAR balance"""
    try:
        hedera_client: HederaClient = req.app.state.hedera_client
        
        balance = await hedera_client.get_account_balance(account_id)
        
        if balance is not None:
            return {
                "status": "success",
                "account_id": account_id or hedera_client.account_id_str,
                "balance": balance,
                "currency": "HBAR",
                "message": "Balance retrieved successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve balance"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account balance"
        )


@router.post("/transfer")
async def transfer_hbar(
    request: TransferRequest,
    req: Request
):
    """Transfer HBAR to another account"""
    try:
        hedera_client: HederaClient = req.app.state.hedera_client
        
        tx_id = await hedera_client.transfer_hbar(
            to_account=request.to_account,
            amount=request.amount,
            memo=request.memo
        )
        
        if tx_id:
            logger.info(f"Transferred {request.amount} HBAR to {request.to_account}: {tx_id}")
            return {
                "status": "success",
                "transaction_id": tx_id,
                "to_account": request.to_account,
                "amount": request.amount,
                "memo": request.memo,
                "message": "Transfer completed successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to transfer HBAR"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to transfer HBAR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer HBAR"
        )


@router.get("/network/status")
async def get_network_status(req: Request):
    """Get Hedera network status"""
    try:
        hedera_client: HederaClient = req.app.state.hedera_client
        
        # Get basic network information
        network_info = {
            "network": hedera_client.network,
            "account_id": hedera_client.account_id_str,
            "status": "connected" if hedera_client.client else "mock_mode",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Try to get account balance as a connectivity test
        try:
            balance = await hedera_client.get_account_balance()
            network_info["balance"] = balance
            network_info["connectivity"] = "healthy"
        except Exception:
            network_info["connectivity"] = "limited"
        
        return {
            "status": "success",
            "network_info": network_info,
            "message": "Network status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get network status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve network status"
        )
