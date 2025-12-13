# Backend Architecture Analysis & Debug Report

**Date:** Generated on analysis
**Status:** 🔴 Critical Issues Found - System Partially Broken

---

## 1️⃣ What the Backend Is Doing

### Entry Point (Server Startup)

The backend has **TWO entry points**, which is confusing:

1. **Main Entry Point (Flask):** `backend/run.py`
   - Uses Flask application factory from `api/__init__.py`
   - Actually calls `database/__init__.py`'s `create_app()` (see line 5 in `api/__init__.py`)
   - Runs on port 5000 (default)
   - Loads config from `config.py`

2. **Alternative Entry Point (FastAPI):** `backend/main.py`
   - FastAPI app for ML credit scoring API
   - Runs on port 8000
   - Uses same MongoDB connection pattern

**Flow:**
```
run.py → api/__init__.py → database/__init__.py → create_app()
  ↓
Flask app created
  ↓
MongoDB connection attempted (synchronous, blocks on failure)
  ↓
Blueprints registered (routes loaded)
  ↓
Server starts on port 5000
```

### API Routes

Routes are organized as Flask blueprints in `api/routes/`:

- `/api/transactions` - Transaction CRUD operations
- `/api/blockchain` - Direct blockchain interactions
- `/api/shopkeeper` - Shopkeeper management
- `/api/customer` - Customer management
- `/api/cooperative` - Cooperative management
- `/api/admin` - Admin operations
- `/api/whatsapp` - WhatsApp bot webhooks
- `/api/debt` - Debt management
- `/api/grocery` - Grocery orders
- `/api/noticeboard` - Notices/announcements
- `/api/supplier` - Supplier portal

### Controllers / Services

**Service Layer Pattern:**
- Business logic in `services/` directory
- Routes call services, services interact with models
- Examples:
  - `services/transaction/transaction_service.py` - Transaction creation, verification, blockchain writes
  - `services/transaction_verification.py` - Fraud detection, verification logic
  - `services/debt/debt_service.py` - Debt entry via WhatsApp

**Transaction Flow:**
```
POST /api/transactions
  ↓
create_transaction_with_verification()
  ↓
TransactionVerificationService.verify() (fraud detection)
  ↓
Transaction saved to MongoDB
  ↓
If verified → BlockchainService.record_transaction() → Polygon Amoy
  ↓
Transaction.blockchain_tx_id updated in MongoDB
```

### Database Interactions (MongoDB)

**Connection:**
- MongoEngine ODM used
- Connection established in `database/__init__.py:38-47` (synchronously)
- URI format: `mongodb://localhost:27017/kirana_db` or MongoDB Atlas SRV
- Database name from `MONGODB_DB_NAME` env var

**Models (MongoEngine Documents):**
- `Shopkeeper` - Shopkeepers with wallet addresses
- `Customer` - Customers with phone numbers
- `Transaction` - All transactions (sale/credit/repay) with blockchain_tx_id
- `Product` - Inventory items
- `Cooperative` - Shopkeeper cooperatives
- `Supplier` - Suppliers
- `PendingConfirmation` - WhatsApp OTP confirmations

**Collections:** Defined in `database/models.py` meta dictionaries

### Blockchain Interactions

**What is Written on-Chain:**
1. **Transaction Records** - When transaction is verified (fraud score low, customer confirmed):
   - Voice hash (SHA256 of transcript)
   - Shop address (Ethereum address)
   - Amount (in wei/paise - smallest unit)
   - Transaction type (0=SALE, 1=CREDIT, 2=REPAY)

2. **Shopkeeper Registration** - When shopkeeper registers
3. **Credit Score Updates** - ML credit scores (optional)
4. **Cooperative Creation/Joining** - Cooperative management

**When Blockchain Writes Happen:**
- Transaction creation: Only if `verification_result.should_write_to_blockchain == True`
- Conditions checked by `TransactionVerificationService._decide_credit_storage()`
- After customer confirmation (WhatsApp flow)

