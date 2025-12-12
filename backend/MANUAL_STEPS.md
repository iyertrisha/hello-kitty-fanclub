# Manual Steps to Test the Backend

Follow these steps in order. The seeder script has been fixed and should work now.

## Prerequisites Checklist

- [ ] MongoDB is installed and running
- [ ] Python 3.9+ is installed
- [ ] Virtual environment (`venv`) exists in project root
- [ ] `.env` file exists in `backend/` directory

---

## Step 1: Activate Virtual Environment

Open PowerShell and run:

```powershell
cd D:\whackiest\helloKittyFanclub
.\venv\Scripts\Activate.ps1
cd backend
```

You should see `(venv)` in your prompt.

---

## Step 2: Install Dependencies (if not already done)

```powershell
pip install -r requirements.txt
```

This installs Flask, MongoEngine, and all other dependencies. Wait for it to complete.

---

## Step 3: Verify MongoDB is Running

```powershell
# Check if MongoDB service is running (Windows)
Get-Service -Name MongoDB

# Or test connection
mongosh --eval "db.version()"
```

If MongoDB is not running:
- Start MongoDB service: `Start-Service MongoDB`
- Or start manually: `mongod`

---

## Step 4: Verify .env File

Make sure `backend/.env` exists and has at least:

```
MONGODB_URI=mongodb://localhost:27017/kirana_db
MONGODB_DB_NAME=kirana_db
SECRET_KEY=dev-secret-key-change-in-production
```

If `.env` doesn't exist, copy from `.env.template` and fill in values.

---

## Step 5: Seed the Database

```powershell
python database\seeders\seed_data.py
```

**Expected Output:**
```
INFO:__main__:Starting database seeding...
INFO:__main__:Created shopkeeper: Rajesh Kirana Store
INFO:__main__:Created shopkeeper: Priya Grocery
...
INFO:__main__:✅ Database seeding completed!
  - Shopkeepers: 8
  - Customers: 25
  - Products: 96
  - Transactions: 150
  - Cooperatives: 3
```

If you get `ModuleNotFoundError: No module named 'mongoengine'`:
- Make sure venv is activated (you see `(venv)` in prompt)
- Run `pip install -r requirements.txt` again

---

## Step 6: Start the Flask Server

```powershell
python run.py
```

**Expected Output:**
```
2025-12-12 13:13:58,911 - api - INFO - ✅ Connected to MongoDB: kirana_db
2025-12-12 13:13:58,912 - api - INFO - ✅ Flask application initialized successfully
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Keep this terminal open!** The server must be running to test endpoints.

---

## Step 7: Test Endpoints (in a NEW PowerShell window)

Open a **new PowerShell window** (keep the server running in the first one).

### Test 1: Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/admin/overview" -Method GET
```

### Test 2: Get Shopkeepers
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/admin/stores" -Method GET
```

### Test 3: Get Transactions
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/transactions" -Method GET
```

---

## Common Issues and Fixes

### Issue: `ModuleNotFoundError: No module named 'database'`
**Fix:** The seeder script has been fixed. Make sure you're running it from the `backend/` directory with venv activated.

### Issue: `ModuleNotFoundError: No module named 'mongoengine'`
**Fix:** 
1. Verify venv is activated: `(venv)` should appear in prompt
2. Install dependencies: `pip install -r requirements.txt`

### Issue: `Connection refused` or MongoDB errors
**Fix:**
1. Check MongoDB is running: `Get-Service MongoDB`
2. Start MongoDB: `Start-Service MongoDB`
3. Verify connection string in `.env` file

### Issue: `Address already in use` when starting server
**Fix:** Port 5000 is already in use. Either:
- Stop the other process using port 5000
- Change `FLASK_PORT` in `.env` to a different port (e.g., 5001)

---

## Quick Test Script

You can also use the automated test script (once server is running):

```powershell
python test_all_endpoints.py
```

This will test all endpoints and generate a report.

---

## Summary

**What you need to do manually:**

1. ✅ Activate venv: `.\venv\Scripts\Activate.ps1`
2. ✅ Install dependencies: `pip install -r requirements.txt` (if not done)
3. ✅ Ensure MongoDB is running
4. ✅ Verify `.env` file exists and is configured
5. ✅ Seed database: `python database\seeders\seed_data.py`
6. ✅ Start server: `python run.py` (keep running)
7. ✅ Test endpoints in a new terminal window

The seeder script import issue has been **fixed** - it should work now!

