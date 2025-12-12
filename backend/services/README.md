# Backend Services - Kirana Store Management System

## Overview

This directory contains the verification and fraud detection services for processing voice transactions from the React Native shopkeeper app.

## Services

### 1. Fraud Detection Service

**File:** `fraud_detection.py`

Detects suspicious transaction patterns and validates business rules.

**Key Functions:**
- `detect_credit_anomaly(transaction_data, shopkeeper_history)` - Detect unusual credit patterns
- `validate_credit_transaction(amount, customer_id, shopkeeper_id)` - Basic validation rules
- `detect_sales_anomaly(transaction_data, shopkeeper_history)` - Detect unusual sales patterns
- `validate_sales_transaction(product, price, amount)` - Real-time sales validation

**Anomaly Detection Rules:**
- Credit amount > 2x average daily sales → FLAG
- Credit frequency > 3 per day per customer → FLAG
- Sales price deviation > ±20% from catalog → FLAG
- Customer with no purchase history (credit only) → FLAG
- Unusual transaction timing (off-hours 10PM-6AM) → FLAG

### 2. Transaction Verification Service

**File:** `transaction_verification.py`

Processes text transcripts from react-native-voice and decides blockchain writes.

**Key Functions:**
- `verify_credit_transaction(transaction_data)` - Complete credit verification flow
- `verify_sales_transaction(transaction_data)` - Sales validation flow
- `calculate_transcript_hash(transcript)` - SHA256 hash calculation
- `should_write_to_blockchain(verification_result)` - Decision helper
- `aggregate_daily_sales(shopkeeper_id, date, sales_data)` - Batch aggregation

**Input Format:**
```python
transaction_data = {
    'transcript': str,          # Text from react-native-voice (NOT audio!)
    'type': 'credit' | 'sale' | 'repay',
    'amount': int,              # in paise
    'customer_id': str,
    'shopkeeper_id': str,
    'customer_confirmed': bool, # From WhatsApp
    'shopkeeper_history': dict, # For anomaly detection
    'language': str             # 'hi-IN', 'en-IN', etc.
}
```

## Usage

### Basic Usage

```python
from services.fraud_detection import get_fraud_detection_service
from services.transaction_verification import get_verification_service

# Get service instances
fraud_service = get_fraud_detection_service()
verification_service = get_verification_service()

# Verify a credit transaction
result = verification_service.verify_credit_transaction({
    'transcript': 'राहुल को 500 रुपये का उधार',
    'type': 'credit',
    'amount': 50000,
    'customer_id': 'cust_001',
    'shopkeeper_id': 'shop_001',
    'customer_confirmed': True,
    'shopkeeper_history': {...},
    'language': 'hi-IN'
})

# Check result
if result.should_write_to_blockchain:
    print("Write to blockchain")
else:
    print(f"Store in database: {result.status.value}")
```

### With Blockchain Integration

```python
from blockchain.utils.contract_service import BlockchainService
from blockchain.config import config
from services.transaction_verification import TransactionVerificationService

# Initialize blockchain
blockchain_service = BlockchainService(
    rpc_url=config.RPC_URL,
    private_key=config.PRIVATE_KEY,
    contract_address=config.CONTRACT_ADDRESS
)

# Initialize verification with blockchain
verification_service = TransactionVerificationService(blockchain_service)

# Verify and write to blockchain
result = verification_service.verify_credit_transaction({...})
if result.should_write_to_blockchain:
    tx_result = verification_service.write_to_blockchain(result, tx_type=1)
    print(f"TX Hash: {tx_result['tx_hash']}")
```

## Verification Flow

### Credit Transactions

```
1. Calculate SHA256 hash of transcript
2. Run basic validation (amount, IDs)
3. Run fraud detection:
   - Check amount vs daily sales average
   - Check credit frequency
   - Check customer purchase history
   - Check transaction timing
4. Determine risk level
5. Decision based on risk + customer confirmation:
   - LOW risk + confirmed → BLOCKCHAIN
   - MEDIUM risk + confirmed → BLOCKCHAIN
   - MEDIUM risk + not confirmed → DATABASE (pending)
   - HIGH/CRITICAL risk → DATABASE (flagged)
```

### Sales Transactions

```
1. Calculate SHA256 hash
2. Validate product, price, quantity
3. Check for price deviation from catalog
4. Write to DATABASE immediately
5. Background anomaly detection
6. End-of-day: Aggregate and write batch to BLOCKCHAIN
```

## Testing

Run the test scripts to verify everything works:

```bash
# Test the complete flow
cd whackiest/backend/blockchain
python test_transaction_flow.py

# Start the test API server
python test_api.py

# Test with curl
curl -X POST http://localhost:5001/test/transactions \
  -H "Content-Type: application/json" \
  -d '{"transcript": "राहुल को 500 रुपये का उधार", "type": "credit", "amount": 50000, "customer_id": "cust_001", "shopkeeper_id": "shop_001", "customer_confirmed": true, "language": "hi-IN"}'
```

## Dependencies

- Python 3.9+
- No external APIs required (Google Speech API NOT needed)
- Blockchain service (optional - for actual blockchain writes)

## File Structure

```
whackiest/backend/services/
├── fraud_detection.py          # Fraud detection service
├── transaction_verification.py # Transaction verification service
└── README.md                   # This file

whackiest/backend/blockchain/
├── test_api.py                 # Test Flask API
├── test_transaction_flow.py    # Test script
├── mock_data.py                # Mock data generator
└── API_CONTRACT.md             # API documentation
```

