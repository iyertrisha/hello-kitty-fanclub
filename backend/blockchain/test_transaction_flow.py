"""
Test Transaction Flow Script for Kirana Store Management System

Tests the complete verification → blockchain flow with sample transcripts.
Run this script to verify everything is working before connecting to the React Native app.

Usage: python test_transaction_flow.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from services.fraud_detection import get_fraud_detection_service, FraudRiskLevel
from services.transaction_verification import (
    TransactionVerificationService,
    VerificationStatus,
    StorageLocation
)
from blockchain.mock_data import (
    generate_shopkeeper_history,
    generate_transaction_data,
    generate_test_scenarios,
    SAMPLE_TRANSCRIPTS
)

# Try to import blockchain service
try:
    from blockchain.utils.contract_service import BlockchainService
    from blockchain.config import config
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False


def print_header(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(name: str, passed: bool, details: str = ""):
    """Print test result"""
    icon = "✅" if passed else "❌"
    print(f"  {icon} {name}")
    if details:
        print(f"     └─ {details}")


def test_fraud_detection():
    """Test fraud detection service"""
    print_header("FRAUD DETECTION SERVICE TESTS")
    
    fraud_service = get_fraud_detection_service()
    all_passed = True
    
    # Test 1: Normal credit validation
    result = fraud_service.validate_credit_transaction(
        amount=50000,  # ₹500
        customer_id="customer_123",
        shopkeeper_id="shop_001",
        customer_confirmed=True
    )
    passed = result['is_valid']
    print_result("Normal credit validation", passed, f"Valid: {result['is_valid']}")
    all_passed = all_passed and passed
    
    # Test 2: Invalid amount
    result = fraud_service.validate_credit_transaction(
        amount=0,
        customer_id="customer_123",
        shopkeeper_id="shop_001",
        customer_confirmed=True
    )
    passed = not result['is_valid']
    print_result("Invalid amount detection", passed, f"Errors: {result['errors']}")
    all_passed = all_passed and passed
    
    # Test 3: Credit anomaly detection
    history = generate_shopkeeper_history(average_daily_sales=100000)  # ₹1,000
    result = fraud_service.detect_credit_anomaly(
        transaction_data={
            'amount': 300000,  # ₹3,000 - 3x daily sales
            'customer_id': 'customer_123',
            'shopkeeper_id': 'shop_001'
        },
        shopkeeper_history=history
    )
    passed = result.is_flagged
    print_result("High amount anomaly detection", passed, 
                f"Flagged: {result.is_flagged}, Risk: {result.risk_level.value}")
    all_passed = all_passed and passed
    
    # Test 4: Sales validation
    result = fraud_service.validate_sales_transaction(
        product="Rice (1kg)",
        price=6000,  # ₹60
        quantity=2
    )
    passed = result['is_valid']
    print_result("Normal sales validation", passed, f"Total: ₹{result['total_amount']/100:.2f}")
    all_passed = all_passed and passed
    
    # Test 5: Sales anomaly with price deviation
    history = generate_shopkeeper_history()
    result = fraud_service.detect_sales_anomaly(
        transaction_data={
            'product': 'Rice (1kg)',
            'price': 15000,  # ₹150 - way above catalog price of ₹60
            'quantity': 1,
            'shopkeeper_id': 'shop_001'
        },
        shopkeeper_history=history
    )
    passed = result.is_flagged
    print_result("Price deviation detection", passed, 
                f"Flagged: {result.is_flagged}, Reasons: {len(result.reasons)}")
    all_passed = all_passed and passed
    
    return all_passed


def test_verification_service():
    """Test transaction verification service"""
    print_header("TRANSACTION VERIFICATION SERVICE TESTS")
    
    verification_service = TransactionVerificationService(None)  # No blockchain for now
    all_passed = True
    
    # Test 1: Hash calculation
    hash1 = verification_service.calculate_transcript_hash("मुझे 500 रुपये का क्रेडिट चाहिए")
    hash2 = verification_service.calculate_transcript_hash("मुझे 500 रुपये का क्रेडिट चाहिए")
    hash3 = verification_service.calculate_transcript_hash("different transcript")
    
    passed = (hash1 == hash2) and (hash1 != hash3) and len(hash1) == 64
    print_result("Hash calculation consistency", passed, f"Hash length: {len(hash1)}")
    all_passed = all_passed and passed
    
    # Test 2: Credit verification - normal
    history = generate_shopkeeper_history()
    result = verification_service.verify_credit_transaction({
        'transcript': "राहुल को 500 रुपये का उधार",
        'type': 'credit',
        'amount': 50000,
        'customer_id': 'cust_001',
        'shopkeeper_id': 'shop_001',
        'customer_confirmed': True,
        'shopkeeper_history': history,
        'language': 'hi-IN'
    })
    passed = result.status == VerificationStatus.VERIFIED
    print_result("Credit verification (normal)", passed, 
                f"Status: {result.status.value}, Blockchain: {result.should_write_to_blockchain}")
    all_passed = all_passed and passed
    
    # Test 3: Credit verification - high risk
    history = generate_shopkeeper_history(average_daily_sales=50000)  # Low sales
    result = verification_service.verify_credit_transaction({
        'transcript': "10000 रुपये का उधार",
        'type': 'credit',
        'amount': 1000000,  # ₹10,000 - very high
        'customer_id': 'cust_001',
        'shopkeeper_id': 'shop_001',
        'customer_confirmed': False,
        'shopkeeper_history': history,
        'language': 'hi-IN'
    })
    passed = result.status in [VerificationStatus.FLAGGED, VerificationStatus.PENDING]
    print_result("Credit verification (high risk)", passed, 
                f"Status: {result.status.value}, Risk: {result.fraud_check['risk_level']}")
    all_passed = all_passed and passed
    
    # Test 4: Sales verification
    history = generate_shopkeeper_history()
    result = verification_service.verify_sales_transaction({
        'transcript': "2 kg rice 120 rupees",
        'type': 'sale',
        'product': 'Rice (1kg)',
        'price': 6000,
        'quantity': 2,
        'shopkeeper_id': 'shop_001',
        'shopkeeper_history': history,
        'language': 'en-IN'
    })
    passed = result.status == VerificationStatus.VERIFIED
    print_result("Sales verification", passed, 
                f"Status: {result.status.value}, Blockchain: {result.should_write_to_blockchain}")
    all_passed = all_passed and passed
    
    # Test 5: Daily sales aggregation
    sales_data = [
        {'amount': 5000, 'product': 'Rice'},
        {'amount': 3000, 'product': 'Sugar'},
        {'amount': 12000, 'product': 'Oil'}
    ]
    result = verification_service.aggregate_daily_sales(
        shopkeeper_id='shop_001',
        date=datetime.now(),
        sales_data=sales_data
    )
    passed = result['success'] and result['total_amount'] == 20000
    print_result("Daily sales aggregation", passed, 
                f"Total: ₹{result['total_amount']/100:.2f}, Count: {result['transaction_count']}")
    all_passed = all_passed and passed
    
    return all_passed


def test_blockchain_integration():
    """Test blockchain integration (if available)"""
    print_header("BLOCKCHAIN INTEGRATION TESTS")
    
    if not BLOCKCHAIN_AVAILABLE:
        print("  ⚠️  Blockchain service not available - skipping")
        return True
    
    try:
        config.validate(require_contract=True)
    except ValueError as e:
        print(f"  ⚠️  Blockchain not configured: {e}")
        return True
    
    all_passed = True
    
    try:
        # Initialize blockchain service
        blockchain_service = BlockchainService(
            rpc_url=config.RPC_URL,
            private_key=config.PRIVATE_KEY,
            contract_address=config.CONTRACT_ADDRESS
        )
        print_result("Blockchain connection", True, 
                    f"Address: {blockchain_service.address[:10]}...")
        
        # Initialize verification service with blockchain
        verification_service = TransactionVerificationService(blockchain_service)
        
        # Test: Verify and write credit transaction
        history = generate_shopkeeper_history()
        result = verification_service.verify_credit_transaction({
            'transcript': "Test blockchain credit transaction",
            'type': 'credit',
            'amount': 25000,  # ₹250
            'customer_id': 'cust_test',
            'shopkeeper_id': 'shop_test',
            'customer_confirmed': True,
            'shopkeeper_history': history,
            'language': 'en-IN'
        })
        
        if result.should_write_to_blockchain:
            # Write to blockchain
            tx_result = verification_service.write_to_blockchain(result, tx_type=1)  # CREDIT
            passed = tx_result.get('success', False)
            print_result("Blockchain write", passed, 
                        f"TX Hash: {tx_result.get('tx_hash', 'N/A')[:16]}...")
            all_passed = all_passed and passed
        else:
            print_result("Blockchain write skipped", True, 
                        f"Reason: {result.status.value}")
        
        # Get next transaction ID
        next_id = blockchain_service.get_next_transaction_id()
        print_result("Transaction ID check", True, f"Next ID: {next_id}")
        
    except Exception as e:
        print_result("Blockchain test failed", False, str(e))
        all_passed = False
    
    return all_passed


def test_scenarios():
    """Test all predefined scenarios"""
    print_header("SCENARIO TESTS")
    
    verification_service = TransactionVerificationService(None)
    scenarios = generate_test_scenarios()
    
    all_passed = True
    
    for i, scenario in enumerate(scenarios, 1):
        name = scenario['name']
        data = scenario['data']
        expected = scenario['expected_result']
        
        # Add shopkeeper history
        data['shopkeeper_history'] = scenario['shopkeeper_history']
        
        # Verify based on type
        tx_type = data.get('type', 'credit')
        if tx_type == 'sale':
            result = verification_service.verify_sales_transaction(data)
        else:
            result = verification_service.verify_credit_transaction(data)
        
        actual = result.status.value
        passed = actual == expected
        
        print_result(f"Scenario {i}: {name}", passed, 
                    f"Expected: {expected}, Got: {actual}")
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_hindi_english_transcripts():
    """Test with Hindi and English transcripts"""
    print_header("HINDI/ENGLISH TRANSCRIPT TESTS")
    
    verification_service = TransactionVerificationService(None)
    history = generate_shopkeeper_history()
    
    all_passed = True
    
    # Hindi credit transcripts
    for transcript in SAMPLE_TRANSCRIPTS['credit_hindi'][:3]:
        result = verification_service.verify_credit_transaction({
            'transcript': transcript,
            'type': 'credit',
            'amount': 50000,
            'customer_id': 'cust_001',
            'shopkeeper_id': 'shop_001',
            'customer_confirmed': True,
            'shopkeeper_history': history,
            'language': 'hi-IN'
        })
        passed = result.transcript_hash and len(result.transcript_hash) == 64
        print_result(f"Hindi: {transcript[:30]}...", passed, 
                    f"Hash: {result.transcript_hash[:16]}...")
        all_passed = all_passed and passed
    
    # English credit transcripts
    for transcript in SAMPLE_TRANSCRIPTS['credit_english'][:3]:
        result = verification_service.verify_credit_transaction({
            'transcript': transcript,
            'type': 'credit',
            'amount': 50000,
            'customer_id': 'cust_001',
            'shopkeeper_id': 'shop_001',
            'customer_confirmed': True,
            'shopkeeper_history': history,
            'language': 'en-IN'
        })
        passed = result.transcript_hash and len(result.transcript_hash) == 64
        print_result(f"English: {transcript[:30]}...", passed, 
                    f"Hash: {result.transcript_hash[:16]}...")
        all_passed = all_passed and passed
    
    return all_passed


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🧪 KIRANA TRANSACTION FLOW TESTS")
    print("  Testing: react-native-voice STT → Verification → Blockchain")
    print("=" * 70)
    
    results = {
        'Fraud Detection': test_fraud_detection(),
        'Verification Service': test_verification_service(),
        'Blockchain Integration': test_blockchain_integration(),
        'Scenarios': test_scenarios(),
        'Hindi/English Transcripts': test_hindi_english_transcripts()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for name, result in results.items():
        print_result(name, result)
    
    print("\n" + "-" * 70)
    print(f"  Total: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("  Ready to integrate with React Native app.")
    else:
        print("\n  ⚠️  Some tests failed. Review the output above.")
    
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