**Which Blockchain:**
- **Target:** Polygon Amoy (testnet)
- **Library:** `web3.py` (version 6.0+)
- **Contract:** KiranaLedger.sol (deployed address in CONTRACT_ADDRESS env var)

**Why Blockchain:**
- Immutable ledger of credit transactions
- Verification hash prevents fraud
- Decentralized trust for shopkeepers

---

## 2️⃣ MongoDB Integration Check

### ✅ Correctly Implemented

1. **Connection Setup:**
   - MongoEngine used correctly
   - Connection in app factory pattern
   - Error handling with try/except

2. **Connection URI:**
   - Supports local MongoDB and Atlas SRV URIs
   - Database name specified separately

3. **Models:**
   - Proper MongoEngine Document classes
   - Indexes defined in meta
   - ReferenceFields for relationships

### ❌ Critical Issues

#### Issue 1: Duplicate `create_app()` Functions
**File:** `api/__init__.py` (lines 23-78) AND `database/__init__.py` (lines 18-95)

**Problem:** 
- `api/__init__.py` imports from `database` (line 5)
- But then redefines `create_app()` itself (line 23)
- This creates confusion - which one is actually used?

**Root Cause:** Code duplication from refactoring

**Fix Required:** Remove duplicate, use single source of truth

#### Issue 2: MongoDB Connection Not Validated
**File:** `database/__init__.py:38-47`

**Problem:**
```python
connect(db=app.config['MONGODB_DB_NAME'], host=app.config['MONGODB_URI'], alias='default')
logger.info(f"✅ Connected to MongoDB")
```

**Root Cause:** 
- `connect()` doesn't raise exception if URI is invalid
- MongoEngine connects lazily on first operation
- Success message appears even if connection will fail later

**Impact:** Silent failures - app starts, first DB query fails

**Fix Required:** Add explicit connection test after connect()

#### Issue 3: MongoDB URI Format Conflict
**File:** `config.py:16`

**Problem:**
```python
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kirana_db')
```

If URI contains database name (`/kirana_db`), and you also pass `db='kirana_db'`, MongoEngine might use the URI's database instead.

**Root Cause:** Ambiguous database specification

**Fix Required:** Parse URI and extract DB name, or use only one method

#### Issue 4: No Connection Cleanup
**File:** `database/__init__.py:88-91`

**Problem:**
```python
@app.teardown_appcontext
def close_db(error):
    pass  # MongoEngine handles connection pooling
```

**Root Cause:** 
- Comment says MongoEngine handles it, but no explicit disconnect on shutdown
- Flask app shutdown doesn't call disconnect()
- Only FastAPI app (`main.py:62`) has proper shutdown handler

**Impact:** Connections may leak in long-running processes

#### Issue 5: Missing Awaits (Not Applicable - MongoEngine is Sync)
**Status:** ✅ Not an issue - MongoEngine is synchronous

---

## 3️⃣ Blockchain Integration Check

### ✅ Correctly Implemented

1. **Library:** `web3.py` used correctly
2. **Transaction Signing:** Uses `eth_account` for key management
3. **Gas Handling:** Gas price fetched dynamically, gas limit set
4. **Error Handling:** Try/except blocks around blockchain calls
5. **Contract Interaction:** ABI loaded, contract functions called correctly

### ❌ Critical Issues

#### Issue 1: RPC URL Inconsistency (CRITICAL)
**File 1:** `services/transaction/transaction_service.py:61`
```python
_blockchain_service = BlockchainService(
    rpc_url=BlockchainConfig.RPC_URL,  # ❌ Uses RPC_URL (defaults to localhost:8545)
    private_key=BlockchainConfig.PRIVATE_KEY,
    contract_address=BlockchainConfig.CONTRACT_ADDRESS
)
```

**File 2:** `api/routes/blockchain.py:67`
```python
return BlockchainService(
    rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL,  # ✅ Uses POLYGON_AMOY_RPC_URL
    private_key=BlockchainConfig.PRIVATE_KEY,
    contract_address=BlockchainConfig.CONTRACT_ADDRESS
)
```

