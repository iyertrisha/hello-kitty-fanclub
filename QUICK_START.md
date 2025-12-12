# ⚡ Quick Start - Test Everything Together

## 🎯 One-Command Start (Easiest)

```powershell
cd helloKittyFanclub
.\start_all.ps1
```

This opens 3 separate windows for:
1. **Hardhat Node** (Blockchain)
2. **Flask Backend** 
3. **React Frontend**

Then open: **http://localhost:3000**

---

## 📝 Manual Start (Step-by-Step)

### **Step 1: Start Blockchain** (Terminal 1)
```powershell
cd helloKittyFanclub\backend\blockchain
npm run node
```
✅ Keep this running!

### **Step 2: Start Backend** (Terminal 2)
```powershell
cd d:\whackiest
.\venv\Scripts\Activate.ps1
cd helloKittyFanclub\backend
python run.py
```
✅ Should see: "Running on http://0.0.0.0:5000"

### **Step 3: Start Frontend** (Terminal 3)
```powershell
cd helloKittyFanclub\frontend\admin-dashboard
npm start
```
✅ Browser opens at http://localhost:3000

---

## ✅ Quick Verification

1. **Backend Health**: http://localhost:5000/api/admin/overview
2. **Blockchain Status**: http://localhost:5000/api/blockchain/status
3. **Frontend**: http://localhost:3000

---

## 🔧 Before First Run

1. **Seed Database** (one time):
   ```powershell
   cd helloKittyFanclub\backend
   python database\seeders\seed_data.py
   ```

2. **Install Frontend Dependencies** (one time):
   ```powershell
   cd helloKittyFanclub\frontend\admin-dashboard
   npm install
   ```

3. **Check .env Files**:
   - `backend/.env` should have `CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3`
   - `backend/blockchain/.env` should have same contract address

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Frontend can't connect | Check backend is running on port 5000 |
| Blockchain not available | Make sure Hardhat node is running |
| MongoDB error | Start MongoDB service |
| CORS errors | Check `CORS_ORIGINS` in `backend/.env` |

---

**For detailed guide, see: `INTEGRATION_TESTING_GUIDE.md`**

