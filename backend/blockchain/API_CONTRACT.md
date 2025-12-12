# API Contract - React Native Voice STT Integration

## Overview

This document defines the API contract for integrating react-native-voice (on-device STT) with the Kirana Store backend. The frontend sends **text transcripts** (not audio files) to the backend for verification and blockchain storage.

## Architecture

```
React Native App → react-native-voice → Text Transcript → Backend API → Verification → Blockchain
```

**Key Change:** No Google Speech API needed. Transcription happens on-device using react-native-voice.

---

## API Endpoints

### 1. Create Transaction

**Endpoint:** `POST /api/transactions`

**Description:** Create a new transaction from voice transcript.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>  (if authentication enabled)
```

**Request Body:**
```json
{
  "transcript": "मुझे 500 रुपये का क्रेडिट चाहिए",
  "type": "credit",
  "amount": 50000,
  "customer_id": "customer_123",
  "shopkeeper_id": "shopkeeper_456",
  "customer_confirmed": true,
  "language": "hi-IN"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transcript` | string | ✅ | Text from react-native-voice |
| `type` | string | ✅ | Transaction type: `credit`, `sale`, `repay` |
| `amount` | integer | ✅ | Amount in **paise** (₹500 = 50000) |
| `customer_id` | string | ✅ | Customer identifier |
| `shopkeeper_id` | string | ✅ | Shopkeeper identifier |
| `customer_confirmed` | boolean | ❌ | WhatsApp confirmation status (default: false) |
| `language` | string | ❌ | Language code (default: `hi-IN`) |
| `product` | string | ❌ | Product name (for sales) |
| `quantity` | integer | ❌ | Quantity (for sales, default: 1) |

**Response (201 Created):**
```json
{
  "success": true,
  "transaction_id": "tx_20251212143052",
  "verification": {
    "status": "verified",
    "storage_location": "blockchain",
    "transcript_hash": "a1b2c3d4e5f6...",
    "should_write_to_blockchain": true,
    "errors": [],
    "warnings": []
  },
  "fraud_check": {
    "is_flagged": false,
    "risk_level": "low",
    "score": 0.15,
    "reasons": [],
    "recommendations": []
  },
  "metadata": {
    "language": "hi-IN",
    "amount": 50000,
    "customer_id": "customer_123",
    "verified_at": "2025-12-12T14:30:52.123Z"
  },
  "blockchain": {
    "success": true,
    "tx_hash": "0xabc123...",
    "block_number": 12345,
    "gas_used": 145830
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Validation failed",
  "details": ["Amount must be greater than 0", "Invalid customer ID"]
}
```

---

### 2. Verify Transaction (Direct)

**Endpoint:** `POST /api/verify-transaction`

**Description:** Verify a transaction without creating it (for preview/testing).

**Request Body:** Same as Create Transaction

**Response:**
```json
{
  "status": "verified",
  "storage_location": "blockchain",
  "transcript_hash": "a1b2c3d4e5f6...",
  "should_write_to_blockchain": true,
  "fraud_check": {...},
  "errors": [],
  "warnings": []
}
```

---

### 3. Get Transaction

**Endpoint:** `GET /api/transactions/:id`

**Response:**
```json
{
  "id": "tx_20251212143052",
  "type": "credit",
  "amount": 50000,
  "customer_id": "customer_123",
  "shopkeeper_id": "shopkeeper_456",
  "status": "verified",
  "transcript_hash": "a1b2c3d4e5f6...",
  "blockchain_tx_id": "0xabc123...",
  "created_at": "2025-12-12T14:30:52.123Z"
}
```

---

## Verification Flow

### Credit Transactions

```
1. Calculate SHA256 hash of transcript
2. Run fraud detection checks:
   - Amount vs average daily sales
   - Credit frequency per day
   - Customer purchase history
   - Transaction timing
3. Check customer confirmation status
4. Decision:
   ✅ All pass + confirmed → BLOCKCHAIN
   ⚠️ Pass but no confirmation → DATABASE (pending)
   ❌ Any check fails → DATABASE (flagged)
```

### Sales Transactions

```
1. Calculate SHA256 hash of transcript
2. Validate product, price, quantity
3. Background anomaly detection
4. Write to DATABASE immediately
5. End-of-day: Aggregate and write to BLOCKCHAIN
```

---

## Verification Status Values

| Status | Description | Storage Location |
|--------|-------------|------------------|
| `verified` | All checks passed | Blockchain |
| `pending` | Awaiting customer confirmation | Database (pending) |
| `flagged` | Anomaly detected | Database (flagged) |
| `rejected` | Validation failed | Not stored |

---

## Risk Levels

| Level | Score Range | Action |
|-------|-------------|--------|
| `low` | 0.0 - 0.29 | Auto-approve (may need confirmation for high amounts) |
| `medium` | 0.3 - 0.49 | Requires customer confirmation |
| `high` | 0.5 - 0.69 | Manual review required |
| `critical` | 0.7 - 1.0 | Rejected, flagged for investigation |

---

## Supported Languages

| Code | Language |
|------|----------|
| `hi-IN` | Hindi (India) |
| `en-IN` | English (India) |
| `mr-IN` | Marathi (India) |
| `gu-IN` | Gujarati (India) |

---

## Amount Format

**All amounts are in paise (1/100 of a rupee).**

| Rupees | Paise (API value) |
|--------|-------------------|
| ₹10 | 1000 |
| ₹100 | 10000 |
| ₹500 | 50000 |
| ₹1,000 | 100000 |
| ₹10,000 | 1000000 |

---

## React Native Integration

### Using react-native-voice

```javascript
import Voice from '@react-native-voice/voice';

// Start listening
Voice.start('hi-IN');

// Get transcript
Voice.onSpeechResults = (event) => {
  const transcript = event.value[0];
  
  // Send to backend
  fetch('/api/transactions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transcript: transcript,
      type: 'credit',
      amount: parsedAmount,  // Parse from transcript
      customer_id: customerId,
      shopkeeper_id: shopkeeperId,
      language: 'hi-IN'
    })
  });
};
```

### Example Flow

```javascript
// 1. User speaks: "राहुल को 500 रुपये का उधार"
// 2. react-native-voice transcribes on-device
// 3. App parses amount and customer name
// 4. App sends transcript to backend
// 5. Backend verifies and writes to blockchain
// 6. App shows confirmation
```

---

## Test Endpoints (Development Only)

These endpoints are available on the test API (port 5001):

| Endpoint | Description |
|----------|-------------|
| `GET /test/health` | Health check |
| `POST /test/transactions` | Create transaction |
| `POST /test/verify-transaction` | Verify transaction |
| `GET /test/blockchain/status` | Blockchain status |
| `GET /test/mock/credit` | Get mock credit data |
| `GET /test/mock/sale` | Get mock sale data |
| `GET /test/mock/transcripts` | Sample transcripts |

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing token |
| 404 | Not Found - Transaction not found |
| 500 | Server Error - Internal error |
| 503 | Service Unavailable - Blockchain not connected |

---

## Sample Transcripts for Testing

### Hindi Credit
- "राहुल को 500 रुपये का उधार दे दो"
- "प्रिया को 200 रुपये का क्रेडिट"
- "अमित को 1000 रुपये उधार"

### English Credit
- "Give 500 rupees credit to Rahul"
- "Credit 200 rupees to Priya"
- "Give Amit 1000 rupees udhar"

### Hindi Sale
- "2 किलो चावल 120 रुपये"
- "1 लीटर तेल 150 रुपये"
- "मैगी 14 रुपये"

### English Sale
- "2 kg rice 120 rupees"
- "1 liter oil 150 rupees"
- "Maggie 14 rupees"

---

## Contact

For API integration questions, contact the backend team (Vineet for Flask API).

