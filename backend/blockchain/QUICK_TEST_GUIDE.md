# Quick Test Guide for Voice Demo

## Step-by-Step Testing

### Step 1: Start Test API (Terminal 1)

```powershell
cd helloKittyFanclub\backend\blockchain
python test_api.py
```

**Expected output:**
```
✅ Blockchain service initialized
🚀 Starting server on http://localhost:5001
```

**Keep this terminal running!**

---

### Step 2: Test the API (Terminal 2)

**Option A: Run test script**
```powershell
cd helloKittyFanclub\backend\blockchain
python test_voice_demo.py
```

**Option B: Manual test with curl**
```powershell
# Test health
curl http://localhost:5001/test/health

# Test transaction creation
curl -X POST http://localhost:5001/test/transactions `
  -H "Content-Type: application/json" `
  -d '{\"transcript\": \"राहुल को 500 रुपये का उधार दे दो\", \"type\": \"credit\", \"amount\": 50000, \"customer_id\": \"cust_001\", \"shopkeeper_id\": \"shop_demo\", \"customer_confirmed\": true, \"language\": \"hi-IN\"}'
```

---

### Step 3: Run Voice Demo (Terminal 3)

```powershell
cd helloKittyFanclub\backend\blockchain
python voice_demo.py
```

**Select option 2** (Manual input) for testing:
1. Enter transcript: `राहुल को 500 रुपये का उधार दे दो`
2. Confirm (type `y`)
3. Watch for blockchain write confirmation

---

## What to Look For

### ✅ Success Indicators:

1. **API Running:**
   ```
   ✅ API is running
   ✅ Blockchain available
   ```

2. **Transaction Created:**
   ```
   ✅ TRANSACTION VERIFIED!
   Status: verified
   Storage: blockchain
   ```

3. **Blockchain Write:**
   ```
   ⛓️  BLOCKCHAIN WRITE SUCCESS!
   TX Hash: 0xabc123...
   Block: 12345
   Gas Used: 145830
   ```

---

## Troubleshooting

### "Cannot connect to API"
- Make sure `test_api.py` is running in Terminal 1
- Check: `curl http://localhost:5001/test/health`

### "Blockchain service not available"
- Check `.env` file has `CONTRACT_ADDRESS` and `PRIVATE_KEY`
- Or it will run in mock mode (database only)

### "Blockchain write attempted but no result"
- Check blockchain connection: `curl http://localhost:5001/test/blockchain/status`
- Verify contract is deployed
- Check RPC URL is correct

---

## Quick Test Commands

```powershell
# 1. Start API
cd helloKittyFanclub\backend\blockchain
python test_api.py

# 2. In another terminal, test
python test_voice_demo.py

# 3. Or run voice demo
python voice_demo.py
```

---

## Expected Flow

1. **Voice/Text Input** → Transcript captured
2. **Parse** → Extract amount, customer, type
3. **Send to API** → `POST /test/transactions`
4. **Verify** → Fraud check, validation
5. **Blockchain Write** → If verified, write to blockchain
6. **Return Result** → TX hash, block number, status

---

## Success = All Steps Complete! 🎉

