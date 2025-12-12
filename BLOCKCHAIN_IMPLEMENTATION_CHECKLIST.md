# Blockchain Implementation Checklist

**Project:** Kirana Store Management System  
**Location:** `whackiest/backend/blockchain/`  
**Reference:** Adapted from `herbiproof/` blockchain pattern  
**Network:** Polygon Amoy Testnet (ChainID: 80002)

---

## Prerequisites

- [ ] Node.js installed (v18+)
- [ ] Python installed (v3.9+)
- [ ] MetaMask wallet created
- [ ] Polygon Amoy testnet added to MetaMask
- [ ] Test MATIC obtained from faucet: https://faucet.polygon.technology/
- [ ] Private key exported from MetaMask (for deployment)

---

## Phase 1: Smart Contract Development

### File: `whackiest/backend/blockchain/contracts/KiranaLedger.sol`

**Reference:** `herbiproof/contracts/cropToken.sol`

- [ ] Create `KiranaLedger.sol` file
- [ ] Add SPDX license and pragma (Solidity ^0.8.20)
- [ ] Define enums:
  - [ ] `TransactionType` enum (SALE=0, CREDIT=1, REPAY=2)
- [ ] Define structs:
  - [ ] `Transaction` struct (id, shopAddress, amount, timestamp, txType, voiceHash)
  - [ ] `CreditScoreData` struct (shopAddress, totalSales, creditGiven, creditRepaid, txFrequency, lastUpdated)
  - [ ] `Cooperative` struct (id, name, termsHash, revenueSplitPercent)
- [ ] Define mappings:
  - [ ] `transactions` mapping (uint256 => Transaction)
  - [ ] `registeredShopkeepers` mapping (address => bool)
  - [ ] `shopkeeperCreditScores` mapping (address => CreditScoreData)
  - [ ] `cooperatives` mapping (uint256 => Cooperative)
  - [ ] `cooperativeMembers` mapping (uint256 => mapping(address => bool))
  - [ ] `nextTransactionId` counter variable
- [ ] Define events:
  - [ ] `ShopkeeperRegistered(address shopAddress)`
  - [ ] `TransactionRecorded(uint256 id, address shopAddress, bytes32 voiceHash, uint256 amount, uint8 txType)`
  - [ ] `BatchTransactionRecorded(uint256 id, address shopAddress, bytes32 batchHash, uint256 totalAmount)`
  - [ ] `CreditScoreUpdated(address shopAddress, uint256 totalSales, uint256 creditGiven)`
  - [ ] `CooperativeCreated(uint256 id, string name)`
  - [ ] `ShopkeeperJoinedCooperative(uint256 coopId, address shopAddress)`
- [ ] Implement functions:
  - [ ] `registerShopkeeper()` - Register shopkeeper address
  - [ ] `recordTransaction(bytes32 voiceHash, address shopAddress, uint256 amount, uint8 txType)` - Record single transaction
  - [ ] `recordBatchTransactions(bytes32 batchHash, address shopAddress, uint256 totalAmount)` - Record daily batch
  - [ ] `getTransaction(uint256 txId)` - Read transaction data
  - [ ] `updateCreditScoreData(address shopAddress, CreditScoreData memory data)` - Update credit scores
  - [ ] `getCreditScore(address shopAddress)` - Read credit score
  - [ ] `createCooperative(uint256 coopId, string memory name, bytes32 termsHash, uint256 splitPercent)` - Create cooperative (admin only)
  - [ ] `joinCooperative(uint256 coopId, address shopAddress)` - Join cooperative
  - [ ] `getCooperativeMembers(uint256 coopId)` - Get cooperative members
- [ ] Add modifiers:
  - [ ] `onlyRegistered()` modifier
  - [ ] `onlyAdmin()` modifier (optional)

---

## Phase 2: Hardhat Setup

### File: `whackiest/backend/blockchain/hardhat.config.js`

**Reference:** `herbiproof/hardhat.config.js`

