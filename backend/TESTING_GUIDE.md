# Backend Testing Guide

Quick guide for testing the backend API.

## Quick Start

1. **Start MongoDB:**
   ```bash
   # Windows
   Start-Service MongoDB
   
   # Linux/Mac
   sudo systemctl start mongod
   ```

2. **Activate virtual environment:**
   ```bash
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed database:**
   ```bash
   python database/seeders/seed_data.py
   ```

5. **Start server:**
   ```bash
   python run.py
   ```

6. **Run tests:**
   ```bash
   python test_all_endpoints.py
   ```

## Manual Testing with curl

```bash
# Get all transactions
curl http://localhost:5000/api/transactions

# Create transaction
curl -X POST http://localhost:5000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"sale","amount":100,"shopkeeper_id":"...","customer_id":"..."}'

# Get shopkeeper
curl http://localhost:5000/api/shopkeeper/<id>
```

## Manual Testing with PowerShell

```powershell
# Get overview
Invoke-RestMethod -Uri "http://localhost:5000/api/admin/overview" -Method GET

# Create customer
$body = @{
    name = "Test Customer"
    phone = "+919876543210"
    address = "Test Address"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/customer" -Method POST -Body $body -ContentType "application/json"
```

For detailed step-by-step instructions, see `MANUAL_STEPS.md`.

