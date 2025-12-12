"""
Transaction Verification Service for Kirana Store Management System

Accepts text transcripts from react-native-voice (on-device STT) and performs
verification flow to decide blockchain writes.

This service does NOT require Google Speech API - transcription happens on-device.
"""

import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.fraud_detection import (
    FraudDetectionService,
    FraudCheckResult,
    FraudRiskLevel,
    get_fraud_detection_service
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Status of transaction verification"""
    VERIFIED = "verified"
    PENDING = "pending"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class StorageLocation(Enum):
    """Where to store the transaction"""
    BLOCKCHAIN = "blockchain"
    DATABASE_ONLY = "database_only"
    DATABASE_PENDING = "database_pending"


@dataclass
class VerificationResult:
    """Result of transaction verification"""
    status: VerificationStatus
    storage_location: StorageLocation
    transcript_hash: str
    fraud_check: Optional[Dict[str, Any]]
    errors: list
    warnings: list
    should_write_to_blockchain: bool
    metadata: Dict[str, Any]


class TransactionVerificationService:
    """
    Service for verifying transactions from react-native-voice transcripts.
    
    Input Format:
    {
        'transcript': str,          # Text from react-native-voice (NOT audio!)
        'type': 'credit' | 'sale' | 'repay',
        'amount': int,              # in paise
        'customer_id': str,
        'shopkeeper_id': str,
        'customer_confirmed': bool, # From WhatsApp (Mohit's work)
        'shopkeeper_history': dict, # For anomaly detection
        'language': str             # 'hi-IN', 'en-IN', etc.
    }
    """
    
    def __init__(self, blockchain_service=None):
        """
        Initialize verification service.
        
        Args:
            blockchain_service: Optional BlockchainService instance.
                               If not provided, blockchain writes will be skipped.
        """
        self.fraud_service = get_fraud_detection_service()
        self.blockchain_service = blockchain_service
        logger.info("TransactionVerificationService initialized")
    
    def verify_credit_transaction(
        self,
        transaction_data: Dict[str, Any]
    ) -> VerificationResult:
        """
        Complete credit verification flow.
        
        Verification Steps:
        1. Calculate SHA256 hash of transcript
        2. Run fraud detection checks
        3. Check customer confirmation status
        4. Decision: Write to blockchain if all pass, else database only
        
        Args:
            transaction_data: Transaction data with transcript
        
        Returns:
            VerificationResult with decision
        """
        errors = []
        warnings = []
        
        # Extract data
        transcript = transaction_data.get('transcript', '')
        amount = transaction_data.get('amount', 0)
        customer_id = transaction_data.get('customer_id', '')
        shopkeeper_id = transaction_data.get('shopkeeper_id', '')
        customer_confirmed = transaction_data.get('customer_confirmed', False)
        shopkeeper_history = transaction_data.get('shopkeeper_history', {})
        language = transaction_data.get('language', 'en-IN')
        
        # Step 1: Calculate transcript hash
        transcript_hash = self.calculate_transcript_hash(transcript)
        logger.info(f"Transcript hash: {transcript_hash[:16]}...")
        
        # Step 2: Basic validation
        validation = self.fraud_service.validate_credit_transaction(
            amount=amount,
            customer_id=customer_id,
            shopkeeper_id=shopkeeper_id,
            customer_confirmed=customer_confirmed
        )
        
        if not validation['is_valid']:
            errors.extend(validation['errors'])
        warnings.extend(validation['warnings'])
        
        # Step 3: Fraud detection
        fraud_check = self.fraud_service.detect_credit_anomaly(
            transaction_data={
                'amount': amount,
                'customer_id': customer_id,
                'shopkeeper_id': shopkeeper_id,
                'timestamp': datetime.now()
            },
            shopkeeper_history=shopkeeper_history
        )
        
        # Step 4: Decision logic
        status, storage_location = self._decide_credit_storage(
            validation=validation,
            fraud_check=fraud_check,
            customer_confirmed=customer_confirmed,
            amount=amount
        )
        
        should_write = storage_location == StorageLocation.BLOCKCHAIN
        
        result = VerificationResult(
            status=status,
            storage_location=storage_location,
            transcript_hash=transcript_hash,
            fraud_check={
                'is_flagged': fraud_check.is_flagged,
                'risk_level': fraud_check.risk_level.value,
                'score': fraud_check.score,
                'reasons': fraud_check.reasons,
                'recommendations': fraud_check.recommendations
            },
            errors=errors,
            warnings=warnings,
            should_write_to_blockchain=should_write,
            metadata={
                'language': language,
                'amount': amount,
                'customer_id': customer_id,
                'shopkeeper_id': shopkeeper_id,
                'customer_confirmed': customer_confirmed,
                'verified_at': datetime.now().isoformat()
            }
        )
        
        logger.info(f"Credit verification: status={status.value}, blockchain={should_write}")
        return result
    
    def verify_sales_transaction(
        self,
        transaction_data: Dict[str, Any]
    ) -> VerificationResult:
        """
        Sales transaction verification flow.
        
        Sales Flow:
        1. Real-time validation (product, price, amount)
        2. Write to database immediately
        3. Background anomaly detection
        4. End-of-day aggregation for blockchain
        
        Args:
            transaction_data: Transaction data with transcript
        
        Returns:
            VerificationResult (sales always go to database, aggregated to blockchain later)
        """
        errors = []
        warnings = []
        
        # Extract data
        transcript = transaction_data.get('transcript', '')
        product = transaction_data.get('product', '')
        price = transaction_data.get('price', 0)
        quantity = transaction_data.get('quantity', 1)
        shopkeeper_id = transaction_data.get('shopkeeper_id', '')
        shopkeeper_history = transaction_data.get('shopkeeper_history', {})
        language = transaction_data.get('language', 'en-IN')
        
        # Step 1: Calculate transcript hash
        transcript_hash = self.calculate_transcript_hash(transcript)
        
        # Step 2: Basic validation
        product_catalog = shopkeeper_history.get('product_catalog', {})
        validation = self.fraud_service.validate_sales_transaction(
            product=product,
            price=price,
            quantity=quantity,
            product_catalog=product_catalog
        )
        
        if not validation['is_valid']:
            errors.extend(validation['errors'])
        warnings.extend(validation['warnings'])
        
        # Step 3: Anomaly detection (background check)
        fraud_check = self.fraud_service.detect_sales_anomaly(
            transaction_data={
                'product': product,
                'price': price,
                'quantity': quantity,
                'shopkeeper_id': shopkeeper_id
            },
            shopkeeper_history=shopkeeper_history
        )
        
        # Sales always go to database, aggregated to blockchain daily
        # Individual sales never written directly to blockchain
        status = VerificationStatus.VERIFIED if not errors else VerificationStatus.REJECTED
        storage_location = StorageLocation.DATABASE_ONLY
        
        if fraud_check.is_flagged:
            status = VerificationStatus.FLAGGED
            warnings.append("Transaction flagged for review")
        
        result = VerificationResult(
            status=status,
            storage_location=storage_location,
            transcript_hash=transcript_hash,
            fraud_check={
                'is_flagged': fraud_check.is_flagged,
                'risk_level': fraud_check.risk_level.value,
                'score': fraud_check.score,
                'reasons': fraud_check.reasons,
                'recommendations': fraud_check.recommendations
            },
            errors=errors,
            warnings=warnings,
            should_write_to_blockchain=False,  # Sales are aggregated daily
            metadata={
                'language': language,
                'product': product,
                'price': price,
                'quantity': quantity,
                'total_amount': validation.get('total_amount', price * quantity),
                'shopkeeper_id': shopkeeper_id,
                'verified_at': datetime.now().isoformat()
            }
        )
        
        logger.info(f"Sales verification: status={status.value}")
        return result
    
    def calculate_transcript_hash(self, transcript: str) -> str:
        """
        Calculate SHA256 hash of transcript for blockchain storage.
        
        Args:
            transcript: Text transcript from react-native-voice
        
        Returns:
            SHA256 hash as hex string (64 characters, suitable for bytes32)
        """
        if not transcript:
            transcript = ""
        
        # Normalize transcript (lowercase, strip whitespace)
        normalized = transcript.strip().lower()
        
        # Calculate SHA256 hash
        hash_bytes = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        return hash_bytes
    
    def should_write_to_blockchain(
        self,
        verification_result: VerificationResult
    ) -> Tuple[bool, str]:
        """
        Decision helper to determine if transaction should go to blockchain.
        
        Args:
            verification_result: Result from verification
        
        Returns:
            Tuple of (should_write: bool, reason: str)
        """
        if verification_result.status == VerificationStatus.REJECTED:
            return False, "Transaction rejected due to validation errors"
        
        if verification_result.status == VerificationStatus.FLAGGED:
            return False, "Transaction flagged for review"
        
        if verification_result.storage_location == StorageLocation.BLOCKCHAIN:
            return True, "Transaction verified for blockchain"
        
        if verification_result.storage_location == StorageLocation.DATABASE_PENDING:
            return False, "Awaiting customer confirmation"
        
        return False, "Transaction stored in database only"
    
    def _decide_credit_storage(
        self,
        validation: Dict[str, Any],
        fraud_check: FraudCheckResult,
        customer_confirmed: bool,
        amount: int
    ) -> Tuple[VerificationStatus, StorageLocation]:
        """
        Decide verification status and storage location for credit transactions.
        
        Decision Logic:
        - All checks pass + customer confirms → BLOCKCHAIN
        - Checks pass but no customer response → DATABASE_PENDING
        - Any check fails → DATABASE_ONLY (flagged for review)
        """
        # Validation failed
        if not validation['is_valid']:
            return VerificationStatus.REJECTED, StorageLocation.DATABASE_ONLY
        
        # High risk fraud detection
        if fraud_check.risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL]:
            return VerificationStatus.FLAGGED, StorageLocation.DATABASE_ONLY
        
        # Medium risk - needs confirmation
        if fraud_check.risk_level == FraudRiskLevel.MEDIUM:
            if customer_confirmed:
                return VerificationStatus.VERIFIED, StorageLocation.BLOCKCHAIN
            else:
                return VerificationStatus.PENDING, StorageLocation.DATABASE_PENDING
        
        # Low risk
        if fraud_check.risk_level == FraudRiskLevel.LOW:
            # High amount still needs confirmation
            if amount > 200000 and not customer_confirmed:  # ₹2,000 in paise
                return VerificationStatus.PENDING, StorageLocation.DATABASE_PENDING
            
            if customer_confirmed or amount <= 200000:
                return VerificationStatus.VERIFIED, StorageLocation.BLOCKCHAIN
            else:
                return VerificationStatus.PENDING, StorageLocation.DATABASE_PENDING
        
        # Default: pending
        return VerificationStatus.PENDING, StorageLocation.DATABASE_PENDING
    
    def write_to_blockchain(
        self,
        verification_result: VerificationResult,
        tx_type: int = 1  # Default to CREDIT
    ) -> Dict[str, Any]:
        """
        Write verified transaction to blockchain.
        
        Args:
            verification_result: Verified transaction result
            tx_type: Transaction type (0=SALE, 1=CREDIT, 2=REPAY)
        
        Returns:
            Dict with blockchain transaction result
        """
        if not self.blockchain_service:
            logger.warning("Blockchain service not configured")
            return {
                'success': False,
                'error': 'Blockchain service not configured'
            }
        
        should_write, reason = self.should_write_to_blockchain(verification_result)
        
        if not should_write:
            return {
                'success': False,
                'error': reason,
                'storage_location': verification_result.storage_location.value
            }
        
        try:
            # Get shop address from blockchain service
            shop_address = self.blockchain_service.address
            
            # Record transaction
            result = self.blockchain_service.record_transaction(
                voice_hash=verification_result.transcript_hash,
                shop_address=shop_address,
                amount=verification_result.metadata.get('amount', 0),
                tx_type=tx_type
            )
            
            if result['success']:
                logger.info(f"Transaction written to blockchain: {result['tx_hash']}")
            else:
                logger.error(f"Blockchain write failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Blockchain write error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def aggregate_daily_sales(
        self,
        shopkeeper_id: str,
        date: datetime,
        sales_data: list
    ) -> Dict[str, Any]:
        """
        Aggregate daily sales for batch blockchain write.
        
        Args:
            shopkeeper_id: Shopkeeper identifier
            date: Date of aggregation
            sales_data: List of sales transactions for the day
        
        Returns:
            Dict with aggregation result and batch hash
        """
        if not sales_data:
            return {
                'success': False,
                'error': 'No sales data to aggregate'
            }
        
        # Calculate totals
        total_amount = sum(sale.get('amount', 0) for sale in sales_data)
        total_count = len(sales_data)
        
        # Create batch data string for hashing
        batch_data = f"{shopkeeper_id}:{date.isoformat()}:{total_amount}:{total_count}"
        batch_hash = hashlib.sha256(batch_data.encode('utf-8')).hexdigest()
        
        return {
            'success': True,
            'shopkeeper_id': shopkeeper_id,
            'date': date.isoformat(),
            'total_amount': total_amount,
            'transaction_count': total_count,
            'batch_hash': batch_hash,
            'ready_for_blockchain': True
        }


# Singleton instance
_verification_service: Optional[TransactionVerificationService] = None


def get_verification_service(blockchain_service=None) -> TransactionVerificationService:
    """Get or create verification service instance"""
    global _verification_service
    if _verification_service is None:
        _verification_service = TransactionVerificationService(blockchain_service)
    return _verification_service

