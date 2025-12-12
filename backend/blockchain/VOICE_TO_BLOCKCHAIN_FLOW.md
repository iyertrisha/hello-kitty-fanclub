# Voice Transaction → Blockchain → Admin Dashboard Flow

## Overview

This document explains the complete flow from voice input to blockchain storage and visibility in the admin dashboard.

## Complete Flow

```
🎤 Voice Input
    ↓
📝 Speech-to-Text (Python speech_recognition)
    ↓
🔍 Parse Transaction (Extract product, quantity, amount)
    ↓
📡 POST /api/transactions (Backend API)
    ↓
✅ Verification & Fraud Detection
    ↓
⛓️  Blockchain Write (if verified)
    ↓
💾 MongoDB Storage
    ↓
📊 Admin Dashboard → Blockchain Logs
```

## Step-by-Step Process

### 1. Voice Input (`voice_demo.py`)

**Command:**
```bash
cd helloKittyFanclub\backend\blockchain
python voice_demo.py
```

**What happens:**
- Captures voice input from microphone
- Transcribes to text using `speech_recognition`
- Parses transcript to extract:
  - Product name (e.g., "टमाटर" → "Tomatoes")
  - Quantity (e.g., "1 किलो" → 1 kg)
  - Amount (calculated from product price × quantity)
  - Transaction type (credit/sale)

### 2. API Request

**Endpoint:** `POST http://localhost:5000/api/transactions`

**Request Body:**
```json
{
  "transcript": "1 किलो टमाटर उधार दे दो",
  "type": "credit",
  "amount": 5000,  // in paise (₹50.00)
  "customer_id": "cust_demo",
  "shopkeeper_id": "shop_demo",
  "customer_confirmed": true,
  "language": "hi-IN",
  "product": "Tomatoes",
  "quantity": 1.0,
  "unit": "kg",
  "price": 50.00
}
```

### 3. Backend Processing (`create_transaction_with_verification`)

**What happens:**
1. ✅ Validates shopkeeper and customer exist
2. ✅ Generates shopkeeper history for fraud detection
3. ✅ Runs verification service:
   - Generates SHA256 hash of transcript
   - Performs fraud detection checks
   - Determines if transaction should go to blockchain
4. ✅ Creates transaction in MongoDB with:
   - `status`: 'verified' (if passed checks)
   - `transcript_hash`: SHA256 hash
   - `verification_status`: 'verified'/'flagged'/'pending'
   - `fraud_score`: 0-100
   - `fraud_risk_level`: 'low'/'medium'/'high'/'critical'

### 4. Blockchain Write

**If verification passes:**
```python
blockchain_service.record_transaction(
    voice_hash=transcript_hash,      # SHA256 of transcript
    shop_address=shopkeeper.wallet_address,
    amount=5000,                      # in paise
    tx_type=1                         # 1=CREDIT, 0=SALE, 2=REPAY
)
```

**Blockchain stores:**
- ✅ `voiceHash`: SHA256 hash of transcript
- ✅ `amount`: Transaction amount (in paise)
- ✅ `txType`: Transaction type (0/1/2)
- ✅ `shopAddress`: Shopkeeper's Ethereum address
- ✅ `timestamp`: Block timestamp

**Transaction updated with:**
- `blockchain_tx_id`: Transaction hash from blockchain
- `blockchain_block_number`: Block number where transaction was recorded

### 5. Admin Dashboard Display

**Endpoint:** `GET /api/admin/blockchain-logs`

**What it shows:**
- All transactions with `status` in `['verified', 'completed']`
- Transactions with `blockchain_tx_id` are marked as **blockchain-verified**
- Transactions without `blockchain_tx_id` show as **pending_blockchain**

**Response Format:**
```json
{
  "logs": [
    {
      "id": "transaction_id",
      "type": "credit",
      "amount": 5000,
      "shopkeeper_name": "Demo Shop",
      "customer_name": "Demo Customer",
      "timestamp": "2024-01-15T10:30:00",
      "transaction_hash": "0xabc123...",  // blockchain_tx_id
      "block_number": 12345,
      "status": "verified",
      "has_blockchain_record": true,
      "transcript_hash": "sha256_hash..."
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 150
  }
}
```

