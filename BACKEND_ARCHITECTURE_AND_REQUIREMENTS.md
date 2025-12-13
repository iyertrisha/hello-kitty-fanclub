# Backend Architecture & Requirements Documentation

**Last Updated:** Based on repository analysis and clarification questions  
**Purpose:** Comprehensive reference for implementing missing backend features

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Data Models & Relationships](#data-models--relationships)
4. [Authentication & Authorization](#authentication--authorization)
5. [Blockchain Integration](#blockchain-integration)
6. [Inventory Management](#inventory-management)
7. [WhatsApp Bot Integration](#whatsapp-bot-integration)
8. [Voice-to-Blockchain Flow](#voice-to-blockchain-flow)
9. [Credit Scoring System](#credit-scoring-system)
10. [Missing Backend Features](#missing-backend-features)
11. [API Contract Requirements](#api-contract-requirements)
12. [Integration Points](#integration-points)

---

## System Overview

This is a **hackathon-grade system** evolving into production that integrates:

- **Flutter Mobile App** (shopkeeper interface)
- **WhatsApp Chatbot** (customer-facing, debt management)
- **Supplier Portal** (web-based, inventory management)
- **Admin Dashboard** (web-based, monitoring & analytics)
- **MongoDB** (primary database, source of truth)
- **Blockchain Ledger** (immutable audit trail, Polygon Amoy testnet)

### Core Principles

- **MongoDB = Source of Truth**: All operational data lives in MongoDB
- **Blockchain = Immutable Audit Ledger**: Transaction hashes and verification data
- **No Secrets in Code**: All secrets via environment variables
- **No Breaking Changes**: Version routes if needed
- **Async Blockchain Writes**: MongoDB writes succeed immediately, blockchain writes happen in background

---

## Technology Stack

### Backend Framework

- **Primary**: Flask (Python) - Port 5000
  - Main API server for all business logic
  - Routes: `/api/*`
  - Entry point: `backend/run.py`
  
- **Secondary**: FastAPI (Python) - Port 8000
  - ML credit scoring endpoints only
  - Routes: `/docs`, `/health`
  - Entry point: `backend/main.py`

### Database

- **MongoDB** with MongoEngine ODM
- Connection: `MONGODB_URI` from `.env`
- Database name: `MONGODB_DB_NAME` (default: `kirana_db`)

### Blockchain

- **Network**: Polygon Amoy (testnet)
- **Library**: Web3.py (Python)
- **RPC URL**: `POLYGON_AMOY_RPC_URL` from `.env`
- **Contract**: KiranaLedger.sol (deployed address in `CONTRACT_ADDRESS`)
- **Service**: `blockchain/utils/contract_service.py`

### WhatsApp Bot

- **Provider**: whatsapp-web.js (Node.js, free)
- **Location**: `backend/whatsapp-bot/`
- **Entry Point**: `backend/whatsapp-bot/index.js`
- **Architecture**: Stateless message handling

### Voice Processing

- **STT**: Google Speech API (Trisha's integration)
- **Parser**: `blockchain/voice_parser.py` (Hindi/English/Kannada)
- **Flow**: Voice → STT → Parse → Transaction → Blockchain

---

## Data Models & Relationships

### Core Entities

#### Shopkeeper
- **Unique Identifier**: Phone number (one-to-one, cannot be reused)
- **Required Fields**: `name`, `address`, `phone`, `wallet_address`
- **Optional Fields**: `email`, `location`, `blockchain_address`
- **Credit Score**: `credit_score` (0-900, Vishwas Score)
- **Status**: `is_active`, `flagged`, `flag_reason`

#### Customer
- **Unique Identifier**: Phone number
- **Relationship**: Many-to-many with shopkeepers
- **Default Shopkeeper**: `default_shopkeeper_id` (for WhatsApp bot routing)
- **Auto-creation**: Created on first WhatsApp contact
- **Fields**: `name`, `phone`, `total_purchases`, `total_credits`, `credit_balance`

#### Product (Inventory)
- **Owner**: Supplier (inventory truth owned by supplier)
- **Relationship**: Many-to-one with shopkeeper (shopkeeper views supplier inventory)
- **Pricing**: Fixed by supplier (no shopkeeper markup)
- **Fields**: `name`, `category`, `price`, `stock_quantity`, `shopkeeper_id`

#### Transaction
- **Types**: `sale`, `credit`, `repay`
- **Status**: `pending`, `verified`, `disputed`, `completed`
- **Blockchain**: All verified transactions go on-chain
- **Fields**: `type`, `amount`, `shopkeeper_id`, `customer_id`, `product_id`, `blockchain_tx_id`, `transcript_hash`

#### Cooperative
- **Members**: List of shopkeepers
- **Purpose**: Bulk ordering, revenue sharing
- **Fields**: `name`, `members`, `revenue_split_percent`, `blockchain_coop_id`

#### Supplier
- **Service Area**: Geographic center + radius (km)
- **Authentication**: Email + OTP
- **Fields**: `name`, `email`, `phone`, `service_area_center`, `service_area_radius_km`

### Relationship Diagram

```
Shopkeeper (1) ──< (N) Transaction (N) >── (1) Customer
     │                                              │
     │                                              │
     └──< (N) Product                               └── (1) default_shopkeeper_id
     │
     └──< (N) Cooperative.members

Supplier (1) ──< (N) Product (via inventory seeder)
```

---

## Authentication & Authorization

### Shopkeeper (Flutter App)

- **Method**: Phone number + OTP
- **Flow**:
  1. User enters phone number
  2. Backend sends OTP (via SMS/WhatsApp)
  3. User verifies OTP
  4. Backend creates session/JWT
  5. **Register-on-first-login**: If shopkeeper doesn't exist, create profile
- **Required Endpoints**:
  - `POST /api/shopkeeper/login/request-otp`
  - `POST /api/shopkeeper/login/verify-otp`
  - `POST /api/shopkeeper/register` (auto-called if first login)

### Supplier (Web Portal)

- **Method**: Email + OTP (already implemented)
- **Endpoints**: 
  - `POST /api/supplier/login/request-otp`
  - `POST /api/supplier/login/verify-otp`
- **Session**: Flask session-based

### Customer (WhatsApp Bot)

- **Method**: Phone number (auto-created on first contact)
- **No explicit login**: Customer identified by WhatsApp phone number
- **Auto-creation**: `get_or_create_customer_by_phone()` in `grocery_service.py`

---

## Blockchain Integration

### Network Configuration

- **Network**: Polygon Amoy (testnet)
- **RPC URL**: `POLYGON_AMOY_RPC_URL` from `.env`
- **Chain ID**: From `CHAIN_ID` env var
- **Gas Limit**: `GAS_LIMIT` (default: 3000000)

### What Goes On-Chain

- **All Verified Transactions**: `sale`, `credit`, `repay`
- **Data Stored**:
  - `voiceHash`: SHA256 hash of transcript
  - `amount`: Transaction amount (in paise)
  - `txType`: 0=SALE, 1=CREDIT, 2=REPAY
  - `shopAddress`: Shopkeeper's Ethereum address
  - `timestamp`: Block timestamp

### Write Strategy

- **Async Pattern**: 
  1. MongoDB write succeeds immediately
  2. Blockchain write happens in background
  3. Transaction status: `pending` → `verified` (after blockchain confirmation)
  4. `blockchain_tx_id` and `blockchain_block_number` updated when confirmed

### Reconciliation

- **Strategy**: Periodic reconciliation job (to be implemented)
- **Check**: MongoDB transactions with `status='verified'` but no `blockchain_tx_id`
- **Action**: Retry blockchain write or mark as failed

### Service Methods

```python
# blockchain/utils/contract_service.py
- register_shopkeeper(address)
- record_transaction(voice_hash, shop_address, amount, tx_type)
- get_credit_score(shop_address)
- get_transaction(tx_id)
```

---

## Inventory Management

### Ownership Model

- **Truth Owner**: Supplier
- **Shopkeeper View**: Shopkeepers see supplier inventory (read-only or cached)
- **Pricing**: Fixed by supplier (no shopkeeper markup)
- **Inventory Seeder**: Shared across systems (to be implemented)

### Product Model

```python
Product:
  - name: String
  - category: String
  - price: Float (fixed by supplier)
  - stock_quantity: Int (supplier's stock)
  - shopkeeper_id: Reference (for shopkeeper-specific view)
```

### Inventory Seeder Requirements

- **Shared Data**: Products seeded from supplier catalog
- **Sync**: When supplier updates inventory, shopkeepers see updated prices/stock
- **Location**: `backend/database/seeders/` (existing structure)

---

## WhatsApp Bot Integration

### Provider

- **whatsapp-web.js** (Node.js, free, no API fees)
- **Location**: `backend/whatsapp-bot/`
- **Architecture**: Stateless (each message handled independently)

### Linking to Shopkeeper

- **Method**: Phone number matching
- **Flow**:
  1. Customer messages WhatsApp bot
  2. Bot extracts customer phone number
  3. Bot looks up customer's `default_shopkeeper_id`
  4. Bot queries shopkeeper's inventory via API
  5. Bot responds with shopkeeper-specific data

### Auto-Customer Creation

- **Trigger**: First WhatsApp message from unknown phone
- **Implementation**: `get_or_create_customer_by_phone()` in `grocery_service.py`
- **Default Shopkeeper**: Can be set via QR code scan (to be implemented)

### QR Code Generation

- **Purpose**: Link customer WhatsApp to shopkeeper
- **Format**: `whatsapp://link?phone=<shopkeeper_phone>&text=<encoded_message>`
- **Endpoint**: `GET /api/shopkeeper/<id>/qr-code` (to be implemented)
- **Usage**: Shopkeeper displays QR code in Flutter app, customer scans to link

### Debt Management

- **Endpoints**: `/api/debt/*` (already implemented)
- **Features**:
  - Query debt: "How much do I owe?"
  - Record debt: "Bought milk for ₹120"
  - Payment tracking: "Paid ₹50"
- **Blockchain**: Debt entries recorded on-chain

### Credit Reminders

- **Scheduler**: `reminderScheduler.js` (Node.js cron)
- **Frequency**: Configurable via `REMINDER_SCHEDULE` env var
- **Cutoff**: Outstanding debts > 0
- **Implementation**: Calls Flask API to get debt list, sends WhatsApp messages

---

## Voice-to-Blockchain Flow

### Complete Flow

```
🎤 Voice Input (Flutter App)
    ↓
📝 Speech-to-Text (Google Speech API)
    ↓
🔍 Parse Transcript (voice_parser.py)
    ↓
📡 POST /api/transactions (with transcript)
    ↓
✅ Verification & Fraud Detection
    ↓
💾 MongoDB Write (immediate)
    ↓
⛓️  Blockchain Write (async, background)
    ↓
📊 Admin Dashboard (blockchain logs)
```

### Endpoints

- `POST /api/transactions/transcribe` - Upload audio, get transcript
- `POST /api/transactions/parse` - Parse transcript, extract transaction data
- `POST /api/transactions` - Create transaction (with or without transcript)

### Verification Process

1. **Transcript Hash**: SHA256 hash of transcript stored
2. **Fraud Detection**: Checks transaction history, patterns
3. **Verification Status**: `verified`, `flagged`, `pending`, `rejected`
4. **Blockchain Write**: Only if `verification_status='verified'`

### Voice Parser

- **Languages**: Hindi, English, Kannada
- **Location**: `blockchain/voice_parser.py`
- **Features**:
  - Extracts: product, quantity, amount, customer, type
  - Product mapping: Hindi → English
  - Unit conversion: kg, gram, piece, etc.

---

## Credit Scoring System

### Formula

- **Method**: ML Model (already implemented)
- **Location**: `backend/ml/credit_score_model.py`
- **Input Features**:
  - Total sales
  - Credit given
  - Credit repaid
  - Transaction frequency
  - Days active
  - Product count
  - Cooperative membership

### Score Range

- **Vishwas Score**: 0-900
- **Calculation**: ML model prediction
- **Update Frequency**: On transaction completion or periodic batch

### Credit Limit

- **Type**: Fixed limit based on credit score
- **Formula**: `max_credit = credit_score * multiplier` (e.g., score * 100 = max credit in ₹)
- **Enforcement**: Check before allowing new credit transactions

### When Score Changes

- **Increases**: On successful repayments, consistent transaction history
- **Decreases**: On missed payments, disputes, fraud flags
- **Update Trigger**: After transaction status changes to `completed` or `disputed`

---

## Missing Backend Features

### 1. Shopkeeper Mobile (Flutter) Integration

#### Phone Number Login (OTP)
- [ ] `POST /api/shopkeeper/login/request-otp` - Send OTP to phone
- [ ] `POST /api/shopkeeper/login/verify-otp` - Verify OTP, create session
- [ ] `POST /api/shopkeeper/register` - Auto-register on first login (if phone not found)
- [ ] `GET /api/shopkeeper/me` - Get current shopkeeper profile (from session)

#### Store Profile Creation
- [ ] `POST /api/shopkeeper/<id>/profile` - Create/update store profile
  - Fields: `name`, `address`, `location` (lat/lng), `email`
- [ ] `GET /api/shopkeeper/<id>/profile` - Get store profile

#### QR Code Generation
- [ ] `GET /api/shopkeeper/<id>/qr-code` - Generate QR code for WhatsApp linking
  - Returns: QR code image or data URL
  - Format: `whatsapp://link?phone=<shopkeeper_phone>&text=Link+to+shop`

#### Voice → Text → Ledger → Blockchain
- [x] `POST /api/transactions/transcribe` - Already implemented
- [x] `POST /api/transactions/parse` - Already implemented
- [x] `POST /api/transactions` - Already implemented (with transcript support)
- [ ] Verify Flutter app integration works end-to-end

#### Inventory Database
- [x] `GET /api/shopkeeper/<id>/inventory` - Already implemented
- [x] `PUT /api/shopkeeper/<id>/inventory/<product_id>` - Already implemented
- [ ] `POST /api/shopkeeper/<id>/inventory` - Add new product (if shopkeeper can add)
- [ ] `DELETE /api/shopkeeper/<id>/inventory/<product_id>` - Remove product

#### Inventory Seeder (Shared)
- [ ] `POST /api/admin/inventory/seed` - Seed products from supplier catalog
- [ ] `GET /api/inventory/products` - Get all products (for seeder sync)
- [ ] Sync mechanism: When supplier updates inventory, shopkeepers see updates

#### Cooperative Join/Leave
- [x] Cooperative model exists
- [ ] `POST /api/cooperative/<id>/join` - Shopkeeper joins cooperative
- [ ] `POST /api/cooperative/<id>/leave` - Shopkeeper leaves cooperative
- [ ] `GET /api/shopkeeper/<id>/cooperatives` - List shopkeeper's cooperatives

#### Recent Transactions Dashboard
- [ ] `GET /api/shopkeeper/<id>/transactions/recent` - Get recent transactions (last 30 days)
  - Query params: `limit`, `offset`, `type`, `status`
- [ ] `GET /api/shopkeeper/<id>/transactions/stats` - Get transaction statistics
  - Returns: total sales, total credits, total repayments, counts

#### Full Transaction History
- [x] `GET /api/transactions` - Already implemented (with filters)
- [ ] Verify shopkeeper-specific filtering works

#### Credit/Debit Totals
- [ ] `GET /api/shopkeeper/<id>/credit-summary` - Get credit summary
  - Returns: total_credits_given, total_repayments, outstanding_credits, customer_counts
- [ ] `GET /api/shopkeeper/<id>/debt-summary` - Get debt summary (per customer)

#### Credit Score Calculation
- [x] `GET /api/shopkeeper/<id>/credit-score` - Already implemented
- [ ] Verify ML model integration works
- [ ] Add credit limit calculation: `max_credit = credit_score * 100`

### 2. WhatsApp Bot Integration

#### Link Inventory Using Shopkeeper Phone
- [x] `get_or_create_customer_by_phone()` - Already implemented
- [ ] Verify WhatsApp bot can query shopkeeper inventory via phone number
- [ ] Add endpoint: `GET /api/whatsapp/shopkeeper-by-phone?phone=<phone>` - Get shopkeeper by phone

#### Auto-Create Customer on First Contact
- [x] `get_or_create_customer_by_phone()` - Already implemented
- [ ] Verify works with WhatsApp bot message handler

#### Debt ↔ Ledger Linkage
- [x] Debt service exists: `services/debt/debt_service.py`
- [x] Debt routes exist: `api/routes/debt.py`
- [ ] Verify WhatsApp bot calls debt endpoints correctly

#### Product + Price View from Inventory
- [ ] `GET /api/whatsapp/products?shopkeeper_phone=<phone>` - Get products for shopkeeper
- [ ] Format response for WhatsApp bot (text/menu format)

#### Scheduled Credit Reminders
- [x] `reminderScheduler.js` - Already implemented
- [ ] Verify cron schedule works
- [ ] Add endpoint: `GET /api/debt/reminders/pending` - Get customers with outstanding debt
- [ ] Add endpoint: `POST /api/debt/reminders/send` - Send reminder to customer

### 3. Supplier Portal Integration

#### List Registered Stores by Geographic Area
- [ ] `GET /api/supplier/stores?lat=<lat>&lng=<lng>&radius=<km>` - Get stores in area
  - Uses supplier's `service_area_center` and `service_area_radius_km`
- [ ] `GET /api/supplier/stores` - Get all stores in supplier's service area

#### Bulk Orders from Cooperatives
- [x] `BulkOrder` model exists
- [ ] `POST /api/supplier/bulk-orders` - Create bulk order from cooperative
- [ ] `GET /api/supplier/bulk-orders` - List bulk orders
- [ ] `PUT /api/supplier/bulk-orders/<id>/status` - Update order status

#### Read-Only Blockchain Access
- [ ] `GET /api/supplier/blockchain/transactions?shopkeeper_id=<id>` - Get shopkeeper's blockchain transactions
- [ ] `GET /api/supplier/blockchain/verify?tx_hash=<hash>` - Verify transaction on blockchain

### 4. Admin Dashboard Compatibility

#### Verify Compatibility
- [x] `GET /api/admin/blockchain-logs` - Already implemented
- [ ] Verify no breaking changes to existing admin endpoints
- [ ] Test map logic still works (if admin dashboard has maps)

#### Additional Endpoints (if needed)
- [ ] `GET /api/admin/shopkeepers/stats` - Aggregate shopkeeper statistics
- [ ] `GET /api/admin/transactions/analytics` - Transaction analytics

---

## API Contract Requirements

### Authentication Headers

```http
# Session-based (Flask)
Cookie: session=<session_id>

# JWT-based (if implemented)
Authorization: Bearer <jwt_token>

# Internal API Key (WhatsApp bot)
Authorization: Bearer <WHATSAPP_INTERNAL_API_KEY>
```

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}

# Error Response
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

### Pagination

```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 100,
    "total_pages": 5
  }
}
```

---

## Integration Points

### Flutter App → Backend

- **Base URL**: `http://localhost:5000/api` (or production URL)
- **Auth**: Phone + OTP → Session
- **Endpoints**:
  - Shopkeeper login/register
  - Profile management
  - Inventory CRUD
  - Transaction creation (voice flow)
  - Dashboard data (transactions, stats, credit score)
  - QR code generation

### WhatsApp Bot → Backend

- **Base URL**: `http://localhost:5000/api` (from `FLASK_API_URL` env var)
- **Auth**: Internal API key (`WHATSAPP_INTERNAL_API_KEY`)
- **Endpoints**:
  - Debt queries/recording
  - Product catalog
  - Customer auto-creation
  - Reminder scheduling

### Supplier Portal → Backend

- **Base URL**: `http://localhost:5000/api`
- **Auth**: Email + OTP → Flask session
- **Endpoints**:
  - Store listing (geographic)
  - Bulk order management
  - Blockchain read access

### Admin Dashboard → Backend

- **Base URL**: `http://localhost:5000/api`
- **Auth**: (To be determined - may need admin auth)
- **Endpoints**:
  - Blockchain logs
  - Shopkeeper management
  - Transaction analytics
  - Map data (if applicable)

---

## Environment Variables Required

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/kirana_db
MONGODB_DB_NAME=kirana_db

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SECRET_KEY=<secret_key>

# Blockchain
RPC_URL=http://localhost:8545
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=<private_key>
CONTRACT_ADDRESS=<deployed_contract_address>
ADMIN_ADDRESS=<admin_wallet_address>
CHAIN_ID=80002
GAS_LIMIT=3000000

# WhatsApp Bot
FLASK_API_URL=http://localhost:5000
WHATSAPP_INTERNAL_API_KEY=<api_key>
REMINDER_SCHEDULE=0 9 * * *
TEST_MODE=false

# OTP (for shopkeeper/supplier login)
# SMS provider or WhatsApp OTP service

# SendGrid (for email OTP)
SENDGRID_API_KEY=<key>
SENDGRID_FROM_EMAIL=noreply@kirana.com

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Background Jobs & Schedulers

### Required Jobs

1. **Blockchain Reconciliation**
   - **Frequency**: Every 5 minutes
   - **Purpose**: Retry failed blockchain writes
   - **Location**: `services/transaction/blockchain_reconciliation.py` (to be created)

2. **Credit Score Updates**
   - **Frequency**: After each transaction completion
   - **Purpose**: Recalculate shopkeeper credit score
   - **Location**: `services/shopkeeper/credit_score_service.py` (to be created)

3. **Credit Reminders** (WhatsApp Bot)
   - **Frequency**: Daily at 9 AM (configurable)
   - **Purpose**: Send debt reminders to customers
   - **Location**: `backend/whatsapp-bot/reminderScheduler.js` (already implemented)

4. **Inventory Sync**
   - **Frequency**: On supplier inventory update
   - **Purpose**: Sync supplier inventory to shopkeeper views
   - **Location**: `services/inventory/inventory_sync.py` (to be created)

---

## Testing Requirements

### Unit Tests

- Service layer functions
- Model validations
- Blockchain service methods

### Integration Tests

- API endpoints
- Database operations
- Blockchain writes
- WhatsApp bot message handling

### End-to-End Tests

- Voice → Transaction → Blockchain flow
- WhatsApp bot → Backend → Database flow
- Flutter app → Backend → MongoDB flow

---

## Deployment Considerations

### Local Development

- Flask: `python run.py` (port 5000)
- FastAPI: `python main.py` (port 8000)
- WhatsApp Bot: `npm start` in `backend/whatsapp-bot/`
- MongoDB: Local instance
- Blockchain: Local Hardhat or Polygon Amoy testnet

### Production

- **Backend**: Flask + FastAPI (same server or separate)
- **Database**: MongoDB Atlas or self-hosted
- **Blockchain**: Polygon Mainnet (when ready)
- **WhatsApp Bot**: Node.js process (PM2 or systemd)
- **Queue**: Redis/Celery for background jobs (if needed)

---

## Next Steps

1. **Review this document** for accuracy
2. **Prioritize missing features** based on business needs
3. **Implement features** in order of priority
4. **Test integrations** with each client (Flutter, WhatsApp, Supplier, Admin)
5. **Deploy** to staging environment
6. **Monitor** blockchain writes and reconciliation

---

## Notes

- This is a **hackathon-grade system** - focus on correctness and clarity
- **No breaking changes** - use versioned routes if needed
- **MongoDB is source of truth** - blockchain is audit ledger only
- **Async blockchain writes** - don't block API responses
- **Phone numbers are unique** - one shopkeeper per phone number
- **Inventory owned by supplier** - shopkeepers view supplier inventory
- **Fixed pricing** - no shopkeeper markup on supplier prices

---

**End of Document**

