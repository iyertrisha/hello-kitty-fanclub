# Kirana Ledger Blockchain - Setup Guide

Complete setup guide for the Kirana Store Management System blockchain layer.

## Prerequisites

Before you begin, ensure you have:

- ✅ Node.js installed (v18 or higher)
- ✅ Python installed (v3.9 or higher)
- ✅ MetaMask wallet created
- ✅ Polygon Amoy testnet added to MetaMask
- ✅ Test MATIC obtained from faucet: https://faucet.polygon.technology/

---

## Step-by-Step Setup

### Step 1: Install Node.js Dependencies

Navigate to the blockchain directory and install dependencies:

```powershell
cd whackiest\backend\blockchain
npm install
```

This will install Hardhat and all required Ethereum development tools.

---

### Step 2: Create Environment File

Create a `.env` file from the template:

```powershell
Copy-Item env.template -Destination .env
```

Edit the `.env` file and fill in your details:

```env
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your_wallet_private_key_here
ADMIN_ADDRESS=your_wallet_address_here
CONTRACT_ADDRESS=
```

**⚠️ IMPORTANT:** Never commit your `.env` file! It contains your private key.

**To get your private key from MetaMask:**
1. Open MetaMask
2. Click the three dots menu
3. Select "Account details"
4. Click "Show private key"
5. Enter your password
6. Copy the private key (without the 0x prefix)

---

### Step 3: Compile the Smart Contract

Compile the Solidity contract:

```powershell
npm run compile
```

This creates the compiled contract and ABI in the `artifacts/` directory.

---

### Step 4: Copy ABI File

Copy the compiled ABI to the `abis/` directory for Python to use:

```powershell
Copy-Item artifacts\contracts\KiranaLedger.sol\KiranaLedger.json -Destination abis\KiranaLedger.json
```

---

### Step 5: Test on Local Network (Optional but Recommended)

#### 5a. Start Local Hardhat Node

In a **new PowerShell terminal**, start the local blockchain:

```powershell
cd whackiest\backend\blockchain
npm run node
```

Keep this terminal running. You'll see 20 test accounts with private keys.

#### 5b. Deploy to Localhost

In your **original terminal**, deploy the contract:

```powershell
npm run deploy:localhost
```

You should see output like:

```
✅ Deployment successful!
═══════════════════════════════════════════════════
Contract Name:    KiranaLedger
Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3
Deployer Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Network:          localhost
Chain ID:         1337
═══════════════════════════════════════════════════
```

**Copy the Contract Address** and update your `.env` file:

```env
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
RPC_URL=http://localhost:8545
```

---

### Step 6: Install Python Dependencies

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

Or if you prefer using a virtual environment:

```powershell
# Create virtual environment
python -m venv venv

# Activate it (PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

### Step 7: Test the Python Service

Run the test script to verify everything works:

```powershell
python test_blockchain.py
```

You should see output like:

```
🧪 KIRANA LEDGER BLOCKCHAIN TEST
═══════════════════════════════════════════════════════
✅ Configuration validated
📡 Connecting to blockchain...
✅ Connected to blockchain at http://localhost:8545
✅ Service initialized successfully

💰 Account Balance:
   0xf39F...266: 10000.0000 ETH

📝 Test 1: Check Registration Status
   Already registered: False

📝 Test 2: Register Shopkeeper
   ✅ Registration successful!
   Transaction: 0x1234...
   Block: 1

...

🎉 ALL TESTS COMPLETED!
```

---

### Step 8: Deploy to Polygon Amoy Testnet (Production)

Once local testing is successful, deploy to the real testnet:

#### 8a. Get Test MATIC

Visit the Polygon Amoy faucet and get test MATIC:
- Faucet: https://faucet.polygon.technology/
- Enter your wallet address
- Select "Polygon Amoy"
- Request test MATIC

#### 8b. Update .env for Polygon Amoy

Update your `.env` file:

```env
RPC_URL=https://rpc-amoy.polygon.technology
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your_wallet_private_key_here
ADMIN_ADDRESS=your_wallet_address_here
CONTRACT_ADDRESS=
```

#### 8c. Deploy to Polygon Amoy

```powershell
npm run deploy:polygonAmoy
```

This will deploy to the real testnet. **Save the contract address!**

Update your `.env` with the new contract address:

```env
CONTRACT_ADDRESS=0x1234567890abcdef...
```

#### 8d. Verify on PolygonScan

Check your contract on the blockchain explorer:
- PolygonScan Amoy: https://amoy.polygonscan.com/
- Search for your contract address

#### 8e. Test Python Service on Amoy

Run the test script again to verify it works on Amoy:

```powershell
python test_blockchain.py
```

---

## Quick Reference - Common Commands

### Hardhat Commands

```powershell
# Compile contracts
npm run compile

