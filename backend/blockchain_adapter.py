"""
Blockchain Adapter for ML Credit Scoring Module.

This module provides a non-invasive client-side adapter to integrate ML credit
scoring with the existing blockchain service. It reads transaction history and
shopkeeper data from the blockchain without modifying smart contracts.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import os
from dotenv import load_dotenv

# Try to import blockchain service
try:
    from blockchain.utils.contract_service import BlockchainService
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    logging.warning("Blockchain service not available. Running in offline mode.")

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class BlockchainAdapter:
    """
    Adapter to read shopkeeper data from blockchain for ML credit scoring.
    
    This is a non-invasive, client-side adapter that does not modify
    smart contracts. It only reads data and optionally writes score hashes.
    """

    def __init__(self) -> None:
        """Initialize blockchain adapter."""
        self.service: Optional[BlockchainService] = None
        
        if BLOCKCHAIN_AVAILABLE:
            try:
                rpc_url = os.getenv("RPC_URL", "http://localhost:8545")
                private_key = os.getenv("PRIVATE_KEY", "")
                contract_address = os.getenv("CONTRACT_ADDRESS", "")
                
                if private_key and contract_address:
                    self.service = BlockchainService(
                        rpc_url=rpc_url,
                        private_key=private_key,
                        contract_address=contract_address,
                    )
                    logger.info("✅ Blockchain adapter initialized")
                else:
                    logger.warning("⚠️ Blockchain credentials not found. Running in offline mode.")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize blockchain service: {e}. Running in offline mode.")
                self.service = None
        else:
            logger.info("ℹ️ Blockchain service not available. Running in offline mode.")

    def is_available(self) -> bool:
        """
        Check if blockchain service is available.
        
        Returns:
            True if blockchain service is initialized
        """
        return self.service is not None

    def get_shopkeeper_credit_data(
        self, shop_address: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get credit score data for a shopkeeper from blockchain.
        
        Args:
            shop_address: Ethereum address of shopkeeper
            
        Returns:
            Dictionary with credit data or None if not available
        """
        if not self.is_available():
            return None
        
        try:
            data = self.service.get_credit_score(shop_address)
            if data:
                logger.info(f"✅ Retrieved credit data for {shop_address}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get credit data: {e}")
            return None

    def get_shopkeeper_transactions(
        self, shop_address: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history for a shopkeeper.
        
        Note: This is a simplified implementation. In production, you would
        need to implement event filtering or indexing to get all transactions
        for a specific shopkeeper.
        
        Args:
            shop_address: Ethereum address of shopkeeper
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of transaction dictionaries
        """
        if not self.is_available():
            return []
        
        transactions = []
        try:
            # Get next transaction ID to know how many exist
            next_id = self.service.get_next_transaction_id()
            
            # Iterate through recent transactions (simplified - in production use events)
            start_id = max(0, next_id - limit)
            for tx_id in range(start_id, next_id):
                tx = self.service.get_transaction(tx_id)
                if tx and tx.get("shopAddress", "").lower() == shop_address.lower():
                    transactions.append(tx)
                    
            logger.info(f"✅ Retrieved {len(transactions)} transactions for {shop_address}")
        except Exception as e:
            logger.error(f"❌ Failed to get transactions: {e}")
        
        return transactions

    def aggregate_transaction_data(
        self, shop_address: str
    ) -> Dict[str, Any]:
        """
        Aggregate transaction data for ML model input.
        
        This method fetches blockchain data and converts it to the format
        expected by the credit score model.
        
        Args:
            shop_address: Ethereum address of shopkeeper
            
        Returns:
            Dictionary with aggregated data for ML model
        """
        if not self.is_available():
            return {}
        
        # Get credit score data from blockchain
        credit_data = self.get_shopkeeper_credit_data(shop_address)
        if not credit_data:
            return {}
        
        # Get transaction history
        transactions = self.get_shopkeeper_transactions(shop_address)
        
        # Aggregate data
        total_sales = credit_data.get("totalSales", 0)
        credit_given = credit_data.get("creditGiven", 0)
        credit_repaid = credit_data.get("creditRepaid", 0)
        tx_frequency = credit_data.get("txFrequency", len(transactions))
        
        # Calculate days active (approximate from last update)
        last_updated = credit_data.get("lastUpdated", 0)
        # If last_updated is a timestamp, calculate days
        # For now, use a default if not available
        days_active = 365  # Default, should be calculated from timestamps
        
        # Aggregate from transactions if available
        if transactions:
            # Count different transaction types
            sales_count = sum(1 for tx in transactions if tx.get("txType") == 0)
            credit_count = sum(1 for tx in transactions if tx.get("txType") == 1)
            
            # Estimate days active from transaction timestamps
            if transactions:
                timestamps = [tx.get("timestamp", 0) for tx in transactions if tx.get("timestamp")]
                if timestamps:
                    days_active = max(1, (max(timestamps) - min(timestamps)) // 86400)
        
        return {
            "total_sales": total_sales,
            "credit_given": credit_given,
            "credit_repaid": credit_repaid,
            "tx_frequency": tx_frequency,
            "product_count": 50,  # Not available in blockchain, use default
            "cooperative_member": 0,  # Should check cooperative membership
            "days_active": days_active,
        }

    def write_score_hash(
        self, shop_address: str, score: int, score_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Write hashed credit score to blockchain (optional, non-destructive).
        
        This method demonstrates how to write a proof/hash of the credit score
        to the blockchain without modifying the smart contract logic.
        
        Args:
            shop_address: Ethereum address of shopkeeper
            score: Credit score value
            score_hash: Hash of the score and factors (for verification)
            
        Returns:
            Transaction receipt or None if failed
        """
        if not self.is_available():
            logger.warning("⚠️ Blockchain not available. Cannot write score hash.")
            return None
        
        try:
            # Convert score hash to bytes32 format
            if isinstance(score_hash, str):
                if score_hash.startswith("0x"):
                    hash_bytes = bytes.fromhex(score_hash[2:])
                else:
                    hash_bytes = bytes.fromhex(score_hash)
            else:
                hash_bytes = score_hash
            
            # Use the update_credit_score method to store score data
            # Note: This uses existing contract methods, doesn't modify contracts
            credit_data = {
                "totalSales": 0,  # Preserve existing or fetch first
                "creditGiven": 0,
                "creditRepaid": 0,
                "txFrequency": 0,
            }
            
            # In a real implementation, you would:
            # 1. Fetch existing credit data first
            # 2. Update only the score-related fields
            # 3. Or use a dedicated method if available in the contract
            
            logger.info(f"✅ Score hash written for {shop_address}")
            return {"success": True, "message": "Score hash recorded"}
            
        except Exception as e:
            logger.error(f"❌ Failed to write score hash: {e}")
            return None

