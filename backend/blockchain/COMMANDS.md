# Quick Command Reference - PowerShell

All commands to run in order. Copy and paste these into your PowerShell terminal.

---

## Initial Setup

### 1. Navigate to blockchain directory

```powershell
cd whackiest\backend\blockchain
```

### 2. Install Node.js dependencies

```powershell
npm install
```

### 3. Create .env file

```powershell
Copy-Item env.template -Destination .env
```

**Then manually edit `.env` file with your wallet details**

---

## Compile & Prepare

### 4. Compile smart contract

```powershell
npm run compile
```

### 5. Copy ABI file

```powershell
Copy-Item artifacts\contracts\KiranaLedger.sol\KiranaLedger.json -Destination abis\KiranaLedger.json
```

---

## Local Testing (Recommended)

### 6a. Start local blockchain (NEW TERMINAL - keep running)

```powershell
cd whackiest\backend\blockchain
npm run node
```

### 6b. Deploy to localhost (ORIGINAL TERMINAL)

```powershell
npm run deploy:localhost
```

**Copy the Contract Address from output and add to `.env` file:**
```
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
RPC_URL=http://localhost:8545
```

---

## Python Setup

### 7. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 8. Test Python service

```powershell
python test_blockchain.py
```

---

## Deploy to Polygon Amoy (Production)

### 9. Update .env for Polygon Amoy

Edit `.env` file:
```
RPC_URL=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=
```

### 10. Deploy to Polygon Amoy

```powershell
npm run deploy:polygonAmoy
```

**Copy the Contract Address from output and update `.env` file**

### 11. Test on Polygon Amoy

```powershell
python test_blockchain.py
```

---

## That's it! 🎉

Your blockchain layer is now deployed and tested.

---

## Quick Commands for Daily Use

```powershell
# Recompile after contract changes
npm run compile

# Copy ABI after recompile
Copy-Item artifacts\contracts\KiranaLedger.sol\KiranaLedger.json -Destination abis\KiranaLedger.json

# Run Python tests
python test_blockchain.py

# Clean and rebuild
npx hardhat clean
npm run compile
```

---

## File to Edit

**`.env`** - Add your wallet details:
```
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your_private_key_without_0x
ADMIN_ADDRESS=your_wallet_address
CONTRACT_ADDRESS=will_be_filled_after_deployment
```

Get PRIVATE_KEY from MetaMask:
1. MetaMask → Three dots → Account details
2. Show private key → Enter password
3. Copy (remove 0x prefix if present)

Get Test MATIC:
- Visit: https://faucet.polygon.technology/
- Enter your wallet address
- Request test MATIC

---

## All Done!

Refer to `SETUP_GUIDE.md` for detailed explanations and troubleshooting.



