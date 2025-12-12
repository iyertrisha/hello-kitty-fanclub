"""
FastAPI router for Credit Score Prediction API.

This module provides REST endpoints for credit score prediction using
the ML model and optional blockchain integration.
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from ml.credit_score_model import CreditScoreModel
from blockchain_adapter import BlockchainAdapter
from database.models import Shopkeeper, Transaction, Product, Cooperative
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML Credit Scoring"])

# Initialize model and blockchain adapter
model = CreditScoreModel()
blockchain_adapter = BlockchainAdapter()


def aggregate_shopkeeper_data_from_db(shopkeeper_id: str) -> Dict[str, Any]:
    """
    Aggregate shopkeeper data from database for credit scoring.
    
    Fetches shopkeeper, verified transactions, and calculates metrics.
    
    Args:
        shopkeeper_id: Shopkeeper ID string
        
    Returns:
        Dictionary with aggregated shopkeeper data:
        - total_sales: Sum of verified sale transactions
        - credit_given: Sum of verified credit transactions
        - credit_repaid: Sum of verified repay transactions
        - tx_frequency: Count of verified transactions
        - product_count: Number of products for shopkeeper
        - days_active: Days since shopkeeper registration (min 1)
        - cooperative_member: 1 if shopkeeper is in a cooperative, 0 otherwise
        
    Raises:
        Shopkeeper.DoesNotExist: If shopkeeper not found
        InvalidId: If shopkeeper_id format is invalid
    """
    # Fetch shopkeeper
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise
    except InvalidId:
        raise
    
    # Fetch all verified transactions for this shopkeeper
    verified_transactions = Transaction.objects(
        shopkeeper_id=shopkeeper_id,
        status='verified'
    )
    
    # Calculate transaction metrics
    total_sales = sum(
        float(tx.amount) for tx in verified_transactions 
        if tx.type == 'sale'
    )
    credit_given = sum(
        float(tx.amount) for tx in verified_transactions 
        if tx.type == 'credit'
    )
    credit_repaid = sum(
        float(tx.amount) for tx in verified_transactions 
        if tx.type == 'repay'
    )
    tx_frequency = verified_transactions.count()
    
    # Get product count
    product_count = Product.objects(shopkeeper_id=shopkeeper_id).count()
    
    # Calculate days active (minimum 1 day)
    if shopkeeper.registered_at:
        days_active = max(1, (datetime.utcnow() - shopkeeper.registered_at).days)
    else:
        days_active = 1
    
    # Check if shopkeeper is a member of any cooperative
    cooperative_member = 0
    try:
        cooperatives = Cooperative.objects(members=shopkeeper_id)
        if cooperatives.count() > 0:
            cooperative_member = 1
    except Exception as e:
        logger.warning(f"Error checking cooperative membership: {e}")
        cooperative_member = 0
    
    return {
        "total_sales": total_sales,
        "credit_given": credit_given,
        "credit_repaid": credit_repaid,
        "tx_frequency": tx_frequency,
        "product_count": product_count,
        "days_active": days_active,
        "cooperative_member": cooperative_member,
    }


class ShopkeeperInputModel(BaseModel):
    """Input model for credit score prediction."""
    
    total_sales: float = Field(..., ge=0, description="Total sales amount")
    credit_given: float = Field(..., ge=0, description="Total credit given")
    credit_repaid: float = Field(..., ge=0, description="Total credit repaid")
    tx_frequency: int = Field(..., ge=0, description="Transaction frequency count")
    product_count: int = Field(..., ge=0, description="Number of products")
    cooperative_member: int = Field(..., ge=0, le=1, description="Cooperative membership (0 or 1)")
    days_active: int = Field(..., gt=0, description="Number of days active")
    shopkeeper_id: Optional[str] = Field(None, description="Shopkeeper identifier")
    shop_address: Optional[str] = Field(None, description="Ethereum address for blockchain lookup")
    
    @field_validator("cooperative_member")
    @classmethod
    def validate_cooperative_member(cls, v: int) -> int:
        """Validate cooperative_member is 0 or 1."""
        if v not in [0, 1]:
            raise ValueError("cooperative_member must be 0 or 1")
        return v


class CreditScoreFactorsModel(BaseModel):
    """Model for credit score factors."""
    
    transaction_consistency: float = Field(..., description="Transaction consistency factor (0.0-1.0)")
    business_growth: float = Field(..., description="Business growth factor (0.0-1.0)")
    product_diversity: float = Field(..., description="Product diversity factor (0.0-1.0)")
    cooperative_participation: float = Field(..., description="Cooperative participation factor (0.0-1.0)")
    repayment_history: float = Field(..., description="Repayment history factor (0.0-1.0)")


class CreditScoreOutputModel(BaseModel):
    """Output model for credit score prediction."""
    
    score: int = Field(..., ge=300, le=900, description="Credit score (300-900)")
    factors: CreditScoreFactorsModel = Field(..., description="Individual factor scores")
    explanation: str = Field(..., description="Human-readable explanation")
    blockchain_verified: bool = Field(default=False, description="Whether data was verified on blockchain")
    source: List[str] = Field(default_factory=lambda: ["database"], description="Data sources used: database, blockchain")


@router.post("/predict-credit-score", response_model=CreditScoreOutputModel)
async def predict_credit_score(
    data: ShopkeeperInputModel
) -> CreditScoreOutputModel:
    """
    Predict credit score for a shopkeeper.
    
    This endpoint calculates a credit score based on shopkeeper data.
    If shop_address is provided and blockchain is available, it will attempt
    to fetch and merge blockchain-verified data.
    
    Args:
        data: Shopkeeper input data
        
    Returns:
        Credit score prediction with factors and explanation
        
    Raises:
        HTTPException: If input validation fails or model error occurs
    """
    try:
        # Prepare shopkeeper data dictionary
        shopkeeper_data = {
            "total_sales": data.total_sales,
            "credit_given": data.credit_given,
            "credit_repaid": data.credit_repaid,
            "tx_frequency": data.tx_frequency,
            "product_count": data.product_count,
            "cooperative_member": data.cooperative_member,
            "days_active": data.days_active,
        }
        
        # Optionally fetch blockchain data if address provided
        blockchain_verified = False
        source = ["database"]
        if data.shop_address and blockchain_adapter.is_available():
            try:
                blockchain_data = blockchain_adapter.aggregate_transaction_data(
                    data.shop_address
                )
                if blockchain_data:
                    # Merge blockchain data (blockchain takes precedence for verified fields)
                    shopkeeper_data.update({
                        k: v for k, v in blockchain_data.items()
                        if v is not None and v > 0
                    })
                    blockchain_verified = True
                    source.append("blockchain")
                    logger.info(f"✅ Merged blockchain data for {data.shop_address}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch blockchain data: {e}")
        
        # Predict credit score
        score = model.predict(shopkeeper_data)
        
        # Get factors
        factors_dict = model.get_factors(shopkeeper_data)
        factors = CreditScoreFactorsModel(**factors_dict)
        
        # Get explanation
        explanation = model.explain_score(shopkeeper_data)
        
        return CreditScoreOutputModel(
            score=score,
            factors=factors,
            explanation=explanation,
            blockchain_verified=blockchain_verified,
            source=source,
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/predict-credit-score/{shopkeeper_id}", response_model=CreditScoreOutputModel)
async def predict_credit_score_by_id(shopkeeper_id: str) -> CreditScoreOutputModel:
    """
    Predict credit score for a shopkeeper by ID.
    
    Fetches shopkeeper data from database and calculates credit score.
    Optionally merges blockchain-verified data if shopkeeper has wallet_address.
    
    Args:
        shopkeeper_id: Shopkeeper ID string
        
    Returns:
        Credit score prediction with factors and explanation
        
    Raises:
        HTTPException: 404 if shopkeeper not found, 400 for validation errors, 500 for server errors
    """
    try:
        # Validate shopkeeper_id format first (before database query)
        if not shopkeeper_id or not shopkeeper_id.strip():
            raise HTTPException(status_code=400, detail="Invalid shopkeeper ID")
        
        # Validate MongoDB ObjectId format (24 hex characters)
        if len(shopkeeper_id) != 24:
            raise HTTPException(status_code=400, detail="Invalid shopkeeper ID")
        
        try:
            # Try to validate it's hex
            int(shopkeeper_id, 16)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid shopkeeper ID")
        
        # Fetch shopkeeper data from database
        try:
            shopkeeper_data = aggregate_shopkeeper_data_from_db(shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            logger.error(f"❌ Shopkeeper not found: {shopkeeper_id}")
            raise HTTPException(status_code=404, detail=f"Shopkeeper {shopkeeper_id} not found")
        except InvalidId:
            logger.error(f"❌ Invalid shopkeeper ID format: {shopkeeper_id}")
            raise HTTPException(status_code=400, detail="Invalid shopkeeper ID")
        except Exception as e:
            logger.error(f"❌ Database error fetching shopkeeper data: {e}")
            raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
        
        # Fetch shopkeeper object to get wallet_address for blockchain lookup
        blockchain_verified = False
        source = ["database"]
        try:
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            wallet_address = shopkeeper.wallet_address if shopkeeper else None
            
            # Optionally fetch blockchain data if address available
            if wallet_address and blockchain_adapter.is_available():
                try:
                    blockchain_data = blockchain_adapter.aggregate_transaction_data(
                        wallet_address
                    )
                    if blockchain_data:
                        # Merge blockchain data (blockchain takes precedence for verified fields)
                        shopkeeper_data.update({
                            k: v for k, v in blockchain_data.items()
                            if v is not None and v > 0
                        })
                        blockchain_verified = True
                        source.append("blockchain")
                        logger.info(f"✅ Merged blockchain data for shopkeeper {shopkeeper_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch blockchain data: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch shopkeeper for blockchain lookup: {e}")
        
        # Predict credit score
        try:
            score = model.predict(shopkeeper_data)
        except ValueError as e:
            logger.error(f"❌ Model validation error: {e}")
            raise HTTPException(status_code=400, detail=f"Model validation error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Model prediction error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Model prediction error: {str(e)}"
            )
        
        # Get factors
        factors_dict = model.get_factors(shopkeeper_data)
        factors = CreditScoreFactorsModel(**factors_dict)
        
        # Get explanation
        explanation = model.explain_score(shopkeeper_data)
        
        logger.info(f"✅ Credit score calculated for shopkeeper {shopkeeper_id}: {score}")
        
        return CreditScoreOutputModel(
            score=score,
            factors=factors,
            explanation=explanation,
            blockchain_verified=blockchain_verified,
            source=source,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in predict_credit_score_by_id: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns status of ML model, database connection, and blockchain adapter.
    """
    health_status = {
        "model_loaded": model.model is not None,
        "db_connected": False,
        "shopkeeper_count": 0,
        "blockchain_available": blockchain_adapter.is_available(),
        "message": "ML subsystem operational"
    }
    
    # Check database connection by attempting a simple query
    try:
        shopkeeper_count = Shopkeeper.objects.count()
        health_status["db_connected"] = True
        health_status["shopkeeper_count"] = shopkeeper_count
    except Exception as e:
        logger.warning(f"⚠️ Database health check failed: {e}")
        health_status["db_connected"] = False
        health_status["message"] = f"ML subsystem operational (database unavailable: {str(e)})"
    
    return health_status

