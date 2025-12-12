"""
FastAPI router for Credit Score Prediction API.

This module provides REST endpoints for credit score prediction using
the ML model and optional blockchain integration.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from ml.credit_score_model import CreditScoreModel
from blockchain_adapter import BlockchainAdapter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML Credit Scoring"])

# Initialize model and blockchain adapter
model = CreditScoreModel()
blockchain_adapter = BlockchainAdapter()


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


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model.model is not None,
        "blockchain_available": blockchain_adapter.is_available(),
    }

