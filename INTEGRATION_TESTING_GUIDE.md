# 🚀 Complete Integration Testing Guide
## Frontend + Backend + Blockchain

This guide will help you test all three components together.

---

## 📋 Prerequisites Checklist

- [ ] Node.js installed (`node --version`)
- [ ] Python installed (`python --version`)
- [ ] MongoDB running (`mongod` or MongoDB service)
- [ ] Virtual environment activated
- [ ] All dependencies installed

---

## 🎯 Step-by-Step Testing

### **Terminal 1: Start Blockchain (Hardhat Node)**

```powershell
cd helloKittyFanclub\backend\blockchain
npm run node
```

**Keep this terminal running!** You should see:
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/
```

---

### **Terminal 2: Deploy Contract (if not already deployed)**

```powershell
cd helloKittyFanclub\backend\blockchain
npm run deploy:localhost
```

**Copy the Contract Address** from the output (e.g., `0x5FbDB2315678afecb367f032d93F642f64180aa3`)

**Update `backend/blockchain/.env`:**
```env
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
RPC_URL=http://localhost:8545
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
ADMIN_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

**Also update `backend/.env`:**
```env
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
ADMIN_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
```

---

### **Terminal 3: Start Backend (Flask)**

```powershell
# Activate virtual environment
cd d:\whackiest
.\venv\Scripts\Activate.ps1

# Navigate to backend
cd helloKittyFanclub\backend

# Seed database (first time only)
python database\seeders\seed_data.py

# Start Flask server
python run.py
```

**You should see:**
```
✅ Connected to MongoDB: kirana_db
✅ Flask application initialized successfully
 * Running on http://0.0.0.0:5000
```

---

### **Terminal 4: Start Frontend (React)**

```powershell
cd helloKittyFanclub\frontend\admin-dashboard

# Install dependencies (first time only)
npm install

# Start React app
npm start
```

**The browser should automatically open** at `http://localhost:3000`

---

## ✅ Verification Steps

### 1. **Check Blockchain Status**

Open browser: `http://localhost:5000/api/blockchain/status`

Expected response:
```json
{
  "available": true,
  "configured": true,
  "contract_address": "0x5FbDB...",
  "network": "Local"
}
```

### 2. **Check Backend Health**

Open browser: `http://localhost:5000/api/admin/overview`

Expected: JSON response with stats

### 3. **Check Frontend**

Open browser: `http://localhost:3000`

You should see the Admin Dashboard with:
- Overview page
- Stores page
- Cooperatives page
- Analytics page
- Blockchain Logs page

---

## 🧪 Testing Scenarios

### **Scenario 1: View Overview**
1. Open `http://localhost:3000`
2. Click "Overview" in sidebar
3. Should see stats cards and charts

### **Scenario 2: View Stores**
1. Click "Stores" in sidebar
2. Should see list of stores from database
3. Try searching/filtering

### **Scenario 3: View Blockchain Logs**
1. Click "Blockchain Logs" in sidebar
2. Should see blockchain transactions (if any)
3. Check filters work

### **Scenario 4: Create Transaction (Test Full Flow)**
1. Use Postman or browser console:
   ```javascript
   fetch('http://localhost:5000/api/transactions', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       type: 'sale',
       amount: 100.50,
       shopkeeper_id: 'YOUR_SHOPKEEPER_ID',
       customer_id: 'YOUR_CUSTOMER_ID'
     })
   })
   ```
2. Check if it appears in frontend

### **Scenario 5: Test Blockchain Integration**
1. Register a shopkeeper on blockchain:
   ```javascript
   fetch('http://localhost:5000/api/blockchain/register-shopkeeper', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       address: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266'
     })
   })
   ```
2. Check blockchain logs in frontend

---

## 🔍 Troubleshooting

### **Problem: Frontend can't connect to backend**

**Solution:**
1. Check `frontend/admin-dashboard/src/services/api.js` has:
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
   ```
2. Create `.env.local` in `frontend/admin-dashboard/`:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```
3. Restart React app

### **Problem: Backend can't connect to blockchain**

**Solution:**
1. Make sure Hardhat node is running (Terminal 1)
2. Check `backend/.env` has correct `CONTRACT_ADDRESS`
3. Check `backend/blockchain/.env` has same values
4. Restart Flask server

### **Problem: CORS errors**

**Solution:**
1. Check `backend/.env` has:
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```
2. Restart Flask server

### **Problem: MongoDB connection failed**

**Solution:**
1. Make sure MongoDB is running
2. Check `backend/.env` has:
   ```
   MONGODB_URI=mongodb://localhost:27017/kirana_db
   ```
3. Run seed script: `python database\seeders\seed_data.py`

### **Problem: Frontend shows "No data"**

**Solution:**
1. Check browser console for errors
2. Check Network tab in DevTools
3. Verify backend is running on port 5000
4. Check backend logs for errors

---

## 📊 Expected Ports

| Service | Port | URL |
|---------|------|-----|
| Hardhat Node | 8545 | http://localhost:8545 |
| Flask Backend | 5000 | http://localhost:5000 |
| React Frontend | 3000 | http://localhost:3000 |
| MongoDB | 27017 | mongodb://localhost:27017 |

---

## 🎉 Success Indicators

✅ **All services running:**
- Terminal 1: Hardhat node showing "Started HTTP..."
- Terminal 3: Flask showing "Running on http://0.0.0.0:5000"
- Terminal 4: React showing "Compiled successfully!"

✅ **Frontend working:**
- Dashboard loads without errors
- Data appears in all pages
- No console errors

✅ **Backend working:**
- API endpoints return data
- No errors in Flask logs
- MongoDB connected

✅ **Blockchain working:**
- `/api/blockchain/status` returns `"available": true`
- Transactions can be recorded
- Blockchain logs appear in frontend

---

## 🚀 Quick Start Script

Save this as `start_all.ps1` in project root:

```powershell
# Start all services
Write-Host "Starting all services..." -ForegroundColor Green

# Terminal 1: Blockchain
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd helloKittyFanclub\backend\blockchain; npm run node"

# Wait a bit
Start-Sleep -Seconds 3

# Terminal 2: Deploy (if needed)
# Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd helloKittyFanclub\backend\blockchain; npm run deploy:localhost"

# Terminal 3: Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\whackiest; .\venv\Scripts\Activate.ps1; cd helloKittyFanclub\backend; python run.py"

# Wait a bit
Start-Sleep -Seconds 3

# Terminal 4: Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd helloKittyFanclub\frontend\admin-dashboard; npm start"

Write-Host "All services starting in separate windows!" -ForegroundColor Green
```

Run with: `.\start_all.ps1`

---

## 📝 Notes

- **Keep all terminals running** while testing
- **Hardhat node must be running** for blockchain to work
- **MongoDB must be running** for backend to work
- **Check browser console** for frontend errors
- **Check Flask terminal** for backend errors
- **Use DevTools Network tab** to see API calls

---

**Happy Testing! 🎉**