# Run local node (in separate terminal)
npm run node

# Deploy to localhost
npm run deploy:localhost

# Deploy to Polygon Amoy
npm run deploy:polygonAmoy

# Clean compiled files
npx hardhat clean
```

### Python Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_blockchain.py
```

### File Management

```powershell
# Copy ABI file
Copy-Item artifacts\contracts\KiranaLedger.sol\KiranaLedger.json -Destination abis\KiranaLedger.json

# Create .env file
Copy-Item env.template -Destination .env
```

---

## Troubleshooting

### Problem: "npm: command not found"

**Solution:** Install Node.js from https://nodejs.org/

### Problem: "python: command not found"

**Solution:** Install Python from https://www.python.org/

### Problem: "Compilation failed"

**Solutions:**
1. Delete `node_modules` and run `npm install` again
2. Clear cache: `npx hardhat clean`
3. Check Solidity version in `hardhat.config.js` matches contract

### Problem: "Deployment failed - insufficient funds"

**Solution:** Get more test MATIC from the faucet: https://faucet.polygon.technology/

### Problem: "Python service can't find ABI"

**Solution:** Make sure you copied the ABI file:
```powershell
Copy-Item artifacts\contracts\KiranaLedger.sol\KiranaLedger.json -Destination abis\KiranaLedger.json
```

### Problem: "Configuration validation failed"

**Solution:** Check your `.env` file has all required fields:
- PRIVATE_KEY
- CONTRACT_ADDRESS
- ADMIN_ADDRESS

### Problem: "Connection failed" when running Python tests

**Solutions:**
1. If testing on localhost, make sure `npm run node` is running
2. Check RPC_URL in `.env` is correct
3. Check your internet connection (for Polygon Amoy)

---

## File Structure

After setup, your directory should look like:

```
whackiest/backend/blockchain/
├── contracts/
│   └── KiranaLedger.sol          ✅ Smart contract
├── scripts/
│   └── deploy.js                  ✅ Deployment script
├── abis/
│   ├── README.md
│   └── KiranaLedger.json          ✅ Contract ABI (after compilation)
├── utils/
│   ├── __init__.py
│   └── contract_service.py        ✅ Python Web3 service
├── artifacts/                     (Generated by Hardhat)
├── cache/                         (Generated by Hardhat)
├── config.py                      ✅ Configuration
├── hardhat.config.js              ✅ Hardhat config
├── package.json                   ✅ Node dependencies
├── requirements.txt               ✅ Python dependencies
├── test_blockchain.py             ✅ Test script
├── env.template                   ✅ Environment template
├── .env                           ✅ Your environment (not committed)
├── .gitignore                     ✅ Git ignore file
├── SETUP_GUIDE.md                 📖 This file
└── deployed_address.json          (Generated after deployment)
```

---

## Next Steps

After successfully setting up the blockchain layer:

1. ✅ Smart contract is deployed
2. ✅ Python service can interact with the contract
3. ✅ All tests pass

You can now build the upper layers:
- REST API endpoints
- MongoDB integration
- ML credit scoring
- WhatsApp integration
- Frontend applications

---

## Resources

- **Hardhat Documentation:** https://hardhat.org/docs
- **Web3.py Documentation:** https://web3py.readthedocs.io/
- **Polygon Documentation:** https://docs.polygon.technology/
- **Polygon Amoy Faucet:** https://faucet.polygon.technology/
- **Polygon Amoy Explorer:** https://amoy.polygonscan.com/
- **Ethers.js Documentation:** https://docs.ethers.org/v6/

---

## Security Notes

⚠️ **NEVER commit your `.env` file!**

⚠️ **NEVER share your private key!**

⚠️ **Use test networks for development!**

⚠️ **Keep your MetaMask seed phrase safe!**

---

**Need help?** Check the troubleshooting section or review the blockchain implementation checklist.



