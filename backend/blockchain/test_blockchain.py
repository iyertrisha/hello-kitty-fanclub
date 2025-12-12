"""
Test script for KiranaLedger blockchain service
Run this after deploying the contract to test functionality
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.contract_service import BlockchainService
from config import config
import hashlib


def create_test_hash(data: str) -> str:
    """Create a test hash from a string"""
    return hashlib.sha256(data.encode()).hexdigest()


def test_blockchain_service():
    """Test blockchain service functionality"""
    
    print("\n" + "=" * 70)
    print("🧪 KIRANA LEDGER BLOCKCHAIN TEST")
    print("=" * 70)

    # Validate configuration (require contract address for testing)
    try:
        config.validate(require_contract=True)
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n⚠️  Make sure to:")
        print("   1. Copy env.template to .env")
        print("   2. Fill in your PRIVATE_KEY (use Hardhat's default for localhost)")
        print("   3. Deploy the contract first: npm run deploy:localhost")
        print("   4. Update CONTRACT_ADDRESS in .env with the deployed address")
        return

    # Initialize service
    try:
        print(f"\n📡 Connecting to blockchain...")
        service = BlockchainService(
            rpc_url=config.RPC_URL,
            private_key=config.PRIVATE_KEY,
            contract_address=config.CONTRACT_ADDRESS,
        )
        print("✅ Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return

    # Get account balance
    print(f"\n💰 Account Balance:")
    balance = service.get_account_balance_eth()
    print(f"   {service.address}: {balance:.4f} ETH")

    # Test 1: Check if already registered
    print(f"\n📝 Test 1: Check Registration Status")
    is_registered = service.is_shopkeeper_registered(service.address)
    print(f"   Already registered: {is_registered}")

    # Test 2: Register shopkeeper (if not registered)
    if not is_registered:
        print(f"\n📝 Test 2: Register Shopkeeper")
        result = service.register_shopkeeper()
        if result["success"]:
            print(f"   ✅ Registration successful!")
            print(f"   Transaction: {result['tx_hash']}")
            print(f"   Block: {result['block_number']}")
        else:
            print(f"   ❌ Registration failed: {result['error']}")
            return
    else:
        print(f"\n📝 Test 2: Register Shopkeeper - SKIPPED (already registered)")

    # Test 3: Record a transaction
    print(f"\n📝 Test 3: Record Transaction")
    voice_hash = create_test_hash("test_transaction_001")
    amount = 10000  # Amount in wei
    tx_type = 0  # SALE

    result = service.record_transaction(
        voice_hash=voice_hash,
        shop_address=service.address,
        amount=amount,
        tx_type=tx_type,
    )

    if result["success"]:
        print(f"   ✅ Transaction recorded successfully!")
        print(f"   Transaction: {result['tx_hash']}")
        print(f"   Block: {result['block_number']}")
        print(f"   Gas used: {result['gas_used']}")
    else:
        print(f"   ❌ Transaction recording failed: {result['error']}")
        return

    # Test 4: Get transaction by ID
    print(f"\n📝 Test 4: Get Transaction")
    next_tx_id = service.get_next_transaction_id()
    tx_id = next_tx_id - 1  # Get the last recorded transaction

    transaction = service.get_transaction(tx_id)
    if transaction:
        print(f"   ✅ Transaction retrieved:")
        print(f"   ID: {transaction['id']}")
        print(f"   Shop: {transaction['shopAddress']}")
        print(f"   Amount: {transaction['amount']} wei")
        print(f"   Type: {transaction['txType']}")
        print(f"   Timestamp: {transaction['timestamp']}")
        print(f"   Voice Hash: {transaction['voiceHash'][:16]}...")
    else:
        print(f"   ❌ Failed to retrieve transaction")

    # Test 5: Record batch transactions
    print(f"\n📝 Test 5: Record Batch Transactions")
    batch_hash = create_test_hash("batch_001_10_transactions")
    total_amount = 50000  # Total amount in wei

    result = service.record_batch_transactions(
        batch_hash=batch_hash,
        shop_address=service.address,
        total_amount=total_amount,
    )

    if result["success"]:
        print(f"   ✅ Batch recorded successfully!")
        print(f"   Transaction: {result['tx_hash']}")
        print(f"   Block: {result['block_number']}")
    else:
        print(f"   ❌ Batch recording failed: {result['error']}")

    # Test 6: Update credit score
    print(f"\n📝 Test 6: Update Credit Score")
    credit_data = {
        "totalSales": 100000,
        "creditGiven": 20000,
        "creditRepaid": 15000,
        "txFrequency": 25,
    }

    result = service.update_credit_score(
        shop_address=service.address,
        credit_data=credit_data,
    )

    if result["success"]:
        print(f"   ✅ Credit score updated successfully!")
        print(f"   Transaction: {result['tx_hash']}")
    else:
        print(f"   ❌ Credit score update failed: {result['error']}")

    # Test 7: Get credit score
    print(f"\n📝 Test 7: Get Credit Score")
    score = service.get_credit_score(service.address)
    if score:
        print(f"   ✅ Credit score retrieved:")
        print(f"   Total Sales: {score['totalSales']}")
        print(f"   Credit Given: {score['creditGiven']}")
        print(f"   Credit Repaid: {score['creditRepaid']}")
        print(f"   Transaction Frequency: {score['txFrequency']}")
        print(f"   Last Updated: {score['lastUpdated']}")
    else:
        print(f"   ❌ Failed to retrieve credit score")

    # Test 8: Get next transaction ID
    print(f"\n📝 Test 8: Get Next Transaction ID")
    next_id = service.get_next_transaction_id()
    print(f"   Next Transaction ID: {next_id}")

    print("\n" + "=" * 70)
    print("🎉 ALL TESTS COMPLETED!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_blockchain_service()



