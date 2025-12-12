# MongoDB Setup Guide

## Quick Setup: MongoDB Atlas (Cloud - Recommended)

MongoDB Atlas is free and doesn't require installation. Perfect for development!

### Step 1: Create MongoDB Atlas Account

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up with your email (or use Google/GitHub)
3. Choose the **FREE** tier (M0 Sandbox)

### Step 2: Create a Cluster

1. After signup, you'll be asked to create a cluster
2. Choose:
   - **Cloud Provider:** AWS (or any)
   - **Region:** Choose closest to you (e.g., `us-east-1`)
   - **Cluster Tier:** **M0 Sandbox** (FREE)
3. Click "Create Cluster" (takes 3-5 minutes)

### Step 3: Create Database User

1. In the left sidebar, click **"Database Access"**
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Enter:
   - **Username:** `kirana_user` (or any username)
   - **Password:** Create a strong password (save it!)
5. Under "Database User Privileges", select **"Read and write to any database"**
6. Click **"Add User"**

### Step 4: Whitelist Your IP Address

1. In the left sidebar, click **"Network Access"**
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (for development)
   - Or add your current IP: Click "Add Current IP Address"
4. Click **"Confirm"**

### Step 5: Get Connection String

1. Go back to **"Clusters"** (left sidebar)
2. Click **"Connect"** button on your cluster
3. Choose **"Connect your application"**
4. Select **"Python"** and version **"3.6 or later"**
5. Copy the connection string (looks like):
   ```
   mongodb+srv://kirana_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 6: Update Your .env File

1. Open `whackiest/backend/.env`
2. Replace the `MONGODB_URI` line with your connection string:
   ```env
   MONGODB_URI=mongodb+srv://kirana_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/kirana_db?retryWrites=true&w=majority
   ```
   **Important:** Replace:
   - `<password>` with your actual password
   - Keep `kirana_db` as the database name (or change it if you want)

3. Save the file

### Step 7: Test Connection

Restart your Flask backend and try the OTP again!

---

## Alternative: Install MongoDB Locally

If you prefer local MongoDB:

### Windows Installation

1. **Download MongoDB Community Server:**
   - Go to: https://www.mongodb.com/try/download/community
   - Select:
     - Version: Latest (7.0+)
     - Platform: Windows
     - Package: MSI
   - Click "Download"

2. **Install:**
   - Run the installer
   - Choose "Complete" installation
   - **IMPORTANT:** Check "Install MongoDB as a Service"
   - Check "Install MongoDB Compass" (GUI tool - optional)
   - Click "Install"

3. **Verify Installation:**
   ```powershell
   mongod --version
   ```

4. **Start MongoDB:**
   ```powershell
   net start MongoDB
   ```

5. **Your .env should already be correct:**
   ```env
   MONGODB_URI=mongodb://localhost:27017/kirana_db
   ```

---

## Troubleshooting

### MongoDB Atlas Connection Issues

- **"Authentication failed"**: Check your username/password in the connection string
- **"IP not whitelisted"**: Make sure you added your IP in Network Access
- **"Timeout"**: Check your internet connection

### Local MongoDB Issues

- **"Service not found"**: MongoDB wasn't installed as a service. Reinstall with "Install as Service" checked.
- **"Port 27017 in use"**: Another application is using MongoDB's port. Stop it or change MongoDB's port.

---

## Quick Test

After setup, test your connection:

```powershell
cd whackiest\backend
python -c "from database.models import connect_db; connect_db(); print('✅ MongoDB connected!')"
```

---

**Recommendation:** Use MongoDB Atlas for development - it's faster to set up and works immediately!

