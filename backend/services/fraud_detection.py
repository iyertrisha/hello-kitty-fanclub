"""
Fraud Detection Service for Kirana Store Management System

Detects suspicious transaction patterns and validates business rules.
Works with text transcripts from react-native-voice (on-device STT).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FraudRiskLevel(Enum):
    """Risk levels for fraud detection"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FraudCheckResult:
    """Result of a fraud detection check"""
    is_flagged: bool
    risk_level: FraudRiskLevel
    reasons: List[str]
    score: float  # 0.0 to 1.0, higher = more suspicious
    recommendations: List[str]


class FraudDetectionService:
    """
    Service for detecting fraudulent transactions and anomalies.
    
    Anomaly Detection Rules:
    - Credit amount > average daily sales → FLAG
    - Credit frequency > 3 per day → FLAG
    - Sales price deviation > ±20% from catalog → FLAG
    - Customer with no purchase history (credit only) → FLAG
    - Unusual transaction timing (off-hours)
    """
    
    # Configuration thresholds
    MAX_CREDIT_PER_DAY = 3  # Maximum credits per customer per day
    PRICE_DEVIATION_THRESHOLD = 0.20  # 20% price deviation allowed
    HIGH_AMOUNT_MULTIPLIER = 2.0  # Flag if amount > 2x average daily sales
    OFF_HOURS_START = 22  # 10 PM
    OFF_HOURS_END = 6  # 6 AM
    
    def __init__(self):
        logger.info("FraudDetectionService initialized")
    
    def detect_credit_anomaly(
        self,
        transaction_data: Dict[str, Any],
        shopkeeper_history: Dict[str, Any]
    ) -> FraudCheckResult:
        """
        Detect unusual credit patterns.
        
        Args:
            transaction_data: Current transaction data
                - amount: int (in paise)
                - customer_id: str
                - shopkeeper_id: str
                - timestamp: datetime (optional)
            shopkeeper_history: Historical data for the shopkeeper
                - average_daily_sales: int
                - total_transactions: int
                - customer_credits_today: Dict[str, int]
                - customer_purchase_history: Dict[str, List]
        
        Returns:
            FraudCheckResult with detection details
        """
        reasons = []
        score = 0.0
        recommendations = []
        
        amount = transaction_data.get('amount', 0)
        customer_id = transaction_data.get('customer_id', '')
        timestamp = transaction_data.get('timestamp', datetime.now())
        
        avg_daily_sales = shopkeeper_history.get('average_daily_sales', 0)
        customer_credits_today = shopkeeper_history.get('customer_credits_today', {})
        customer_purchase_history = shopkeeper_history.get('customer_purchase_history', {})
        
        # Rule 1: Credit amount > average daily sales
        if avg_daily_sales > 0 and amount > avg_daily_sales * self.HIGH_AMOUNT_MULTIPLIER:
            reasons.append(f"Credit amount (₹{amount/100:.2f}) exceeds 2x average daily sales (₹{avg_daily_sales/100:.2f})")
            score += 0.3
            recommendations.append("Verify customer identity and purpose of credit")
        
        # Rule 2: Credit frequency > 3 per day
        credits_today = customer_credits_today.get(customer_id, 0)
        if credits_today >= self.MAX_CREDIT_PER_DAY:
            reasons.append(f"Customer has {credits_today} credits today (max: {self.MAX_CREDIT_PER_DAY})")
            score += 0.25
            recommendations.append("Review customer's credit history before approving")
        
        # Rule 3: Customer with no purchase history (credit only)
        customer_purchases = customer_purchase_history.get(customer_id, [])
        if len(customer_purchases) == 0:
            reasons.append("Customer has no purchase history (credit-only)")
            score += 0.2
            recommendations.append("Request customer to make at least one purchase first")
        
        # Rule 4: Unusual timing (off-hours)
        hour = timestamp.hour if isinstance(timestamp, datetime) else datetime.now().hour
        if hour >= self.OFF_HOURS_START or hour < self.OFF_HOURS_END:
            reasons.append(f"Transaction at unusual hour ({hour}:00)")
            score += 0.15
            recommendations.append("Verify transaction authenticity")
        
        # Rule 5: Very high amount (potential fraud)
        if amount > 100000:  # > ₹1000 in paise
            reasons.append(f"High credit amount: ₹{amount/100:.2f}")
            score += 0.1
        
        # Determine risk level
        is_flagged = score > 0.2
        risk_level = self._calculate_risk_level(score)
        
        logger.info(f"Credit anomaly check: flagged={is_flagged}, score={score:.2f}, reasons={len(reasons)}")
        
        return FraudCheckResult(
            is_flagged=is_flagged,
            risk_level=risk_level,
            reasons=reasons,
            score=min(score, 1.0),
            recommendations=recommendations
        )
    
    def validate_credit_transaction(
        self,
        amount: int,
        customer_id: str,
        shopkeeper_id: str,
        customer_confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Basic validation rules for credit transactions.
        
        Args:
            amount: Transaction amount in paise
            customer_id: Customer identifier
            shopkeeper_id: Shopkeeper identifier
            customer_confirmed: Whether customer confirmed via WhatsApp
        
        Returns:
            Dict with validation result
        """
        errors = []
        warnings = []
        
        # Amount validation
        if amount <= 0:
            errors.append("Amount must be greater than 0")
        
        if amount > 5000000:  # ₹50,000 in paise
            errors.append("Credit amount exceeds maximum limit (₹50,000)")
        elif amount > 1000000:  # ₹10,000 in paise
            warnings.append("High credit amount - requires additional verification")
        
        # ID validation
        if not customer_id or len(customer_id) < 3:
            errors.append("Invalid customer ID")
        
        if not shopkeeper_id or len(shopkeeper_id) < 3:
            errors.append("Invalid shopkeeper ID")
        
        # Customer confirmation
        if not customer_confirmed and amount > 500000:  # ₹5,000 in paise
            warnings.append("Customer confirmation recommended for amounts > ₹5,000")
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'requires_confirmation': amount > 200000 and not customer_confirmed  # ₹2,000
        }
    
    def detect_sales_anomaly(
        self,
        transaction_data: Dict[str, Any],
        shopkeeper_history: Dict[str, Any]
    ) -> FraudCheckResult:
        """
        Detect unusual sales patterns.
        
        Args:
            transaction_data: Current transaction data
                - product: str
                - price: int (in paise)
                - quantity: int
                - shopkeeper_id: str
            shopkeeper_history: Historical data
                - product_catalog: Dict[str, int] (product -> price)
                - average_daily_sales: int
                - sales_today: int
        
        Returns:
            FraudCheckResult with detection details
        """
        reasons = []
        score = 0.0
        recommendations = []
        
        product = transaction_data.get('product', '')
        price = transaction_data.get('price', 0)
        quantity = transaction_data.get('quantity', 1)
        
        product_catalog = shopkeeper_history.get('product_catalog', {})
        avg_daily_sales = shopkeeper_history.get('average_daily_sales', 0)
        sales_today = shopkeeper_history.get('sales_today', 0)
        
        # Rule 1: Price deviation from catalog
        if product in product_catalog:
            catalog_price = product_catalog[product]
            if catalog_price > 0:
                deviation = abs(price - catalog_price) / catalog_price
                if deviation > self.PRICE_DEVIATION_THRESHOLD:
                    reasons.append(f"Price deviation: ₹{price/100:.2f} vs catalog ₹{catalog_price/100:.2f} ({deviation*100:.1f}%)")
                    score += 0.3
                    recommendations.append("Verify price with customer before recording")
        
        # Rule 2: Unusual quantity
        if quantity > 100:
            reasons.append(f"Unusual quantity: {quantity} units")
            score += 0.2
            recommendations.append("Confirm bulk order with customer")
        
        # Rule 3: Daily sales exceeding average significantly
        total_today = sales_today + (price * quantity)
        if avg_daily_sales > 0 and total_today > avg_daily_sales * 3:
            reasons.append(f"Daily sales (₹{total_today/100:.2f}) exceeds 3x average (₹{avg_daily_sales/100:.2f})")
            score += 0.15
        
        # Rule 4: Product not in catalog
        if product and product not in product_catalog:
            reasons.append(f"Product '{product}' not in catalog")
            score += 0.1
            recommendations.append("Add product to catalog for future tracking")
        
        is_flagged = score > 0.2
        risk_level = self._calculate_risk_level(score)
        
        logger.info(f"Sales anomaly check: flagged={is_flagged}, score={score:.2f}")
        
        return FraudCheckResult(
            is_flagged=is_flagged,
            risk_level=risk_level,
            reasons=reasons,
            score=min(score, 1.0),
            recommendations=recommendations
        )
    
    def validate_sales_transaction(
        self,
        product: str,
        price: int,
        quantity: int,
        product_catalog: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Real-time validation for sales transactions.
        
        Args:
            product: Product name
            price: Price in paise
            quantity: Quantity sold
            product_catalog: Optional catalog for price validation
        
        Returns:
            Dict with validation result
        """
        errors = []
        warnings = []
        
        # Basic validation
        if not product or len(product.strip()) == 0:
            errors.append("Product name is required")
        
        if price <= 0:
            errors.append("Price must be greater than 0")
        
        if quantity <= 0:
            errors.append("Quantity must be greater than 0")
        
        if price > 10000000:  # ₹1,00,000 in paise
            errors.append("Price exceeds maximum limit")
        
        # Catalog validation
        if product_catalog and product in product_catalog:
            catalog_price = product_catalog[product]
            if catalog_price > 0:
                deviation = abs(price - catalog_price) / catalog_price
                if deviation > self.PRICE_DEVIATION_THRESHOLD:
                    warnings.append(f"Price differs from catalog by {deviation*100:.1f}%")
        
        is_valid = len(errors) == 0
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'total_amount': price * quantity
        }
    
    def _calculate_risk_level(self, score: float) -> FraudRiskLevel:
        """Calculate risk level based on fraud score"""
        if score >= 0.7:
            return FraudRiskLevel.CRITICAL
        elif score >= 0.5:
            return FraudRiskLevel.HIGH
        elif score >= 0.3:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW


# Singleton instance
_fraud_service: Optional[FraudDetectionService] = None


def get_fraud_detection_service() -> FraudDetectionService:
    """Get or create fraud detection service instance"""
    global _fraud_service
    if _fraud_service is None:
        _fraud_service = FraudDetectionService()
    return _fraud_service