## Verification Checklist

### ✅ Voice Input → API
- [x] Voice demo captures audio
- [x] Speech-to-text transcribes correctly
- [x] Product name extracted (Hindi → English)
- [x] Quantity extracted (kg, gram, piece, etc.)
- [x] Price looked up from database or demo prices
- [x] Amount calculated (price × quantity)
- [x] Transaction data sent to `/api/transactions`

### ✅ API → Database
- [x] Transaction created in MongoDB
- [x] Transcript hash generated (SHA256)
- [x] Verification status set
- [x] Fraud detection performed
- [x] Transaction status set to 'verified' (if passed)

### ✅ Database → Blockchain
- [x] Blockchain service initialized
- [x] Transaction written to blockchain (if verified)
- [x] `blockchain_tx_id` stored in database
- [x] `blockchain_block_number` stored in database

### ✅ Blockchain → Admin Dashboard
- [x] `/api/admin/blockchain-logs` endpoint exists
- [x] Shows transactions with `status='verified'`
- [x] Displays `blockchain_tx_id` if available
- [x] Shows transaction details (amount, type, shopkeeper, customer)
- [x] Pagination support

## Testing the Complete Flow

### 1. Start Backend Server
```bash
cd helloKittyFanclub\backend
python run.py
```
Server should be running on `http://localhost:5000`

### 2. Start Blockchain (if using local Hardhat)
```bash
cd helloKittyFanclub\backend\blockchain
npm run deploy:localhost
```

### 3. Run Voice Demo
```bash
cd helloKittyFanclub\backend\blockchain
python voice_demo.py
```

**Say:** "1 किलो टमाटर उधार दे दो"

**Expected Output:**
```
✅ Found product in database: Tomatoes @ ₹50.00/kg
💰 Calculated amount: 1.0 kg × ₹50.00 = ₹50.00

✅ TRANSACTION CREATED!
   Transaction ID: 507f1f77bcf86cd799439011
   Status: verified

✅ VERIFICATION COMPLETE!
   Verification Status: verified

⛓️  BLOCKCHAIN WRITE SUCCESS!
   TX Hash: 0xabc123...
   Block Number: 12345

✅ This transaction is now visible in Admin Dashboard → Blockchain Logs!
```

### 4. Check Admin Dashboard

1. Open admin dashboard: `http://localhost:3000` (or your frontend URL)
2. Navigate to **Blockchain Logs** page
3. You should see:
   - Transaction with amount ₹50.00
   - Type: credit
   - Shopkeeper: Demo Shop
   - Transaction Hash: `0xabc123...`
   - Block Number: 12345
   - Status: verified

## Troubleshooting

### Transaction not appearing in blockchain logs?

1. **Check transaction status:**
   ```python
   # In MongoDB
   Transaction.objects(id="transaction_id").first().status
   # Should be 'verified' or 'completed'
   ```

2. **Check blockchain write:**
   ```python
   # In MongoDB
   Transaction.objects(id="transaction_id").first().blockchain_tx_id
   # Should have a transaction hash if written to blockchain
   ```

3. **Check API response:**
   - Look for `blockchain_tx_id` in verification response
   - If missing, blockchain write may have failed

4. **Check blockchain service:**
   - Ensure blockchain is running
   - Check `.env` has correct blockchain config
   - Verify shopkeeper has `wallet_address` set

### Transaction created but not in blockchain?

- Transaction may be in `pending` status (fraud check failed)
- Check `verification_status` field
- Check `fraud_score` and `fraud_risk_level`
- High fraud scores prevent blockchain write

## Summary

✅ **Complete Integration:** Voice → API → Database → Blockchain → Admin Dashboard

When you say a transaction through voice:
1. ✅ It creates a transaction in the database
2. ✅ It writes to blockchain (if verified)
3. ✅ It appears in Admin Dashboard → Blockchain Logs

The transaction is **immediately visible** in the admin dashboard's blockchain logs page!