**Problem:**
- Transaction service uses `RPC_URL` (defaults to `http://localhost:8545`)
- Blockchain routes use `POLYGON_AMOY_RPC_URL` (defaults to Polygon Amoy)
- **These point to different networks!**

**Root Cause:** Inconsistent configuration usage

**Impact:** 
- Transactions created via `/api/transactions` try to write to localhost (which is likely not running)
- Direct blockchain calls via `/api/blockchain` use Polygon Amoy
- Transactions silently fail blockchain writes

**Fix Required:** Use same RPC URL everywhere, prefer `POLYGON_AMOY_RPC_URL`

#### Issue 2: Blockchain Service Instance Management
**File:** `services/transaction/transaction_service.py:36-72`

**Problem:**
- Global singleton `_blockchain_service` in transaction_service
- But `api/routes/blockchain.py:66` creates NEW instance every request
- Different services initialize differently

**Root Cause:** No centralized blockchain service initialization

**Impact:** Multiple Web3 connections, inconsistent state

#### Issue 3: Silent Blockchain Failures
**File:** `services/transaction/transaction_service.py:69-72`

**Problem:**
```python
except Exception as e:
    logger.warning(f"Failed to initialize blockchain service: {e}.")
    return None  # ❌ Returns None, no exception
```

**Root Cause:** 
- Failures are logged as warnings, not errors
- Service returns None, transaction continues without blockchain
- No notification to user that blockchain write failed

**Impact:** Transactions succeed in MongoDB but fail silently on blockchain

#### Issue 4: Missing Connection Validation
**File:** `blockchain/utils/contract_service.py:31-32`

**Problem:**
```python
if not self.w3.is_connected():
    raise ConnectionError(f"Failed to connect to blockchain at {rpc_url}")
```

This check happens during `__init__`, but:
- If RPC URL is wrong, initialization might succeed but later calls fail
- No retry logic
- No health check endpoint validates blockchain connection

**Impact:** App starts successfully, blockchain calls fail later

#### Issue 5: No Gas Balance Check
**File:** `blockchain/utils/contract_service.py:89-92`

**Problem:**
```python
gas_price = self.w3.eth.gas_price
transaction = tx_function(*args).build_transaction({
    "gas": gas_limit,
    "gasPrice": gas_price,
})
```

No check if wallet has sufficient MATIC/ETH for gas fees.

**Impact:** Transactions fail with "insufficient funds" at send time

#### Issue 6: Contract ABI Path Issue
**File:** `blockchain/utils/contract_service.py:45`

**Problem:**
```python
abi_path = Path(__file__).parent.parent / "abis" / "KiranaLedger.json"
```

**Root Cause:** 
- Path is relative to `contract_service.py` location
- If imported from different location, path breaks
- No fallback or validation

**Impact:** FileNotFoundError if ABI file missing or path wrong

#### Issue 7: Async Handling (Not an Issue)
**Status:** ✅ web3.py is synchronous, no async issues

---

## 4️⃣ Why the System Is Not Working Correctly

### Exact Issues with File Names and Line Numbers

#### Issue #1: RPC URL Mismatch - Transactions Fail to Write to Blockchain
- **File:** `backend/services/transaction/transaction_service.py`
- **Line:** 61
- **Root Cause:** Uses `BlockchainConfig.RPC_URL` (localhost) instead of `POLYGON_AMOY_RPC_URL` (Polygon)
- **Impact:** All transaction blockchain writes fail silently (localhost:8545 not running)
- **Severity:** 🔴 CRITICAL

#### Issue #2: MongoDB Connection Not Actually Validated
- **File:** `backend/database/__init__.py`
- **Line:** 38-47
- **Root Cause:** MongoEngine `connect()` doesn't validate connection immediately
- **Impact:** App starts successfully but first DB query fails with connection error
- **Severity:** 🟡 HIGH

#### Issue #3: Duplicate `create_app()` Functions
- **File:** `backend/api/__init__.py` (lines 23-78) AND `backend/database/__init__.py` (lines 18-95)
- **Root Cause:** Code duplication from refactoring
- **Impact:** Confusion about which code path is used, potential bugs
- **Severity:** 🟡 HIGH

