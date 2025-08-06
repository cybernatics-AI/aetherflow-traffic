"""
User Accounts API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from aetherflow.core.database import get_db_session
from aetherflow.core.logging import get_logger
from aetherflow.models.user_accounts import UserAccount
from aetherflow.services.tokenomics_service import TokenomicsService
from aetherflow.hedera.client import get_hedera_client

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["user-accounts"])


# Pydantic models for request/response
class UserAccountCreate(BaseModel):
    hedera_account_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    role: str = "user"
    profile_data: Optional[dict] = None


class UserAccountUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    profile_data: Optional[dict] = None
    privacy_settings: Optional[dict] = None


class UserAccountResponse(BaseModel):
    id: int
    hedera_account_id: str
    email: Optional[str]
    username: Optional[str]
    role: str
    aether_balance: Optional[float]
    total_rewards_earned: Optional[float]
    reputation_score: Optional[float]
    profile_data: Optional[dict]
    created_at: str
    last_login: Optional[str]

    class Config:
        from_attributes = True


@router.post("/", response_model=UserAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_user_account(
    user_data: UserAccountCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new user account"""
    
    try:
        # Check if user already exists
        from sqlalchemy import select
        result = await db.execute(
            select(UserAccount).where(UserAccount.hedera_account_id == user_data.hedera_account_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User account already exists"
            )
        
        # Create new user account
        user_account = UserAccount(
            hedera_account_id=user_data.hedera_account_id,
            email=user_data.email,
            username=user_data.username,
            role=user_data.role,
            profile_data=user_data.profile_data or {}
        )
        
        db.add(user_account)
        await db.commit()
        await db.refresh(user_account)
        
        logger.info(f"Created user account: {user_account.hedera_account_id}")
        
        return UserAccountResponse(
            id=user_account.id,
            hedera_account_id=user_account.hedera_account_id,
            email=user_account.email,
            username=user_account.username,
            role=user_account.role,
            aether_balance=float(user_account.aether_balance or 0),
            total_rewards_earned=float(user_account.total_rewards_earned or 0),
            reputation_score=user_account.reputation_score,
            profile_data=user_account.profile_data,
            created_at=user_account.created_at.isoformat(),
            last_login=user_account.last_login.isoformat() if user_account.last_login else None
        )
        
    except Exception as e:
        logger.error(f"Failed to create user account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )


@router.get("/{account_id}", response_model=UserAccountResponse)
async def get_user_account(
    account_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get user account by Hedera account ID"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(UserAccount).where(UserAccount.hedera_account_id == account_id)
        )
        user_account = result.scalar_one_or_none()
        
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found"
            )
        
        return UserAccountResponse(
            id=user_account.id,
            hedera_account_id=user_account.hedera_account_id,
            email=user_account.email,
            username=user_account.username,
            role=user_account.role,
            aether_balance=float(user_account.aether_balance or 0),
            total_rewards_earned=float(user_account.total_rewards_earned or 0),
            reputation_score=user_account.reputation_score,
            profile_data=user_account.profile_data,
            created_at=user_account.created_at.isoformat(),
            last_login=user_account.last_login.isoformat() if user_account.last_login else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user account"
        )


@router.put("/{account_id}", response_model=UserAccountResponse)
async def update_user_account(
    account_id: str,
    user_data: UserAccountUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update user account"""
    
    try:
        from sqlalchemy import select
        result = await db.execute(
            select(UserAccount).where(UserAccount.hedera_account_id == account_id)
        )
        user_account = result.scalar_one_or_none()
        
        if not user_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found"
            )
        
        # Update fields
        if user_data.email is not None:
            user_account.email = user_data.email
        if user_data.username is not None:
            user_account.username = user_data.username
        if user_data.profile_data is not None:
            user_account.profile_data = user_data.profile_data
        if user_data.privacy_settings is not None:
            user_account.privacy_settings = user_data.privacy_settings
        
        await db.commit()
        await db.refresh(user_account)
        
        logger.info(f"Updated user account: {account_id}")
        
        return UserAccountResponse(
            id=user_account.id,
            hedera_account_id=user_account.hedera_account_id,
            email=user_account.email,
            username=user_account.username,
            role=user_account.role,
            aether_balance=float(user_account.aether_balance or 0),
            total_rewards_earned=float(user_account.total_rewards_earned or 0),
            reputation_score=user_account.reputation_score,
            profile_data=user_account.profile_data,
            created_at=user_account.created_at.isoformat(),
            last_login=user_account.last_login.isoformat() if user_account.last_login else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user account"
        )


@router.get("/{account_id}/portfolio")
async def get_user_portfolio(
    account_id: str,
    db: AsyncSession = Depends(get_db_session),
    hedera_client = Depends(get_hedera_client)
):
    """Get user's tokenomics portfolio"""
    
    try:
        tokenomics_service = TokenomicsService(hedera_client)
        portfolio = await tokenomics_service.get_user_portfolio(db, account_id)
        
        return portfolio
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get user portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user portfolio"
        )


@router.post("/{account_id}/rewards")
async def distribute_reward(
    account_id: str,
    reward_amount: float,
    reward_type: str = "manual",
    db: AsyncSession = Depends(get_db_session),
    hedera_client = Depends(get_hedera_client)
):
    """Manually distribute rewards to user (admin only)"""
    
    try:
        from decimal import Decimal
        
        tokenomics_service = TokenomicsService(hedera_client)
        result = await tokenomics_service.distribute_rewards(
            db=db,
            user_account_id=account_id,
            reward_amount=Decimal(str(reward_amount)),
            reward_type=reward_type
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to distribute reward: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to distribute reward"
        )


@router.get("/", response_model=List[UserAccountResponse])
async def list_user_accounts(
    limit: int = 100,
    offset: int = 0,
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List user accounts with pagination"""
    
    try:
        from sqlalchemy import select
        
        query = select(UserAccount)
        
        if role:
            query = query.where(UserAccount.role == role)
        
        query = query.order_by(UserAccount.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        user_accounts = result.scalars().all()
        
        return [
            UserAccountResponse(
                id=user.id,
                hedera_account_id=user.hedera_account_id,
                email=user.email,
                username=user.username,
                role=user.role,
                aether_balance=float(user.aether_balance or 0),
                total_rewards_earned=float(user.total_rewards_earned or 0),
                reputation_score=user.reputation_score,
                profile_data=user.profile_data,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None
            )
            for user in user_accounts
        ]
        
    except Exception as e:
        logger.error(f"Failed to list user accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list user accounts"
        )


@router.get("/stats/overview")
async def get_user_statistics(
    db: AsyncSession = Depends(get_db_session)
):
    """Get user statistics overview"""
    
    try:
        from sqlalchemy import select, func
        
        # Total users
        total_result = await db.execute(select(func.count(UserAccount.id)))
        total_users = total_result.scalar()
        
        # Users by role
        role_result = await db.execute(
            select(UserAccount.role, func.count(UserAccount.id))
            .group_by(UserAccount.role)
        )
        users_by_role = dict(role_result.all())
        
        # Recent registrations (last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_result = await db.execute(
            select(func.count(UserAccount.id))
            .where(UserAccount.created_at >= recent_cutoff)
        )
        recent_registrations = recent_result.scalar()
        
        # Average reputation
        avg_reputation_result = await db.execute(
            select(func.avg(UserAccount.reputation_score))
            .where(UserAccount.reputation_score.is_not(None))
        )
        avg_reputation = avg_reputation_result.scalar() or 0.0
        
        return {
            "total_users": total_users,
            "users_by_role": users_by_role,
            "recent_registrations_24h": recent_registrations,
            "average_reputation": round(float(avg_reputation), 3),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )
