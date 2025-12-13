# Testing New Endpoints

This guide explains how to run the comprehensive test suite for all newly implemented endpoints.

## Prerequisites

1. **Virtual environment activated**
2. **MongoDB running**
3. **Database seeded** (run `python database\seeders\seed_data.py`)
4. **Flask server running** (run `python run.py`)

## Quick Start

### Step 1: Start the Flask Server

In **Terminal 1**, activate venv and start the server:

```powershell
cd D:\whackiest\helloKittyFanclub
.\venv\Scripts\Activate.ps1
cd backend
python run.py
```

Keep this terminal running. You should see:
```
✅ Connected to MongoDB: kirana_db
✅ Flask application initialized successfully
 * Running on http://127.0.0.1:5000
```

### Step 2: Run the Test Script

In **Terminal 2**, run the test script:

```powershell
cd D:\whackiest\helloKittyFanclub
.\venv\Scripts\Activate.ps1
cd backend
python test_new_endpoints.py
```

## What Gets Tested

The script tests all newly implemented endpoints:

### 1. Shopkeeper Authentication & Login
- `POST /api/shopkeeper/login/request-otp` - Request OTP
- `POST /api/shopkeeper/login/verify-otp` - Verify OTP
- `GET /api/shopkeeper/me` - Get current shopkeeper
- `POST /api/shopkeeper/logout` - Logout

### 2. Shopkeeper Profile Management
- `GET /api/shopkeeper/<id>/profile` - Get profile
- `POST /api/shopkeeper/<id>/profile` - Update profile

### 3. QR Code Generation
- `GET /api/shopkeeper/<id>/qr-code` - Generate QR code

### 4. Inventory Management
- `POST /api/shopkeeper/<id>/inventory` - Add product
- `DELETE /api/shopkeeper/<id>/inventory/<product_id>` - Delete product

### 5. Transaction Endpoints
- `GET /api/shopkeeper/<id>/transactions/recent` - Recent transactions
- `GET /api/shopkeeper/<id>/transactions/stats` - Transaction statistics
- `GET /api/shopkeeper/<id>/credit-summary` - Credit summary
- `GET /api/shopkeeper/<id>/debt-summary` - Debt summary

### 6. Cooperative Endpoints
- `GET /api/shopkeeper/<id>/cooperatives` - Get shopkeeper's cooperatives
- `POST /api/cooperative/<id>/leave` - Leave cooperative

### 7. WhatsApp Bot Endpoints
- `GET /api/whatsapp/shopkeeper-by-phone` - Get shopkeeper by phone
- `GET /api/whatsapp/products` - Get products for WhatsApp

### 8. Supplier Portal Endpoints
- `GET /api/supplier/stores` - Geographic store filtering
- `GET /api/supplier/blockchain/transactions` - Blockchain transactions
- `GET /api/supplier/blockchain/verify` - Verify transaction

### 9. Admin Endpoints
- `POST /api/admin/inventory/seed` - Seed inventory

### 10. Credit Score with Limit
- `GET /api/shopkeeper/<id>/credit-score` - Get credit score with limit

## Expected Output

The script will:
1. Wait for server to start (if not already running)
2. Get test shopkeeper and cooperative IDs from database
3. Test all endpoints systematically
4. Display results for each test
5. Generate a summary report
6. Save detailed results to `new_endpoints_test_report.json`

## Understanding Test Results

- `[PASS]` - Test passed (status code matches expected)
- `[FAIL]` - Test failed (status code doesn't match expected)

**Note**: Some failures are expected:
- Authentication endpoints will fail without valid OTP
- Some supplier endpoints require authentication (will return 401/403)
- These are still tested to verify proper error handling

## Troubleshooting

### "Connection refused - Server not running"
- Make sure Flask server is running in Terminal 1
- Check that server is listening on `http://localhost:5000`

### "No shopkeepers found in database"
- Run the seeder: `python database\seeders\seed_data.py`

### "ModuleNotFoundError: No module named 'requests'"
- Make sure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`

### Tests failing with 401/403
- This is expected for endpoints requiring authentication
- The script tests error handling, so these failures are acceptable

## Test Report

After running, check `new_endpoints_test_report.json` for:
- Detailed results for each endpoint
- Response times
- Error messages (if any)
- Success rate by category

## Next Steps

After testing:
1. Review the test report
2. Check for any unexpected failures
3. Verify database operations (check MongoDB for created/updated records)
4. Test frontend integration with actual frontend applications