#### Issue #4: Blockchain Failures Swallowed Silently
- **File:** `backend/services/transaction/transaction_service.py`
- **Line:** 185-212
- **Root Cause:** Try/except catches all exceptions, logs warning, continues
- **Impact:** Transactions succeed in MongoDB but blockchain writes fail without user notification
- **Severity:** 🔴 CRITICAL

#### Issue #5: No Gas Balance Validation
- **File:** `backend/blockchain/utils/contract_service.py`
- **Line:** 89-110
- **Root Cause:** No check if wallet has MATIC/ETH before sending transaction
- **Impact:** Transaction fails at send time with confusing error
- **Severity:** 🟡 MEDIUM

#### Issue #6: Inconsistent Blockchain Service Initialization
- **File:** Multiple files
  - `backend/services/transaction/transaction_service.py:39-72` (singleton)
  - `backend/api/routes/blockchain.py:52-70` (new instance per request)
  - `backend/services/debt/debt_service.py:210-214` (new instance per call)
- **Root Cause:** No centralized service initialization
- **Impact:** Multiple Web3 connections, potential connection leaks
- **Severity:** 🟡 MEDIUM

#### Issue #7: MongoDB URI Database Name Conflict
- **File:** `backend/config.py`
- **Line:** 16
- **Root Cause:** URI may contain DB name, also passed as separate parameter
- **Impact:** MongoEngine might use wrong database
- **Severity:** 🟢 LOW (might work by accident)

#### Issue #8: No Connection Cleanup on Flask Shutdown
- **File:** `backend/database/__init__.py`
- **Line:** 88-91
- **Root Cause:** `teardown_appcontext` does nothing, no shutdown handler
- **Impact:** Connection leaks in long-running processes
- **Severity:** 🟢 LOW

---

## 5️⃣ Summary: Root Causes

### Primary Reasons System Fails:

1. **Blockchain writes fail because RPC URL points to localhost instead of Polygon Amoy**
   - Transaction service uses wrong RPC URL
   - Localhost Hardhat node not running
   - Failures logged as warnings, not errors

2. **MongoDB connections appear successful but aren't validated**
   - App starts, first query fails
   - No explicit connection test

3. **Error handling is too permissive**
   - Blockchain failures don't stop transaction creation
   - Users don't know blockchain write failed
   - Silent failures accumulate

4. **Configuration inconsistency**
   - Multiple ways to initialize blockchain service
   - Different RPC URLs in different places
   - No single source of truth

### What's Partially Implemented:

✅ **MongoDB Models** - Fully implemented
✅ **Transaction Creation** - Works for MongoDB
✅ **Blockchain Contract Service** - Code is correct
✅ **API Routes** - All routes exist

❌ **Blockchain Integration** - Code exists but uses wrong network
❌ **Error Handling** - Too permissive, failures hidden
❌ **Connection Validation** - Not actually tested
❌ **Service Initialization** - Inconsistent patterns

---

## 6️⃣ Fixes Required (Priority Order)

### Critical (Fix Immediately):

1. **Fix RPC URL in transaction_service.py:61**
   - Change `RPC_URL` to `POLYGON_AMOY_RPC_URL`

2. **Add MongoDB connection validation**
   - Test connection after `connect()`

3. **Fix blockchain error handling**
   - Make blockchain failures visible to users
   - Consider making blockchain writes blocking (fail transaction if blockchain fails)

### High Priority:

4. **Remove duplicate `create_app()`**
   - Consolidate to single function

5. **Centralize blockchain service initialization**
   - Create single `get_blockchain_service()` used everywhere

6. **Add gas balance check**
   - Validate wallet has funds before sending transaction

### Medium/Low Priority:

7. **Fix MongoDB URI parsing**
   - Extract DB name from URI if present

8. **Add connection cleanup**
   - Proper shutdown handlers for Flask

---

**End of Analysis**

