"""
Credit Score Model for KiranaChain Shopkeepers.

This module implements a weighted credit scoring model that evaluates shopkeepers
based on transaction consistency, business growth, product diversity, cooperative
participation, and repayment history.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np

logger = logging.getLogger(__name__)


class CreditScoreModel:
    """
    Credit scoring model for shopkeepers.
    
    Uses weighted factors to calculate credit scores between 300-900.
    Can load a trained ML model if available, otherwise uses deterministic weights.
    """

    # Feature weights (sum = 1.0)
    WEIGHTS = {
        "transaction_consistency": 0.25,
        "business_growth": 0.20,
        "product_diversity": 0.15,
        "cooperative_participation": 0.15,
        "repayment_history": 0.25,
    }

    MIN_SCORE = 300
    MAX_SCORE = 900
    SCORE_RANGE = MAX_SCORE - MIN_SCORE

    def __init__(self, model_path: str = "model.pkl") -> None:
        """
        Initialize the credit score model.
        
        Args:
            model_path: Path to trained model file (relative to backend/ml/)
        """
        self.model_path = Path(__file__).parent / model_path
        self.model: Optional[Any] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load trained model if available, otherwise use weighted baseline."""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                logger.info(f"✅ Loaded trained model from {self.model_path}")
            else:
                logger.info("ℹ️ No trained model found, using weighted baseline")
                self.model = None
        except Exception as e:
            logger.warning(f"⚠️ Failed to load model: {e}. Using weighted baseline")
            self.model = None

    def _validate_input(self, shopkeeper_data: Dict[str, Any]) -> None:
        """
        Validate input data structure.
        
        Args:
            shopkeeper_data: Dictionary containing shopkeeper features
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = [
            "total_sales",
            "credit_given",
            "credit_repaid",
            "tx_frequency",
            "product_count",
            "cooperative_member",
            "days_active",
        ]

        for field in required_fields:
            if field not in shopkeeper_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate numeric types and ranges
        if shopkeeper_data["total_sales"] < 0:
            raise ValueError("total_sales must be non-negative")
        if shopkeeper_data["credit_given"] < 0:
            raise ValueError("credit_given must be non-negative")
        if shopkeeper_data["credit_repaid"] < 0:
            raise ValueError("credit_repaid must be non-negative")
        if shopkeeper_data["days_active"] <= 0:
            raise ValueError("days_active must be positive")
        if shopkeeper_data["product_count"] < 0:
            raise ValueError("product_count must be non-negative")
        if shopkeeper_data["cooperative_member"] not in [0, 1]:
            raise ValueError("cooperative_member must be 0 or 1")

    def _calculate_factors(self, shopkeeper_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate normalized factor scores (0.0 to 1.0).
        
        Args:
            shopkeeper_data: Dictionary containing shopkeeper features
            
        Returns:
            Dictionary of factor scores
        """
        total_sales = float(shopkeeper_data["total_sales"])
        credit_given = float(shopkeeper_data["credit_given"])
        credit_repaid = float(shopkeeper_data["credit_repaid"])
        tx_frequency = float(shopkeeper_data["tx_frequency"])
        product_count = float(shopkeeper_data["product_count"])
        cooperative_member = int(shopkeeper_data["cooperative_member"])
        days_active = float(shopkeeper_data["days_active"])

        # Transaction consistency: based on transaction frequency per day
        # Normalize: 0-2 transactions/day = 0.0, 5+ transactions/day = 1.0
        tx_per_day = tx_frequency / days_active if days_active > 0 else 0
        transaction_consistency = min(1.0, max(0.0, (tx_per_day - 0.5) / 4.5))

        # Business growth: based on total sales normalized
        # Normalize: 0-50k = 0.0, 500k+ = 1.0
        business_growth = min(1.0, max(0.0, total_sales / 500000.0))

        # Product diversity: based on product count
        # Normalize: 0-10 products = 0.0, 100+ products = 1.0
        product_diversity = min(1.0, max(0.0, product_count / 100.0))

        # Cooperative participation: binary (0 or 1)
        cooperative_participation = float(cooperative_member)

        # Repayment history: based on credit repayment ratio
        # Normalize: 0-70% repaid = 0.0, 100%+ repaid = 1.0
        if credit_given > 0:
            repayment_ratio = credit_repaid / credit_given
            repayment_history = min(1.0, max(0.0, (repayment_ratio - 0.7) / 0.3))
        else:
            # No credit given, neutral score
            repayment_history = 0.5

        return {
            "transaction_consistency": transaction_consistency,
            "business_growth": business_growth,
            "product_diversity": product_diversity,
            "cooperative_participation": cooperative_participation,
            "repayment_history": repayment_history,
        }

    def predict(self, shopkeeper_data: Dict[str, Any]) -> int:
        """
        Predict credit score for a shopkeeper.
        
        Args:
            shopkeeper_data: Dictionary containing shopkeeper features
                Required keys: total_sales, credit_given, credit_repaid,
                tx_frequency, product_count, cooperative_member, days_active
                
        Returns:
            Credit score as integer between 300-900
        """
        self._validate_input(shopkeeper_data)
        factors = self._calculate_factors(shopkeeper_data)

        if self.model is not None:
            # Use trained model if available
            try:
                # Prepare features for model (same order as training)
                features = np.array([[
                    shopkeeper_data["total_sales"],
                    shopkeeper_data["credit_given"],
                    shopkeeper_data["credit_repaid"],
                    shopkeeper_data["tx_frequency"],
                    shopkeeper_data["product_count"],
                    shopkeeper_data["cooperative_member"],
                    shopkeeper_data["days_active"],
                ]])
                
                # Apply same feature engineering as training
                credit_ratio = (
                    shopkeeper_data["credit_repaid"] / shopkeeper_data["credit_given"]
                    if shopkeeper_data["credit_given"] > 0
                    else 0.0
                )
                sales_per_day = (
                    shopkeeper_data["total_sales"] / shopkeeper_data["days_active"]
                    if shopkeeper_data["days_active"] > 0
                    else 0.0
                )
                tx_per_day = (
                    shopkeeper_data["tx_frequency"] / shopkeeper_data["days_active"]
                    if shopkeeper_data["days_active"] > 0
                    else 0.0
                )
                
                # Extended features array
                extended_features = np.array([[
                    shopkeeper_data["total_sales"],
                    shopkeeper_data["credit_given"],
                    shopkeeper_data["credit_repaid"],
                    shopkeeper_data["tx_frequency"],
                    shopkeeper_data["product_count"],
                    shopkeeper_data["cooperative_member"],
                    shopkeeper_data["days_active"],
                    credit_ratio,
                    sales_per_day,
                    tx_per_day,
                ]])
                
                score = float(self.model.predict(extended_features)[0])
            except Exception as e:
                logger.warning(f"Model prediction failed: {e}. Using weighted baseline")
                score = self._weighted_score(factors)
        else:
            # Use weighted baseline
            score = self._weighted_score(factors)

        # Clamp to valid range
        score = max(self.MIN_SCORE, min(self.MAX_SCORE, int(round(score))))
        return score

    def _weighted_score(self, factors: Dict[str, float]) -> float:
        """
        Calculate score using weighted factors.
        
        Args:
            factors: Dictionary of normalized factor scores
            
        Returns:
            Raw score (will be clamped later)
        """
        weighted_sum = sum(
            factors[factor] * weight
            for factor, weight in self.WEIGHTS.items()
        )
        return self.MIN_SCORE + (weighted_sum * self.SCORE_RANGE)

    def get_factors(self, shopkeeper_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Get individual factor contributions.
        
        Args:
            shopkeeper_data: Dictionary containing shopkeeper features
            
        Returns:
            Dictionary of factor scores (0.0 to 1.0)
        """
        self._validate_input(shopkeeper_data)
        return self._calculate_factors(shopkeeper_data)

    def explain_score(self, shopkeeper_data: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of the credit score.
        
        Args:
            shopkeeper_data: Dictionary containing shopkeeper features
            
        Returns:
            Human-readable explanation string
        """
        self._validate_input(shopkeeper_data)
        factors = self._calculate_factors(shopkeeper_data)
        score = self.predict(shopkeeper_data)

        explanations = []
        
        if factors["repayment_history"] >= 0.8:
            explanations.append("excellent repayment history")
        elif factors["repayment_history"] >= 0.6:
            explanations.append("good repayment history")
        elif factors["repayment_history"] >= 0.4:
            explanations.append("moderate repayment history")
        else:
            explanations.append("needs improvement in repayment history")

        if factors["transaction_consistency"] >= 0.7:
            explanations.append("consistent transaction activity")
        elif factors["transaction_consistency"] < 0.3:
            explanations.append("low transaction frequency")

        if factors["business_growth"] >= 0.7:
            explanations.append("strong business volume")
        elif factors["business_growth"] < 0.3:
            explanations.append("limited business volume")

        if factors["product_diversity"] >= 0.6:
            explanations.append("diverse product range")
        elif factors["product_diversity"] < 0.3:
            explanations.append("limited product range")

        if factors["cooperative_participation"] == 1.0:
            explanations.append("active cooperative member")

        explanation_text = f"Credit score: {score}/900. "
        explanation_text += "Factors: " + ", ".join(explanations) + "."

        return explanation_text

