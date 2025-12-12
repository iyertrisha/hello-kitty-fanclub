# Voice Demo Setup Guide

## Quick Start for Hackathon Judges

This guide helps you run a live voice demo where judges can speak and transactions are stored on blockchain.

---

## Prerequisites

1. **Blockchain node running** (Terminal 1)
2. **Test API running** (Terminal 2)
3. **Voice demo script** (Terminal 3)

---

## Step-by-Step Setup

### Step 1: Start Blockchain Node

**Terminal 1:**
```powershell
cd whackiest\backend\blockchain
npm run node
```

Keep this running - it's your local blockchain.

---

### Step 2: Start Test API

**Terminal 2:**
```powershell
cd whackiest\backend\blockchain
python test_api.py
```

You should see:
```
🚀 Starting server on http://localhost:5001
```

Keep this running - it handles verification and blockchain writes.

---

### Step 3: Install Voice Recognition (One-time setup)

**Terminal 3:**
```powershell
pip install speechrecognition pyaudio
```

**Note:** If `pyaudio` installation fails on Windows:
```powershell
pip install pipwin
pipwin install pyaudio
```

---

### Step 4: Run Voice Demo

**Terminal 3:**
```powershell
cd whackiest\backend\blockchain
python voice_demo.py
```

---

## Demo Flow

1. **Judge speaks** → "राहुल को 500 रुपये का उधार दे दो"
2. **Script captures** → Microphone records audio
3. **Transcribes** → Google Speech API converts to text
4. **Parses** → Extracts amount, customer, type
5. **Sends to API** → Backend verifies transaction
6. **Blockchain write** → Transaction stored on blockchain
7. **Shows result** → TX hash, block number, status

---

## What Judges Will See

```
🎤 VOICE INPUT MODE
📢 Speak your transaction:
⏸️  Listening... (speak now)

📝 Transcript: राहुल को 500 रुपये का उधार दे दो

📡 SENDING TO BACKEND
✅ TRANSACTION VERIFIED!
   Status: verified
   Storage: blockchain
   Transcript Hash: a1b2c3d4e5f6...

⛓️  BLOCKCHAIN WRITE SUCCESS!
   TX Hash: 0xabc123...
   Block: 12345
   Gas Used: 145830
```

---

## Demo Scripts for Judges

### Hindi Credit
"राहुल को 500 रुपये का उधार दे दो"
"प्रिया को 200 रुपये का क्रेडिट"

### English Credit
"Give 500 rupees credit to Rahul"
"Credit 200 rupees to Priya"

### Hindi Sale
"2 किलो चावल 120 रुपये"
"मैगी 14 रुपये"

### English Sale
"2 kg rice 120 rupees"
"Maggie 14 rupees"

---

## Troubleshooting

### "Cannot connect to API"
- Make sure `test_api.py` is running (Terminal 2)
- Check if port 5001 is available

### "Speech recognition not available"
- Install: `pip install speechrecognition pyaudio`
- Check microphone permissions

### "No speech detected"
- Speak clearly and wait for "Listening..." message
- Check microphone is working
- Try manual input mode (option 2)

### "Blockchain not connected"
- Make sure `npm run node` is running (Terminal 1)
- Check `.env` file has correct `CONTRACT_ADDRESS`

---

## Alternative: Manual Input Mode

If microphone doesn't work, use manual text input:
1. Select option 2 in the demo
2. Type transcript: "राहुल को 500 रुपये का उधार दे दो"
3. Confirm transaction
4. See blockchain result

---

## Quick Test Commands

```powershell
# Test API is running
curl http://localhost:5001/test/health

# Test blockchain status
curl http://localhost:5001/test/blockchain/status

# Test transaction (manual)
curl -X POST http://localhost:5001/test/transactions `
  -H "Content-Type: application/json" `
  -d '{"transcript": "राहुल को 500 रुपये का उधार", "type": "credit", "amount": 50000, "customer_id": "cust_001", "shopkeeper_id": "shop_001", "customer_confirmed": true, "language": "hi-IN"}'
```

---

## Presentation Tips

1. **Show all 3 terminals** - Judges can see the full flow
2. **Speak clearly** - Use demo scripts above
3. **Explain each step** - Voice → Transcript → Verification → Blockchain
4. **Show blockchain explorer** - If using Polygon Amoy, show transaction on explorer
5. **Demo fraud detection** - Try high amount: "10000 रुपये का उधार" (will flag)

---

## Success Checklist

- [ ] Blockchain node running
- [ ] Test API running
- [ ] Voice demo script running
- [ ] Microphone working
- [ ] Test transaction successful
- [ ] Blockchain TX hash visible

---

## Need Help?

If something doesn't work:
1. Check all 3 terminals are running
2. Verify `.env` file has correct settings
3. Try manual input mode first
4. Check error messages in terminals

Good luck with your hackathon demo! 🚀

