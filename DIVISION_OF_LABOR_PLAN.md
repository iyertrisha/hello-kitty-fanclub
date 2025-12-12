# Division of Labor Plan - Kirana Store Management System

**Project:** Whackiest - Blockchain-based Kirana Store Management System  
**Team Members:** Trisha, Vaidehi, Vineet, Mohit  
**Total Estimated Time:** 58-66 hours (distributed across 4 team members)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack Summary](#tech-stack-summary)
3. [Trisha - STT + Blockchain + Verification Logic](#trisha---stt--blockchain--verification-logic)
4. [Vaidehi - React Native Mobile App + React.js Admin Dashboard](#vaidehi---react-native-mobile-app--reactjs-admin-dashboard)
5. [Vineet - Backend API + Database + Business Services](#vineet---backend-api--database--business-services)
6. [Mohit - ML Credit Scoring + WhatsApp + NLP](#mohit---ml-credit-scoring--whatsapp--nlp)
7. [Dependencies & Integration Points](#dependencies--integration-points)
8. [File Structure Reference](#file-structure-reference)
9. [Testing & Integration Checklist](#testing--integration-checklist)

---

## Project Overview

A blockchain-powered Kirana (grocery) store management system with:
- Voice-based transaction recording (Hindi/regional languages)
- Blockchain verification and immutable transaction ledger
- Credit scoring system (Vishwas Score: 300-900)
- Cooperative management for bulk buying
- WhatsApp-based customer verification
- Admin dashboard for analytics and management
- Mobile app for shopkeepers

**Key Features:**
- Speech-to-text for transaction recording
- Smart contract on Polygon Amoy testnet
- Multi-layer fraud detection and verification
- ML-based credit scoring
- Real-time inventory management
- Cooperative bulk order routing

---

## Tech Stack Summary

| Component | Technology |
|-----------|-----------|
| **Blockchain** | Solidity ^0.8.20, Hardhat, Web3.py, Polygon Amoy Testnet |
| **Backend** | Python 3.9+, Flask, MongoDB (PyMongo/MongoEngine), pandas |
| **Frontend Mobile** | React Native, React Native Voice, Axios |
| **Frontend Admin** | React.js/Next.js, Recharts, Axios |
| **ML/AI** | scikit-learn, pandas, Dialogflow |
| **Integrations** | Google Speech API, Twilio (WhatsApp), Razorpay (UPI), ONDC |
| **Database** | MongoDB |
| **Deployment** | Local development + Polygon Amoy testnet |

---

## Trisha - STT + Blockchain + Verification Logic

**Time Estimate:** 14-16 hours  
**Focus:** Smart contract deployment, Google Speech API integration, verification decision engine

### Tech Stack
- **Solidity** ^0.8.20
- **Hardhat** (development environment)
- **Web3.py** (Python blockchain interaction)
- **Google Cloud Speech-to-Text API** (Python client)
- **Python** (fraud detection logic, hash calculation)

### Expected Outcomes

1. **Smart Contract Deployed** to Polygon Amoy testnet
   - Contract address available for other team members
   - All contract functions tested and working
   - ABI file generated and accessible

2. **Google Speech API Integration** functional
   - Hindi and regional language support
   - Voice recording → transcript conversion
   - Error handling for API failures

3. **Verification Logic Engine** implemented
   - Credit transaction verification flow
   - Sales transaction validation rules
   - Hash calculation (SHA256) for transcripts
   - Blockchain write decision logic

4. **Python Blockchain Service** ready for API integration
   - All contract methods exposed via Python service
   - Error handling and logging
   - Connection to Polygon Amoy testnet

### Files to Create/Modify

#### Smart Contract (Already Exists - Verify & Enhance)
```
whackiest/backend/blockchain/contracts/KiranaLedger.sol
```
**Status:** ✅ Already exists - verify all functions work correctly

**Required Functions:**
- `registerShopkeeper()` - Register shopkeeper on blockchain
- `recordTransaction()` - Record individual transaction (credit/repay)
- `recordBatchTransactions()` - Record daily aggregated sales
- `getTransaction()` - Retrieve transaction by ID
- `updateCreditScoreData()` - Update credit score metrics
- `getCreditScore()` - Get credit score data
- `createCooperative()` - Admin creates cooperative
- `joinCooperative()` - Shopkeeper joins cooperative
- `getCooperative()` - Get cooperative details
- `isCooperativeMember()` - Check membership

#### Hardhat Configuration (Already Exists - Verify)
```
whackiest/backend/blockchain/hardhat.config.js
```
**Status:** ✅ Already exists - verify Polygon Amoy network configuration

**Required Configuration:**
- Polygon Amoy testnet RPC URL
- Private key handling (from .env)
- Solidity compiler version ^0.8.20
- Gas optimization settings

#### Deployment Script (Already Exists - Verify)
```
whackiest/backend/blockchain/scripts/deploy.js
```
**Status:** ✅ Already exists - test deployment to Polygon Amoy

**Required Features:**
- Deploy to Polygon Amoy testnet
- Save contract address to file
- Generate ABI file in correct location
- Error handling for deployment failures

#### Python Blockchain Service (Already Exists - Enhance)
```
whackiest/backend/blockchain/utils/contract_service.py
```
**Status:** ✅ Already exists - verify all methods work, add any missing functionality

**Required Methods:**
- `register_shopkeeper(address)` - Register shopkeeper
- `record_transaction(voice_hash, shop_address, amount, tx_type)` - Record transaction
- `record_batch_transactions(batch_hash, shop_address, total_amount)` - Batch sales
- `get_transaction(tx_id)` - Get transaction details
- `update_credit_score(shop_address, credit_data)` - Update credit metrics
- `get_credit_score(shop_address)` - Get credit score data
- `create_cooperative(coop_id, name, terms_hash, split_percent)` - Create cooperative
- `join_cooperative(coop_id, shop_address)` - Join cooperative
- `get_cooperative(coop_id)` - Get cooperative info
- `is_cooperative_member(coop_id, shop_address)` - Check membership
- `is_shopkeeper_registered(address)` - Check registration

#### Google Speech API Integration (NEW)
```
whackiest/backend/integrations/google_speech.py
```
**Status:** ❌ Create new file

**Required Functions:**
- `transcribe_audio(audio_file_path, language_code='hi-IN')` - Convert audio to text
- `transcribe_audio_bytes(audio_bytes, language_code='hi-IN')` - Convert audio bytes to text
- `detect_language(audio_file_path)` - Auto-detect language
- Support for: Hindi (hi-IN), English (en-IN), Marathi (mr-IN), Gujarati (gu-IN)
- Error handling for API failures, rate limits
- Return transcript with confidence score

**Implementation Notes:**
- Use Google Cloud Speech-to-Text API (Python client library)
- Handle authentication via service account JSON key
- Support both file upload and byte stream input
- Return structured response: `{transcript: str, confidence: float, language: str}`

#### Fraud Detection Service (NEW)
```
whackiest/backend/services/fraud_detection.py
```
**Status:** ❌ Create new file

**Required Functions:**
- `detect_credit_anomaly(transaction_data, shopkeeper_history)` - Detect unusual credit patterns
- `validate_credit_transaction(amount, customer_id, shopkeeper_id)` - Business rule validation
- `detect_sales_anomaly(transaction_data, shopkeeper_history)` - Detect unusual sales patterns
- `validate_sales_transaction(product, price, amount)` - Real-time sales validation

**Anomaly Detection Rules:**
- Credit amount > average daily sales (flag)
- Credit frequency > 3 per day (flag)
- Sales amount > catalog price ±20% (flag)
- Unusual transaction timing (off-hours)
- Customer with no purchase history (credit only)

#### Transaction Verification Service (NEW)
```
whackiest/backend/services/transaction_verification.py
```
**Status:** ❌ Create new file

**Required Functions:**
- `verify_credit_transaction(transaction_data)` - Complete credit verification flow
- `verify_sales_transaction(transaction_data)` - Sales validation flow
- `calculate_transcript_hash(transcript)` - SHA256 hash calculation
- `should_write_to_blockchain(verification_result)` - Decision engine
- `aggregate_daily_sales(shopkeeper_id, date)` - Aggregate sales for batch write

**Credit Verification Flow:**
1. Cross-validation (business rules)
2. Customer confirmation status check (from Mohit's WhatsApp service)
3. Anomaly detection (ML model)
4. Decision: Write to blockchain if all pass, else database only

**Sales Verification Flow:**
1. Real-time validation (product, price, amount)
2. Write to database immediately
3. Background anomaly detection
4. End-of-day aggregation for blockchain

**Hash Calculation:**
- Input: Transcript string
- Output: SHA256 hash (bytes32 format for blockchain)
- Format: Hex string (0x...)

### Dependencies

**Trisha's work depends on:**
- None (foundational layer)

**Other team members depend on:**
- Vineet: Needs `contract_service.py` for blockchain API endpoints
- Mohit: Needs verification logic for WhatsApp confirmation flow
- Vaidehi: Indirect dependency (via Vineet's API)

### Testing Requirements

1. **Smart Contract Testing:**
   - Deploy to Polygon Amoy testnet
   - Test all contract functions via Hardhat console
   - Verify events are emitted correctly
   - Test gas costs for each operation

2. **Python Service Testing:**
   - Test connection to Polygon Amoy
   - Test all read/write methods
   - Test error handling (invalid addresses, insufficient gas, etc.)
   - Verify ABI loading works correctly

3. **Google Speech API Testing:**
   - Test with Hindi audio samples
   - Test with regional language samples
   - Test error handling (API failures, invalid audio)
   - Measure transcription accuracy

4. **Verification Logic Testing:**
   - Test credit verification flow with various scenarios
   - Test sales validation rules
   - Test hash calculation consistency
   - Test blockchain write decision logic

### Deliverables

1. ✅ Smart contract deployed to Polygon Amoy (contract address documented)
2. ✅ ABI file in `whackiest/backend/blockchain/abis/KiranaLedger.json`
3. ✅ Python blockchain service fully functional
4. ✅ Google Speech API integration working
5. ✅ Verification logic service implemented
6. ✅ Fraud detection service implemented
7. ✅ Documentation: Setup guide, API reference for contract_service.py

---

## Vaidehi - React Native Mobile App + React.js Admin Dashboard

**Time Estimate:** 14-16 hours  
**Focus:** Mobile app for shopkeepers, Admin dashboard for analytics

### Tech Stack
- **React Native** (mobile app)
- **React Native Voice** (voice recording)
- **React.js/Next.js** (admin dashboard)
- **Recharts** (data visualization)
- **Axios** (API calls)
- **React Navigation** (mobile navigation)
- **AsyncStorage** (offline storage)

### Expected Outcomes

1. **React Native Mobile App** functional
   - Voice recording and playback
   - Transaction recording interface
   - Credit score display with blockchain badge
   - Inventory management
   - Cooperative membership interface
   - Offline data sync

2. **React.js Admin Dashboard** functional
   - Overview statistics (stores, transactions, revenue)
   - Store management with search/filter
   - Cooperative management (create, view members, bulk orders)
   - Analytics charts (sales trends, credit scores, etc.)
   - Blockchain verification logs viewer

3. **API Integration** complete
   - All endpoints connected to Vineet's Flask API
   - Error handling and loading states
   - Authentication (if required)

### Files to Create

#### React Native Mobile App

**Project Structure:**
```
whackiest/frontend/shopkeeper-mobile/
├── src/
│   ├── screens/
│   │   ├── DashboardScreen.js
│   │   ├── RecordTransactionScreen.js
│   │   ├── CreditScoreScreen.js
│   │   ├── InventoryScreen.js
│   │   └── CooperativeScreen.js
│   ├── components/
│   │   ├── VoiceRecorder.js
│   │   ├── TransactionCard.js
│   │   ├── CreditScoreCard.js
│   │   └── ProductCard.js
│   ├── services/
│   │   └── api.js
│   ├── navigation/
│   │   └── AppNavigator.js
│   ├── utils/
│   │   └── offlineStorage.js
│   └── App.js
├── package.json
└── app.json
```

**Files to Create:**

1. **`whackiest/frontend/shopkeeper-mobile/src/screens/DashboardScreen.js`**
   - Display daily sales summary
   - Recent transactions list
   - Quick actions (record transaction, view credit score)
   - Stats cards (today's sales, pending credits, inventory alerts)

2. **`whackiest/frontend/shopkeeper-mobile/src/screens/RecordTransactionScreen.js`**
   - Voice recording interface (React Native Voice)
   - Display transcript from Google Speech API
   - Transaction type selection (Sale/Credit/Repay)
   - Amount and customer input fields
   - Submit to API endpoint

3. **`whackiest/frontend/shopkeeper-mobile/src/screens/CreditScoreScreen.js`**
   - Display Vishwas Score (300-900)
   - Blockchain badge indicator
   - Credit score breakdown (factors)
   - Historical score chart
   - Explanation of score components

4. **`whackiest/frontend/shopkeeper-mobile/src/screens/InventoryScreen.js`**
   - Product list with search
   - Add/edit/delete products
   - Stock quantity management
   - Price management
   - Category filtering

5. **`whackiest/frontend/shopkeeper-mobile/src/screens/CooperativeScreen.js`**
   - List of available cooperatives
   - Join/leave cooperative
   - View cooperative members
   - View bulk order history
   - Revenue split information

6. **`whackiest/frontend/shopkeeper-mobile/src/components/VoiceRecorder.js`**
   - Start/stop recording button
   - Recording indicator (waveform animation)
   - Playback functionality
   - Send audio to backend for transcription
   - Display transcript result

7. **`whackiest/frontend/shopkeeper-mobile/src/components/TransactionCard.js`**
   - Display transaction details (amount, type, date, customer)
   - Blockchain verification badge
   - Status indicator (verified/pending/disputed)
   - Action buttons (view details, dispute)

8. **`whackiest/frontend/shopkeeper-mobile/src/components/CreditScoreCard.js`**
   - Score display with color coding (300-500: red, 500-700: yellow, 700-900: green)
   - Blockchain verified badge
   - Score trend indicator (up/down arrow)
   - Quick stats (total sales, credit given, credit repaid)

9. **`whackiest/frontend/shopkeeper-mobile/src/components/ProductCard.js`**
   - Product name, price, stock quantity
   - Category badge
   - Edit/delete actions
   - Low stock warning

10. **`whackiest/frontend/shopkeeper-mobile/src/services/api.js`**
    - Base API URL configuration
    - Axios instance with interceptors
    - API methods:
      - `getTransactions()` - GET /api/transactions
      - `createTransaction(data)` - POST /api/transactions
      - `getCreditScore()` - GET /api/shopkeeper/credit-score
      - `getInventory()` - GET /api/shopkeeper/inventory
      - `updateInventory(productId, data)` - PUT /api/shopkeeper/inventory/:id
      - `getCooperatives()` - GET /api/cooperative
      - `joinCooperative(coopId)` - POST /api/cooperative/:id/join
      - `uploadAudio(audioFile)` - POST /api/transactions/transcribe
    - Error handling
    - Authentication headers (if required)

11. **`whackiest/frontend/shopkeeper-mobile/src/navigation/AppNavigator.js`**
    - Bottom tab navigator or drawer navigator
    - Screens: Dashboard, Record Transaction, Credit Score, Inventory, Cooperative
    - Navigation between screens
    - Deep linking support (if needed)

12. **`whackiest/frontend/shopkeeper-mobile/src/utils/offlineStorage.js`**
    - Save transactions locally (AsyncStorage)
    - Sync when online
    - Queue failed API calls
    - Conflict resolution logic

#### React.js Admin Dashboard

**Project Structure:**
```
whackiest/frontend/admin-dashboard/
├── src/
│   ├── pages/
│   │   ├── Overview.js
│   │   ├── StoreManagement.js
│   │   ├── Cooperatives.js
│   │   ├── Analytics.js
│   │   └── BlockchainLogs.js
│   ├── components/
│   │   ├── StatsCard.js
│   │   ├── SalesChart.js
│   │   ├── StoreTable.js
│   │   └── CooperativeCard.js
│   ├── services/
│   │   └── api.js
│   └── App.js
├── package.json
└── public/
```

**Files to Create:**

1. **`whackiest/frontend/admin-dashboard/src/pages/Overview.js`**
   - Total stores count
   - Total transactions (today, week, month)
   - Total revenue (today, week, month)
   - Active cooperatives count
   - Recent activity feed
   - Quick stats cards with icons

2. **`whackiest/frontend/admin-dashboard/src/pages/StoreManagement.js`**
   - Table of all shopkeepers
   - Search and filter functionality
   - Columns: Name, Address, Credit Score, Total Sales, Status
   - Actions: View details, Edit, Deactivate
   - Pagination

3. **`whackiest/frontend/admin-dashboard/src/pages/Cooperatives.js`**
   - List of all cooperatives
   - Create new cooperative button
   - View members for each cooperative
   - Bulk order management
   - Revenue split configuration

4. **`whackiest/frontend/admin-dashboard/src/pages/Analytics.js`**
   - Sales trends chart (Recharts - line chart)
   - Credit score distribution (bar chart)
   - Revenue by cooperative (pie chart)
   - Transaction volume over time (area chart)
   - Date range selector

5. **`whackiest/frontend/admin-dashboard/src/pages/BlockchainLogs.js`**
   - List of blockchain transactions
   - Filter by shopkeeper, date, type
   - Display transaction hash, block number, timestamp
   - Link to PolygonScan explorer
   - Verification status indicators

6. **`whackiest/frontend/admin-dashboard/src/components/StatsCard.js`**
   - Reusable card component
   - Props: title, value, icon, trend (optional)
   - Color coding based on value
   - Click handler for navigation

7. **`whackiest/frontend/admin-dashboard/src/components/SalesChart.js`**
   - Recharts line/area chart
   - Display sales over time
   - Date range filtering
   - Tooltip with detailed information
   - Responsive design

8. **`whackiest/frontend/admin-dashboard/src/components/StoreTable.js`**
   - Data table with sorting
   - Search input
   - Filter dropdowns (status, credit score range)
   - Pagination controls
   - Row actions (view, edit, delete)

9. **`whackiest/frontend/admin-dashboard/src/components/CooperativeCard.js`**
   - Display cooperative name, member count, revenue split
   - Member list (expandable)
   - Bulk order history
   - Actions: Edit, View details, Add members

10. **`whackiest/frontend/admin-dashboard/src/services/api.js`**
    - Base API URL configuration
    - Axios instance
    - API methods:
      - `getOverviewStats()` - GET /api/admin/overview
      - `getStores(filters)` - GET /api/admin/stores
      - `getCooperatives()` - GET /api/admin/cooperatives
      - `createCooperative(data)` - POST /api/admin/cooperatives
      - `getAnalytics(dateRange)` - GET /api/admin/analytics
      - `getBlockchainLogs(filters)` - GET /api/admin/blockchain-logs
    - Error handling
    - Loading state management

### Dependencies

**Vaidehi's work depends on:**
- Vineet: Flask API endpoints must be ready
- Trisha: Blockchain service (indirect via Vineet's API)

**Other team members depend on:**
- None (frontend only)

### Testing Requirements

1. **Mobile App Testing:**
   - Test voice recording on physical device
   - Test offline storage and sync
   - Test all API integrations
   - Test navigation flow
   - Test on Android and iOS (if possible)

2. **Admin Dashboard Testing:**
   - Test all API calls
   - Test chart rendering with sample data
   - Test search and filter functionality
   - Test responsive design
   - Test error handling

### Deliverables

1. ✅ React Native mobile app with all screens functional
2. ✅ React.js admin dashboard with all pages functional
3. ✅ API integration complete
4. ✅ Offline storage working
5. ✅ Charts and visualizations rendering correctly
6. ✅ Responsive design for both apps

---

## Vineet - Backend API + Database + Business Services

**Time Estimate:** 14-16 hours  
**Focus:** Flask REST API, MongoDB setup, business logic services

### Tech Stack
- **Python Flask** (REST API framework)
- **MongoDB** (PyMongo or MongoEngine)
- **pandas** (data processing)
- **Flask-CORS** (CORS handling)
- **python-dotenv** (environment variables)

### Expected Outcomes

1. **Flask REST API** fully functional
   - All endpoints implemented and tested
   - Error handling and validation
   - CORS configured
   - Authentication middleware (if required)

2. **MongoDB Database** set up
   - All models defined with indexes
   - Seed data script ready
   - Connection pooling configured

3. **Business Logic Services** implemented
   - Transaction validation
   - Order routing logic
   - Store clustering algorithm
   - Cooperative bulk order aggregation

4. **API Integration** with blockchain service
   - Endpoints for blockchain operations
   - Transaction status updates
   - Credit score synchronization

### Files to Create

#### Flask Application

1. **`whackiest/backend/api/app.py`**
   - Flask app initialization
   - Blueprint registration
   - CORS configuration
   - Error handlers
   - Database connection setup
   - Environment variable loading

**Required Setup:**
- Flask app instance
- MongoDB connection
- CORS enabled for frontend origins
- Global error handlers (404, 500, etc.)
- Request logging middleware

#### API Routes

2. **`whackiest/backend/api/routes/transactions.py`**
   - `POST /api/transactions` - Create new transaction
   - `GET /api/transactions` - Get transactions (with filters)
   - `GET /api/transactions/:id` - Get transaction by ID
   - `PUT /api/transactions/:id/status` - Update transaction status
   - `POST /api/transactions/transcribe` - Upload audio for transcription

**Request/Response Formats:**
- POST: `{type: 'sale'|'credit'|'repay', amount: number, customer_id: string, product_id?: string, audio_file?: File}`
- GET: Query params: `shopkeeper_id, customer_id, type, date_from, date_to, limit, offset`
- Response: `{id, type, amount, customer, shopkeeper, timestamp, status, blockchain_hash?}`

3. **`whackiest/backend/api/routes/shopkeeper.py`**
   - `POST /api/shopkeeper/register` - Register new shopkeeper
   - `GET /api/shopkeeper/:id` - Get shopkeeper profile
   - `PUT /api/shopkeeper/:id` - Update shopkeeper profile
   - `GET /api/shopkeeper/:id/credit-score` - Get credit score
   - `GET /api/shopkeeper/:id/inventory` - Get inventory
   - `PUT /api/shopkeeper/:id/inventory/:product_id` - Update inventory

**Request/Response Formats:**
- Register: `{name, address, phone, email, wallet_address}`
- Credit Score: `{score: number, factors: object, blockchain_verified: boolean}`

4. **`whackiest/backend/api/routes/customer.py`**
   - `GET /api/customer/:id/orders` - Get customer order history
   - `GET /api/customer/:id/credits` - Get credit history
   - `POST /api/customer` - Create customer record
   - `GET /api/customer/:id` - Get customer profile

5. **`whackiest/backend/api/routes/blockchain.py`**
   - `POST /api/blockchain/record-transaction` - Record transaction on blockchain
   - `GET /api/blockchain/transaction/:id` - Get blockchain transaction
   - `POST /api/blockchain/register-shopkeeper` - Register shopkeeper on blockchain
   - `GET /api/blockchain/credit-score/:shopkeeper_id` - Get credit score from blockchain

**Integration:**
- Use Trisha's `contract_service.py` from `whackiest/backend/blockchain/utils/`
- Handle blockchain errors gracefully
- Return blockchain transaction hash on success

6. **`whackiest/backend/api/routes/cooperative.py`**
   - `GET /api/cooperative` - List all cooperatives
   - `GET /api/cooperative/:id` - Get cooperative details
   - `POST /api/cooperative/:id/join` - Join cooperative
   - `GET /api/cooperative/:id/members` - Get cooperative members
   - `POST /api/cooperative/:id/bulk-order` - Create bulk order
   - `GET /api/cooperative/:id/orders` - Get bulk order history

7. **`whackiest/backend/api/routes/admin.py`**
   - `GET /api/admin/overview` - Get overview statistics
   - `GET /api/admin/stores` - Get all stores (with filters)
   - `GET /api/admin/cooperatives` - Get all cooperatives
   - `POST /api/admin/cooperatives` - Create cooperative
   - `GET /api/admin/analytics` - Get analytics data
   - `GET /api/admin/blockchain-logs` - Get blockchain transaction logs

**Analytics Endpoint Response:**
- `{sales_trend: [{date, amount}], credit_scores: [{shopkeeper_id, score}], revenue_by_coop: [{coop_id, revenue}]}`

#### Middleware

8. **`whackiest/backend/api/middleware/auth.py`**
   - JWT token validation (if authentication required)
   - Shopkeeper authentication
   - Admin authentication
   - Request logging

9. **`whackiest/backend/api/middleware/validation.py`**
   - Request body validation
   - Query parameter validation
   - File upload validation
   - Input sanitization

10. **`whackiest/backend/api/middleware/error_handler.py`**
    - Global error handler decorator
    - Custom error classes
    - Error response formatting
    - Logging errors

#### Database Models

11. **`whackiest/backend/database/models.py`**
    - Shopkeeper model
    - Transaction model
    - Customer model
    - Cooperative model
    - Product/Inventory model

**Shopkeeper Model:**
- `{_id, name, address, phone, email, wallet_address, registered_at, credit_score, blockchain_address}`

**Transaction Model:**
- `{_id, type, amount, shopkeeper_id, customer_id, product_id?, timestamp, status, transcript_hash, blockchain_tx_id?, verification_status}`

**Customer Model:**
- `{_id, name, phone, address, created_at, total_purchases, total_credits, credit_balance}`

**Cooperative Model:**
- `{_id, name, description, revenue_split_percent, created_at, members: [shopkeeper_ids], blockchain_coop_id}`

**Product Model:**
- `{_id, name, category, price, stock_quantity, shopkeeper_id, created_at}`

**Indexes Required:**
- Transactions: `shopkeeper_id`, `customer_id`, `timestamp`, `status`
- Shopkeeper: `wallet_address` (unique)
- Customer: `phone` (unique)

#### Database Seeders

12. **`whackiest/backend/database/seeders/seed_data.py`**
    - Seed shopkeepers (5-10 sample shopkeepers)
    - Seed customers (20-30 sample customers)
    - Seed products (50-100 sample products)
    - Seed transactions (100-200 sample transactions)
    - Seed cooperatives (2-3 sample cooperatives)

#### Business Logic Services

13. **`whackiest/backend/services/shopkeeper_service.py`**
    - `get_shopkeeper(shopkeeper_id)` - Get shopkeeper with stats
    - `update_shopkeeper(shopkeeper_id, data)` - Update shopkeeper
    - `calculate_credit_score(shopkeeper_id)` - Calculate credit score (calls ML service)
    - `get_inventory(shopkeeper_id)` - Get inventory with stock alerts

14. **`whackiest/backend/services/customer_service.py`**
    - `get_customer(customer_id)` - Get customer with history
    - `create_customer(data)` - Create new customer
    - `get_customer_orders(customer_id, filters)` - Get order history
    - `get_customer_credits(customer_id)` - Get credit transactions

15. **`whackiest/backend/services/transaction_service.py`**
    - `create_transaction(data)` - Create transaction with validation
    - `get_transactions(filters)` - Get transactions with pagination
    - `update_transaction_status(transaction_id, status)` - Update status
    - `validate_transaction(data)` - Business rule validation
    - `aggregate_daily_sales(shopkeeper_id, date)` - Aggregate sales for blockchain

**Transaction Validation Logic:**
- Check product exists (for sales)
- Check price is within ±20% of catalog price
- Check amount > 0
- Check customer exists (for credits)
- Check credit amount is reasonable (< average daily sales)

16. **`whackiest/backend/services/cooperative_service.py`**
    - `get_cooperatives()` - Get all cooperatives
    - `create_cooperative(data)` - Create cooperative (calls blockchain)
    - `join_cooperative(coop_id, shopkeeper_id)` - Join cooperative
    - `get_cooperative_members(coop_id)` - Get members
    - `create_bulk_order(coop_id, order_data)` - Create bulk order
    - `calculate_revenue_split(coop_id, total_revenue)` - Calculate splits

17. **`whackiest/backend/services/order_routing.py`**
    - `find_nearest_store(product_id, quantity, customer_location)` - Find store with inventory
    - `route_order(order_data)` - Route order to best store
    - `check_inventory(store_id, product_id, quantity)` - Check stock availability
    - `calculate_distance(location1, location2)` - Calculate distance (Haversine formula)

**Order Routing Logic:**
- Find all stores with product in stock
- Filter by distance (within 10km radius)
- Select store with highest stock or lowest price
- Return store details and estimated delivery

18. **`whackiest/backend/services/store_clustering.py`**
    - `cluster_stores_by_location(stores, max_distance)` - Cluster stores geographically
    - `suggest_cooperative_members(store_id, radius)` - Suggest stores for cooperative
    - `calculate_cluster_center(stores)` - Calculate cluster center
    - `get_nearby_stores(store_id, radius)` - Get nearby stores

**Store Clustering Logic:**
- Group stores within 5km radius
- Suggest cooperative formation
- Calculate optimal cooperative boundaries

19. **`whackiest/backend/services/admin_service.py`**
    - `get_overview_stats()` - Calculate overview statistics
    - `get_all_stores(filters)` - Get stores with pagination
    - `get_analytics_data(date_range)` - Get analytics data
    - `get_blockchain_logs(filters)` - Get blockchain transactions

### Dependencies

**Vineet's work depends on:**
- Trisha: `contract_service.py` for blockchain operations
- Mohit: ML service endpoint for credit scoring (optional, can use local calculation)

**Other team members depend on:**
- Vaidehi: All frontend apps depend on Vineet's API
- Mohit: WhatsApp service needs transaction endpoints
- Trisha: Indirect (blockchain service is used by API)

### Testing Requirements

1. **API Endpoint Testing:**
   - Test all endpoints with Postman/curl
   - Test error handling (invalid data, missing fields)
   - Test pagination and filtering
   - Test file upload (audio transcription)

2. **Database Testing:**
   - Test all CRUD operations
   - Test indexes performance
   - Test seed data script
   - Test connection pooling

3. **Service Testing:**
   - Test transaction validation logic
   - Test order routing algorithm
   - Test store clustering algorithm
   - Test blockchain integration

### Deliverables

1. ✅ Flask API with all endpoints functional
2. ✅ MongoDB database with all models and indexes
3. ✅ Seed data script ready
4. ✅ All business logic services implemented
5. ✅ Blockchain integration working
6. ✅ API documentation (endpoints, request/response formats)
7. ✅ Error handling and validation complete

---

## Mohit - ML Credit Scoring + WhatsApp + NLP

**Time Estimate:** 16-18 hours  
**Focus:** ML model, WhatsApp integration, NLP, payment gateway, ONDC integration

### Tech Stack
- **scikit-learn** (ML models)
- **pandas** (data processing)
- **Twilio API** (WhatsApp)
- **Dialogflow** (NLP)
- **Razorpay API** (UPI payments)
- **Python Flask** (webhook handlers)
- **ngrok** (local webhook testing)

### Expected Outcomes

1. **ML Credit Scoring Model** trained and deployed
   - Vishwas Score (300-900) calculation
   - Model explanation and factor breakdown
   - API endpoint for credit score prediction

2. **WhatsApp Integration** functional
   - Customer order flow via WhatsApp
   - Credit confirmation flow
   - Monthly confirmation system
   - Webhook handling

3. **NLP Integration** working
   - Dialogflow setup with intents
   - Entity extraction (product, quantity, unit)
   - Multi-turn conversation handling
   - Hindi/English support

4. **Payment Gateway** integrated
   - Razorpay UPI setup
   - Mock transaction handling
   - Payment status tracking

5. **ONDC Integration** (adapter)
   - Voice inventory to ONDC schema conversion
   - Mock ONDC API calls

### Files to Create

#### ML Credit Scoring

1. **`whackiest/backend/ml/credit_score_model.py`**
   - `CreditScoreModel` class
   - `predict(shopkeeper_data)` - Predict credit score
   - `explain_score(shopkeeper_data)` - Explain score factors
   - `get_factors(shopkeeper_data)` - Get contributing factors

**Model Features:**
- Transaction consistency (coefficient: 0.25)
- Business growth (coefficient: 0.20)
- Product diversity (coefficient: 0.15)
- Cooperative participation (coefficient: 0.15)
- Repayment history (coefficient: 0.25)

**Output:**
- Score: 300-900 (integer)
- Factors: `{transaction_consistency: score, business_growth: score, product_diversity: score, cooperative_participation: score, repayment_history: score}`
- Explanation: Human-readable explanation string

2. **`whackiest/backend/ml/train_model.py`**
   - Load training data from CSV
   - Feature engineering
   - Train Gradient Boosting or Random Forest model
   - Save model to file (`model.pkl`)
   - Evaluate model performance
   - Generate feature importance plot

**Training Data Format (CSV):**
- Columns: `shopkeeper_id, total_sales, credit_given, credit_repaid, tx_frequency, product_count, cooperative_member, days_active, credit_score`

3. **`whackiest/backend/ml/data/training_data.csv`**
   - Sample training data (100-200 rows)
   - Realistic shopkeeper data
   - Credit scores (300-900 range)

#### WhatsApp Integration

4. **`whackiest/backend/integrations/whatsapp/twilio_client.py`**
   - `TwilioClient` class
   - `send_message(to, message)` - Send WhatsApp message
   - `send_template_message(to, template, params)` - Send template message
   - `receive_message(webhook_data)` - Parse incoming message

**Twilio Setup:**
- Account SID and Auth Token from .env
- WhatsApp sandbox number
- Webhook URL configuration

5. **`whackiest/backend/api/routes/whatsapp.py`**
   - `POST /api/whatsapp/webhook` - Receive WhatsApp messages
   - `POST /api/whatsapp/send` - Send WhatsApp message
   - `POST /api/whatsapp/confirm-credit` - Handle credit confirmation
   - `POST /api/whatsapp/monthly-confirmation` - Send monthly summary

**Webhook Handler Logic:**
- Parse incoming message
- Extract customer phone number
- Route to appropriate handler (order, confirmation, etc.)
- Call Dialogflow for NLP processing
- Update database based on response

**Credit Confirmation Flow:**
1. Receive: "Confirm ₹500 credit to Suresh? Reply YES/NO"
2. Wait for customer response
3. Parse YES/NO response
4. Update transaction status in database
5. If YES: Trigger blockchain write (via Vineet's API)

**Monthly Confirmation Flow:**
1. Generate monthly purchase summary for customer
2. Send WhatsApp message with summary
3. Parse customer response (OK/DISPUTE)
4. Flag disputed transactions for review

6. **`whackiest/backend/services/monthly_confirmation.py`**
   - `generate_monthly_summary(customer_id, month, year)` - Generate summary
   - `send_monthly_confirmation(customer_id)` - Send WhatsApp message
   - `process_confirmation_response(customer_id, response)` - Process response
   - `flag_disputed_transactions(customer_id, month)` - Flag disputes

**Monthly Summary Format:**
```
"Namaste! Your purchase summary for December 2024:

📦 Total Purchases: ₹2,450
🛒 Items: 45
📅 Transactions: 12

Top items:
1. Maggie - ₹10 (5 times)
2. Atta - ₹50 (2 times)
3. Rice - ₹200 (1 time)

Reply DISPUTE if you find any errors.
Reply OK to confirm."
```

#### NLP Integration

7. **`whackiest/backend/integrations/dialogflow_client.py`**
   - `DialogflowClient` class
   - `detect_intent(text, session_id)` - Detect intent from text
   - `extract_entities(text, intent)` - Extract entities
   - `handle_conversation(text, session_id, context)` - Multi-turn conversation

**Dialogflow Intents:**
- `place_order` - Customer wants to place order
- `check_price` - Customer wants to check price
- `confirm_order` - Customer confirms order
- `confirm_credit` - Customer confirms credit
- `dispute_transaction` - Customer disputes transaction

**Entities:**
- `@product` - Product name
- `@quantity` - Quantity number
- `@unit` - Unit (kg, liter, piece)
- `@customer_name` - Customer name
- `@amount` - Amount in rupees

**Example:**
- Input: "10 kg rice chahiye"
- Intent: `place_order`
- Entities: `{product: "rice", quantity: 10, unit: "kg"}`

#### Payment Gateway

8. **`whackiest/backend/integrations/razorpay_client.py`**
   - `RazorpayClient` class
   - `create_payment_order(amount, currency)` - Create payment order
   - `verify_payment(payment_id, order_id)` - Verify payment
   - `create_upi_link(amount, customer_phone)` - Create UPI payment link
   - `check_payment_status(payment_id)` - Check payment status

**Razorpay Setup:**
- API Key and Secret from .env
- Webhook URL for payment callbacks
- Mock mode for testing (no real payments)

#### ONDC Integration

9. **`whackiest/backend/integrations/ondc_client.py`**
   - `ONDCClient` class
   - `convert_to_ondc_schema(product_data)` - Convert product to ONDC format
   - `create_ondc_catalog(products)` - Create ONDC catalog
   - `search_ondc_products(query)` - Search ONDC products (mock)
   - `place_ondc_order(order_data)` - Place ONDC order (mock)

**ONDC Schema Conversion:**
- Convert voice-recorded inventory to ONDC product schema
- Map product attributes (name, price, quantity, category)
- Generate ONDC-compliant JSON

#### ML API Routes

10. **`whackiest/backend/api/routes/ml.py`**
    - `POST /api/ml/creditScore` - Calculate credit score
    - `GET /api/ml/creditScore/:shopkeeper_id` - Get credit score
    - `POST /api/ml/explainScore` - Explain credit score factors

**Credit Score Endpoint:**
- Input: `{shopkeeper_id: string}` or `{transaction_data: object}`
- Output: `{score: number, factors: object, explanation: string, blockchain_verified: boolean}`

**Note:** This endpoint should ONLY read blockchain-verified transaction data (via Vineet's API)

### Dependencies

**Mohit's work depends on:**
- Vineet: Transaction API endpoints for reading data
- Vineet: Transaction status update endpoints
- Trisha: Verification logic (indirect via Vineet)

**Other team members depend on:**
- Vineet: Uses Mohit's credit score API endpoint
- Vaidehi: Indirect (WhatsApp flow affects transaction status)

### Testing Requirements

1. **ML Model Testing:**
   - Test credit score prediction with sample data
   - Test model explanation output
   - Test feature importance
   - Validate score range (300-900)

2. **WhatsApp Testing:**
   - Test webhook receiving messages
   - Test sending messages
   - Test credit confirmation flow
   - Test monthly confirmation system
   - Use ngrok for local webhook testing

3. **NLP Testing:**
   - Test intent detection with Hindi/English
   - Test entity extraction
   - Test multi-turn conversations
   - Test order flow end-to-end

4. **Payment Gateway Testing:**
   - Test payment order creation
   - Test payment verification
   - Test UPI link generation
   - Test webhook callbacks (mock)

5. **ONDC Testing:**
   - Test schema conversion
   - Test catalog creation
   - Test product search (mock)

### Deliverables

1. ✅ ML credit scoring model trained and deployed
2. ✅ WhatsApp integration functional (Twilio)
3. ✅ Dialogflow NLP integration working
4. ✅ Razorpay payment gateway integrated
5. ✅ ONDC adapter implemented
6. ✅ Monthly confirmation system working
7. ✅ API endpoints for ML and WhatsApp
8. ✅ Documentation: Setup guides for Twilio, Dialogflow, Razorpay

---

## Dependencies & Integration Points

### Dependency Graph

```
Trisha (Blockchain)
    ↓
Vineet (API) ← Uses contract_service.py
    ↓
    ├──→ Vaidehi (Frontend) ← Uses Flask API endpoints
    └──→ Mohit (ML/WhatsApp) ← Uses transaction endpoints
            ↓
        Vineet (API) ← Updates transaction status
```

### Critical Integration Points

1. **Trisha → Vineet:**
   - Vineet uses `whackiest/backend/blockchain/utils/contract_service.py`
   - Vineet calls blockchain methods: `record_transaction()`, `register_shopkeeper()`, `get_credit_score()`
   - Contract address must be shared via environment variable

2. **Vineet → Vaidehi:**
   - All frontend apps call Vineet's Flask API
   - API base URL: `http://localhost:5000/api` (or production URL)
   - CORS must be enabled for frontend origins

3. **Vineet → Mohit:**
   - Mohit reads transactions via: `GET /api/transactions`
   - Mohit updates transaction status via: `PUT /api/transactions/:id/status`
   - Mohit's credit score API called by Vineet: `POST /api/ml/creditScore`

4. **Mohit → Vineet:**
   - WhatsApp confirmations update transaction status
   - Credit score calculation reads blockchain-verified data only
   - Monthly confirmations trigger transaction status updates

5. **Trisha → Mohit (Indirect):**
   - Verification logic determines if transaction goes to blockchain
   - Mohit's WhatsApp flow affects verification status
   - Credit score uses only blockchain-verified data

### Environment Variables Required

**Shared `.env` file in `whackiest/backend/`:**
```env
# Blockchain (Trisha)
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=0x...
ADMIN_ADDRESS=0x...

# Database (Vineet)
MONGODB_URI=mongodb://localhost:27017/kirana_db
MONGODB_DB_NAME=kirana_db

# Google Speech API (Trisha)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Twilio (Mohit)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Dialogflow (Mohit)
DIALOGFLOW_PROJECT_ID=your_project_id
DIALOGFLOW_CREDENTIALS=path/to/credentials.json

# Razorpay (Mohit)
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# Flask API (Vineet)
FLASK_ENV=development
FLASK_PORT=5000
API_BASE_URL=http://localhost:5000

# Frontend (Vaidehi)
REACT_APP_API_URL=http://localhost:5000/api
```

### API Contract (Key Endpoints)

**Transaction Endpoints (Vineet):**
- `POST /api/transactions` - Create transaction
  - Request: `{type, amount, customer_id, shopkeeper_id, audio_file?}`
  - Response: `{id, status, blockchain_hash?}`

- `GET /api/transactions` - Get transactions
  - Query: `shopkeeper_id, customer_id, type, date_from, date_to`
  - Response: `[{id, type, amount, customer, timestamp, status}]`

- `PUT /api/transactions/:id/status` - Update status
  - Request: `{status: 'verified'|'pending'|'disputed'}`
  - Response: `{success: true}`

**Blockchain Endpoints (Vineet → Trisha):**
- `POST /api/blockchain/record-transaction` - Write to blockchain
  - Request: `{transaction_id, voice_hash, amount, tx_type}`
  - Response: `{tx_hash, block_number}`

**Credit Score Endpoints (Mohit):**
- `POST /api/ml/creditScore` - Calculate credit score
  - Request: `{shopkeeper_id}`
  - Response: `{score: 300-900, factors: {...}, explanation: string}`

**WhatsApp Endpoints (Mohit):**
- `POST /api/whatsapp/webhook` - Receive messages
- `POST /api/whatsapp/send` - Send message
  - Request: `{to, message}`
  - Response: `{success: true, message_id}`

---

## File Structure Reference

### Complete File Tree

```
whackiest/
├── backend/
│   ├── api/
│   │   ├── app.py                          [Vineet]
│   │   ├── routes/
│   │   │   ├── transactions.py            [Vineet]
│   │   │   ├── shopkeeper.py              [Vineet]
│   │   │   ├── customer.py                [Vineet]
│   │   │   ├── blockchain.py              [Vineet]
│   │   │   ├── cooperative.py              [Vineet]
│   │   │   ├── admin.py                   [Vineet]
│   │   │   ├── whatsapp.py                [Mohit]
│   │   │   └── ml.py                      [Mohit]
│   │   └── middleware/
│   │       ├── auth.py                    [Vineet]
│   │       ├── validation.py              [Vineet]
│   │       └── error_handler.py           [Vineet]
│   ├── blockchain/
│   │   ├── contracts/
│   │   │   └── KiranaLedger.sol           [Trisha - ✅ Exists]
│   │   ├── scripts/
│   │   │   └── deploy.js                  [Trisha - ✅ Exists]
│   │   ├── utils/
│   │   │   └── contract_service.py        [Trisha - ✅ Exists]
│   │   └── hardhat.config.js              [Trisha - ✅ Exists]
│   ├── integrations/
│   │   ├── google_speech.py               [Trisha]
│   │   ├── whatsapp/
│   │   │   └── twilio_client.py           [Mohit]
│   │   ├── dialogflow_client.py           [Mohit]
│   │   ├── razorpay_client.py             [Mohit]
│   │   └── ondc_client.py                 [Mohit]
│   ├── services/
│   │   ├── fraud_detection.py             [Trisha]
│   │   ├── transaction_verification.py   [Trisha]
│   │   ├── shopkeeper_service.py         [Vineet]
│   │   ├── customer_service.py           [Vineet]
│   │   ├── transaction_service.py        [Vineet]
│   │   ├── cooperative_service.py        [Vineet]
│   │   ├── order_routing.py              [Vineet]
│   │   ├── store_clustering.py           [Vineet]
│   │   ├── admin_service.py             [Vineet]
│   │   └── monthly_confirmation.py       [Mohit]
│   ├── database/
│   │   ├── models.py                      [Vineet]
│   │   └── seeders/
│   │       └── seed_data.py              [Vineet]
│   ├── ml/
│   │   ├── credit_score_model.py         [Mohit]
│   │   ├── train_model.py                [Mohit]
│   │   └── data/
│   │       └── training_data.csv         [Mohit]
│   └── config.py                          [Vineet]
├── frontend/
│   ├── shopkeeper-mobile/                 [Vaidehi]
│   │   └── src/
│   │       ├── screens/                   [Vaidehi]
│   │       ├── components/                [Vaidehi]
│   │       ├── services/
│   │       │   └── api.js                 [Vaidehi]
│   │       ├── navigation/
│   │       │   └── AppNavigator.js        [Vaidehi]
│   │       └── utils/
│   │           └── offlineStorage.js      [Vaidehi]
│   └── admin-dashboard/                   [Vaidehi]
│       └── src/
│           ├── pages/                     [Vaidehi]
│           ├── components/                [Vaidehi]
│           └── services/
│               └── api.js                 [Vaidehi]
└── DIVISION_OF_LABOR_PLAN.md              [This file]
```

---

## Testing & Integration Checklist

### Pre-Integration Checklist

**Trisha:**
- [ ] Smart contract deployed to Polygon Amoy
- [ ] Contract address documented
- [ ] ABI file generated
- [ ] Python blockchain service tested
- [ ] Google Speech API working
- [ ] Verification logic tested

**Vineet:**
- [ ] Flask API running
- [ ] MongoDB connected
- [ ] All endpoints implemented
- [ ] Seed data loaded
- [ ] Blockchain integration tested
- [ ] CORS configured

**Vaidehi:**
- [ ] Mobile app builds successfully
- [ ] Admin dashboard runs
- [ ] API integration code written
- [ ] Components render correctly

**Mohit:**
- [ ] ML model trained
- [ ] Twilio webhook configured
- [ ] Dialogflow intents created
- [ ] Payment gateway tested
- [ ] API endpoints implemented

### Integration Testing Steps

1. **Trisha + Vineet Integration:**
   - [ ] Vineet can call `contract_service.py` methods
   - [ ] Blockchain transactions recorded successfully
   - [ ] Credit scores retrieved from blockchain
   - [ ] Error handling works

2. **Vineet + Vaidehi Integration:**
   - [ ] Mobile app can call all API endpoints
   - [ ] Admin dashboard displays data correctly
   - [ ] CORS allows frontend requests
   - [ ] Error responses handled in frontend

3. **Vineet + Mohit Integration:**
   - [ ] Mohit can read transactions via API
   - [ ] Mohit can update transaction status
   - [ ] Credit score API called by Vineet
   - [ ] WhatsApp confirmations update database

4. **End-to-End Testing:**
   - [ ] Voice recording → Transcription → Transaction creation → Blockchain write
   - [ ] Credit transaction → Customer confirmation → Blockchain write
   - [ ] Sales transaction → Daily aggregation → Blockchain write
   - [ ] Monthly confirmation → Customer response → Status update

### Final Verification

- [ ] All team members' code integrated
- [ ] No blocking errors
- [ ] All API endpoints functional
- [ ] Frontend apps display data correctly
- [ ] Blockchain transactions visible on PolygonScan
- [ ] WhatsApp flow working end-to-end
- [ ] Credit scoring produces reasonable scores
- [ ] Documentation complete

---

## Additional Notes

### Development Workflow

1. **Day 1-2:** Foundation
   - Trisha: Deploy contract, set up blockchain service
   - Vineet: Set up Flask API, MongoDB, basic endpoints
   - Vaidehi: Set up React Native and React.js projects
   - Mohit: Set up ML environment, Twilio account

2. **Day 3-4:** Core Features
   - Trisha: Google Speech API, verification logic
   - Vineet: All API endpoints, business services
   - Vaidehi: All screens and components
   - Mohit: ML model training, WhatsApp integration

3. **Day 5-6:** Integration & Testing
   - Integrate all components
   - End-to-end testing
   - Bug fixes
   - Documentation

### Communication Protocol

- **Daily Standup:** Share progress, blockers, integration needs
- **API Contract:** Vineet shares API documentation early
- **Blockchain Address:** Trisha shares contract address immediately after deployment
- **Environment Variables:** Share `.env` template early
- **Testing:** Test integration points as soon as they're ready

### Risk Mitigation

- **Blockchain Deployment:** Deploy early, test thoroughly
- **API Integration:** Define API contracts early, mock data for frontend
- **WhatsApp Webhooks:** Use ngrok for local testing
- **ML Model:** Use simple model first, iterate if time permits
- **Payment Gateway:** Use mock mode for demo

---

**End of Division of Labor Plan**