- [ ] Create `hardhat.config.js` file
- [ ] Import required packages:
  - [ ] `@nomicfoundation/hardhat-toolbox`
  - [ ] `@nomicfoundation/hardhat-ethers`
  - [ ] `dotenv/config`
- [ ] Configure solidity version (0.8.20)
- [ ] Enable optimizer (200 runs)
- [ ] Configure networks:
  - [ ] `hardhat` network (chainId: 1337)
  - [ ] `localhost` network (http://127.0.0.1:8545, chainId: 1337)
  - [ ] `polygonAmoy` network (RPC URL, chainId: 80002, accounts from PRIVATE_KEY)
- [ ] Configure paths:
  - [ ] sources: "./contracts"
  - [ ] tests: "./test"
  - [ ] cache: "./cache"
  - [ ] artifacts: "./artifacts"

### File: `whackiest/backend/blockchain/package.json`

**Reference:** `herbiproof/package.json`

- [ ] Create `package.json` file
- [ ] Set project name: "kirana-blockchain"
- [ ] Set type: "module"
- [ ] Add scripts:
  - [ ] `compile`: "hardhat compile"
  - [ ] `test`: "hardhat test"
  - [ ] `deploy`: "hardhat run scripts/deploy.js"
  - [ ] `deploy:localhost`: "hardhat run scripts/deploy.js --network localhost"
  - [ ] `deploy:polygonAmoy`: "hardhat run scripts/deploy.js --network polygonAmoy"
  - [ ] `node`: "hardhat node"
- [ ] Add devDependencies (same versions as herbiproof):
  - [ ] `@nomicfoundation/hardhat-chai-matchers`: "^2.0.0"
  - [ ] `@nomicfoundation/hardhat-ethers`: "^3.1.0"
  - [ ] `@nomicfoundation/hardhat-network-helpers`: "^1.0.0"
  - [ ] `@nomicfoundation/hardhat-toolbox`: "^4.0.0"
  - [ ] `@nomicfoundation/hardhat-verify`: "^2.0.0"
  - [ ] `@typechain/ethers-v6`: "^0.5.0"
  - [ ] `@typechain/hardhat`: "^9.0.0"
  - [ ] `@types/chai`: "^4.2.0"
  - [ ] `@types/mocha`: ">=9.1.0"
  - [ ] `chai`: "^4.2.0"
  - [ ] `ethers`: "^6.15.0"
  - [ ] `hardhat`: "^2.26.3"
  - [ ] `hardhat-gas-reporter`: "^1.0.8"
  - [ ] `solidity-coverage`: "^0.8.1"
  - [ ] `typechain`: "^8.3.0"
  - [ ] `typescript`: ">=4.5.0"
- [ ] Add dependencies:
  - [ ] `dotenv`: "^16.6.1"

### Installation

- [ ] Navigate to `whackiest/backend/blockchain/`
- [ ] Run `npm install` to install all dependencies

---

## Phase 3: Deployment Script

### File: `whackiest/backend/blockchain/scripts/deploy.js`

**Reference:** `herbiproof/scripts/deploy.js`

- [ ] Create `deploy.js` file
- [ ] Import hardhat and ethers
- [ ] Implement `main()` function:
  - [ ] Get deployer account (first signer)
  - [ ] Log deployer address and balance
  - [ ] Get contract factory for `KiranaLedger`
  - [ ] Deploy contract
  - [ ] Wait for deployment confirmation
  - [ ] Get deployed contract address
  - [ ] Log deployment summary (contract name, address, deployer, network)
  - [ ] Save contract address to config file (optional)
- [ ] Add error handling (try-catch)
- [ ] Add main execution and error handling at bottom

### Environment Variables

**File:** `whackiest/backend/blockchain/.env`

- [ ] Create `.env` file (do NOT commit this)
- [ ] Add variables:
  ```
  POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
  PRIVATE_KEY=your_wallet_private_key_here
  ADMIN_ADDRESS=your_wallet_address_here
  ```
- [ ] Verify `.env` is in `.gitignore`

### Deployment Steps

- [ ] Compile contract: `npm run compile`
- [ ] Test on localhost:
  - [ ] Start local node: `npm run node` (in separate terminal)
  - [ ] Deploy to localhost: `npm run deploy:localhost`
  - [ ] Verify deployment successful
- [ ] Deploy to Polygon Amoy:
  - [ ] Ensure test MATIC in wallet
  - [ ] Run: `npm run deploy:polygonAmoy`
  - [ ] Save deployed contract address
  - [ ] Verify on PolygonScan Amoy: https://amoy.polygonscan.com/

---

## Phase 4: Python Web3.py Service Layer

### File: `whackiest/backend/blockchain/config.py`

- [ ] Create `config.py` file
- [ ] Import `os` and `dotenv`
- [ ] Load environment variables
- [ ] Define configuration class:
  - [ ] `RPC_URL` (default: http://localhost:8545)
  - [ ] `POLYGON_AMOY_RPC_URL`
  - [ ] `PRIVATE_KEY`
  - [ ] `CONTRACT_ADDRESS` (from deployment)
  - [ ] `ADMIN_ADDRESS`

### File: `whackiest/backend/blockchain/utils/contract_service.py`

**Reference:** `herbiproof/pyScripts/blockchain.py`

- [ ] Create `contract_service.py` file
- [ ] Import required packages:
  - [ ] `web3` from Web3
  - [ ] `json`, `os`, `logging`
  - [ ] Config from `../config.py`
- [ ] Load contract ABI from `../abis/KiranaLedger.json`
- [ ] Create `BlockchainService` class:
  - [ ] `__init__()`: Initialize Web3, load contract, load account
  - [ ] `_validate_address(address)`: Validate Ethereum address
  - [ ] `_handle_transaction(tx_function, *args)`: Generic transaction handler
  - [ ] **Write Methods:**
    - [ ] `register_shopkeeper(address)`: Register shopkeeper
    - [ ] `record_transaction(voice_hash, shop_address, amount, tx_type)`: Record single transaction
    - [ ] `record_batch_transactions(batch_hash, shop_address, total_amount)`: Record batch
    - [ ] `update_credit_score(address, data)`: Update credit scores
    - [ ] `create_cooperative(coop_id, name, terms_hash, split_percent)`: Create cooperative
    - [ ] `join_cooperative(coop_id, shop_address)`: Join cooperative
  - [ ] **Read Methods:**
    - [ ] `get_transaction(tx_id)`: Read transaction
    - [ ] `get_credit_score(address)`: Read credit score
    - [ ] `is_shopkeeper_registered(address)`: Check if registered
    - [ ] `get_cooperative_members(coop_id)`: Get cooperative members
    - [ ] `get_next_transaction_id()`: Get next transaction ID

### Python Requirements

**File:** `whackiest/backend/requirements.txt`

- [ ] Add Python blockchain dependencies:
  ```
  web3>=6.0.0
  python-dotenv>=1.0.0
  ```

---

## Phase 5: ABI Management

### After Compilation

- [ ] Run `npm run compile` in `whackiest/backend/blockchain/`
- [ ] Copy ABI file:
  - [ ] Source: `whackiest/backend/blockchain/artifacts/contracts/KiranaLedger.sol/KiranaLedger.json`
  - [ ] Destination: `whackiest/backend/blockchain/abis/KiranaLedger.json`
- [ ] Verify ABI file exists and is valid JSON

---

## Phase 6: Testing

### Hardhat Local Testing

- [ ] Start local Hardhat node: `npm run node`
- [ ] Deploy contract: `npm run deploy:localhost`
- [ ] Note contract address
- [ ] Update `.env` with local contract address

### Python Service Testing

- [ ] Create test script: `whackiest/backend/blockchain/test_blockchain.py`
- [ ] Import `BlockchainService`
- [ ] Test connection to blockchain
- [ ] Test registering shopkeeper
- [ ] Test recording transaction
- [ ] Test reading transaction
- [ ] Test batch recording
- [ ] Test credit score update
- [ ] Verify all functions work correctly

### Polygon Amoy Testing

- [ ] Deploy to Polygon Amoy: `npm run deploy:polygonAmoy`
- [ ] Update `.env` with Amoy contract address
- [ ] Update `RPC_URL` to Polygon Amoy RPC
- [ ] Run Python service tests against Amoy
- [ ] Verify transactions on PolygonScan Amoy

---

## Phase 7: Documentation

- [ ] Document contract address (save to `CONTRACT_ADDRESS.txt`)
- [ ] Document deployment transaction hash
- [ ] Document contract functions and their usage
- [ ] Create README in `whackiest/backend/blockchain/README.md`:
  - [ ] Contract overview
  - [ ] Deployment instructions
  - [ ] Usage examples
  - [ ] Network details (Polygon Amoy)
  - [ ] Links to PolygonScan

---

## Final Checklist

- [ ] Smart contract compiled successfully
- [ ] Contract deployed to Polygon Amoy testnet
- [ ] Contract address saved in `.env`
- [ ] Python Web3.py service layer created
- [ ] BlockchainService class tested and working
- [ ] ABI file copied to `abis/` folder
- [ ] All read/write methods implemented
- [ ] Transaction handling works correctly
- [ ] Error handling implemented
- [ ] Documentation completed

---

## Next Steps (After Blockchain Layer)

Once blockchain layer is complete, the following will be built on top:

- REST API endpoints (`whackiest/backend/api/routes/`)
- MongoDB models (`whackiest/backend/database/models.py`)
- ML credit scoring (`whackiest/backend/ml/`)
- WhatsApp integration (`whackiest/backend/integrations/whatsapp/`)
- Frontend applications (`whackiest/frontend/`)

---

## File Structure Summary

After completion, the blockchain folder structure should look like:

```
whackiest/backend/blockchain/
├── contracts/
│   └── KiranaLedger.sol          ✅ Smart contract
├── scripts/
│   └── deploy.js                  ✅ Deployment script
├── abis/
│   └── KiranaLedger.json          ✅ Contract ABI
├── utils/
│   └── contract_service.py        ✅ Python Web3 service
├── config.py                       ✅ Configuration
├── hardhat.config.js               ✅ Hardhat config
├── package.json                    ✅ Node dependencies
├── .env                            ✅ Environment variables (not committed)
├── .gitignore                      ✅ Git ignore file
├── README.md                       ✅ Documentation
├── test_blockchain.py              ✅ Test script
├── artifacts/                      (Generated by Hardhat)
└── cache/                          (Generated by Hardhat)
```

---

## Troubleshooting

### Common Issues

1. **Compilation fails:**
   - Check Solidity version matches (^0.8.20)
   - Run `npm install` again
   - Clear cache: `npx hardhat clean`

2. **Deployment fails:**
   - Check wallet has test MATIC
   - Verify private key in `.env`
   - Check RPC URL is correct
   - Try increasing gas limit

3. **Python service can't connect:**
   - Verify contract address in `.env`
   - Check RPC URL is accessible
   - Verify ABI file exists and is correct
   - Check Web3.py version (>=6.0.0)

4. **Transaction fails:**
   - Check account has sufficient gas
   - Verify function parameters are correct
   - Check address is registered (if required)
   - Review contract requires/assertions

---

## Resources

- Hardhat Documentation: https://hardhat.org/docs
- Web3.py Documentation: https://web3py.readthedocs.io/
- Polygon Documentation: https://docs.polygon.technology/
- Polygon Amoy Faucet: https://faucet.polygon.technology/
- Polygon Amoy Explorer: https://amoy.polygonscan.com/
- Ethers.js v6 Documentation: https://docs.ethers.org/v6/

---

**Note:** This checklist covers ONLY the blockchain layer. All other components (APIs, ML, frontend) will be built on top of this foundation.



