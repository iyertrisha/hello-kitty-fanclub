# Testing Voice Demo - Complete Guide

This guide helps you test if `voice_demo.py` can successfully create transactions and write them to the blockchain.

## Prerequisites Checklist

Before testing, ensure you have:

- [ ] Backend services available (fraud_detection, transaction_verification)
- [ ] Blockchain configured (CONTRACT_ADDRESS, PRIVATE_KEY in .env)
- [ ] Hardhat node running (optional, for local blockchain)
- [ ] Python dependencies installed

## Step-by-Step Testing

### Step 1: Start Test API

**Terminal 1:**
```powershell
cd helloKittyFanclub\backend\blockchain
python test_api.py
```

You should see:
```
✅ Blockchain service initialized
🚀 Starting server on http://localhost:5001
```

**If you see "Blockchain service not available":**
- Check `.env` file has `CONTRACT_ADDRESS` and `PRIVATE_KEY`
- Or it will run in mock mode (database only, no blockchain)

### Step 2: Run Test Script

**Terminal 2:**
```powershell
cd helloKittyFanclub\backend\blockchain
python test_voice_demo.py
```

This will:
1. ✅ Check if test_api.py is running
2. ✅ Check blockchain connection status
3. ✅ Test credit transaction creation
4. ✅ Test sale transaction creation
5. ✅ Verify blockchain writes

**Expected Output:**
```
🧪 VOICE DEMO TEST SUITE
======================================================================

======================================================================
  TEST 1: API Connection
======================================================================
✅ PASS - API is running
✅ PASS - Blockchain available

======================================================================
  TEST 2: Blockchain Status
======================================================================
✅ PASS - Blockchain connected
   Contract Address: 0x1234567890abcdef...
   Balance: 0.1000 ETH
   Next TX ID: 5

======================================================================
  TEST 3: Credit Transaction Creation
======================================================================
📤 Sending transaction:
   Type: credit
   Amount: ₹500.00
   Customer: cust_001
   Transcript: राहुल को 500 रुपये का उधार दे दो

✅ PASS - Transaction created
✅ PASS - Transaction verified
✅ PASS - Storage location
✅ PASS - Should write to blockchain
✅ PASS - Blockchain write successful

   ⛓️  Blockchain Details:
      TX Hash: 0xabc123...
      Block: 12345
      Gas Used: 145830
```

### Step 3: Run Voice Demo

**Terminal 3:**
```powershell
cd helloKittyFanclub\backend\blockchain
python voice_demo.py
```

**Options:**
1. **Voice input** - Speak into microphone (requires `speechrecognition` and `pyaudio`)
2. **Manual input** - Type transcript directly (recommended for testing)
3. **Show blockchain status** - Check current blockchain state
4. **Exit**

### Step 4: Test with Manual Input

1. Select option **2** (Manual text input)
2. Enter transcript: `राहुल को 500 रुपये का उधार दे दो`
3. Confirm transaction (type `y`)
4. Watch for blockchain write confirmation

**Expected Output:**
```
📡 SENDING TO BACKEND
======================================================================

📤 Sending transaction:
   Type: credit
   Amount: ₹500.00
   Customer: cust_001
   Language: hi-IN

✅ TRANSACTION VERIFIED!
   Status: verified
   Storage: blockchain
   Transcript Hash: a1b2c3d4e5f6...

⛓️  BLOCKCHAIN WRITE SUCCESS!
   TX Hash: 0xabc123...
   Block: 12345
   Gas Used: 145830
```

## Troubleshooting

### Issue: "Cannot connect to API"

**Solution:**
- Make sure `test_api.py` is running in Terminal 1
- Check if port 5001 is available
- Try: `curl http://localhost:5001/test/health`

### Issue: "Blockchain service not available"

**Solution:**
1. Check `.env` file in `backend/` directory:
   ```env
   CONTRACT_ADDRESS=0x...
   PRIVATE_KEY=0x...
   RPC_URL=http://localhost:8545
   ```

2. If using Polygon Amoy:
   ```env
   RPC_URL=https://rpc-amoy.polygon.technology
   CHAIN_ID=80002
   ```

3. If contract not deployed:
   ```powershell
   cd helloKittyFanclub\backend\blockchain
   npm run deploy:localhost
   # Copy CONTRACT_ADDRESS to .env
   ```

### Issue: "Blockchain write attempted but no result"

**Possible causes:**
- Blockchain service not initialized
- Contract address incorrect
- Insufficient balance for gas
- RPC URL incorrect

**Check:**
```powershell
python test_voice_demo.py
# Look at "TEST 2: Blockchain Status"
```

### Issue: "Speech recognition not available"

**Solution:**
```powershell
pip install speechrecognition pyaudio
```

**Windows (if pyaudio fails):**
```powershell
pip install pipwin
pipwin install pyaudio
```

**Note:** You can still test using option 2 (Manual input) without microphone.

## Test Scenarios

### Scenario 1: Credit Transaction (Hindi)
```
Transcript: राहुल को 500 रुपये का उधार दे दो
Expected: Credit transaction, ₹500, writes to blockchain
```

### Scenario 2: Credit Transaction (English)
```
Transcript: Give 500 rupees credit to Rahul
Expected: Credit transaction, ₹500, writes to blockchain
```

### Scenario 3: Sale Transaction (Hindi)
```
Transcript: 2 किलो चावल 120 रुपये
Expected: Sale transaction, ₹120, stored in database
```

### Scenario 4: Sale Transaction (English)
```
Transcript: 2 kg rice 120 rupees
Expected: Sale transaction, ₹120, stored in database
```

## Verification Checklist

After running tests, verify:

- [ ] Test API is running and accessible
- [ ] Blockchain connection is established
- [ ] Credit transactions are created successfully
- [ ] Credit transactions write to blockchain (if verified)
- [ ] Sale transactions are created successfully
- [ ] Transaction hashes are returned
- [ ] Block numbers are returned
- [ ] Gas usage is reported

## Success Criteria

✅ **All tests pass** = voice_demo.py is ready to use

✅ **Blockchain writes working** = Transactions are being stored on blockchain

✅ **API responding** = Backend integration is working

## Next Steps

Once tests pass:

1. **Keep test_api.py running** (Terminal 1)
2. **Run voice_demo.py** (Terminal 2)
3. **Test with voice or manual input**
4. **Verify transactions on blockchain explorer** (if using Polygon Amoy)

## Quick Test Command

```powershell
# One-liner to test everything
cd helloKittyFanclub\backend\blockchain && python test_voice_demo.py
```

## Need Help?

If something doesn't work:
1. Check all error messages
2. Verify `.env` configuration
3. Ensure test_api.py is running
4. Try manual input mode first
5. Check blockchain status endpoint

Good luck! 🚀

