# Complete Setup Guide - React Native Mobile App + React.js Admin Dashboard

This guide provides step-by-step instructions to set up and run both frontend applications.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Mobile App Setup](#mobile-app-setup)
4. [Admin Dashboard Setup](#admin-dashboard-setup)
5. [Running Everything](#running-everything)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Software

1. **Node.js** (v16 or higher)
   - Download from: https://nodejs.org/
   - Verify: `node --version`

2. **npm** or **yarn**
   - Comes with Node.js
   - Verify: `npm --version`

3. **Python 3.8+** (for backend)
   - Download from: https://www.python.org/

4. **MongoDB** (for backend database)
   - Download from: https://www.mongodb.com/try/download/community

5. **Expo CLI** (for mobile app)
   ```bash
   npm install -g expo-cli
   ```

6. **Git** (optional, for version control)
   - Download from: https://git-scm.com/

### For Mobile App Development

- **iOS Development** (Mac only):
  - Xcode from App Store
  - iOS Simulator

- **Android Development**:
  - Android Studio
  - Android SDK
  - Android Emulator

- **Physical Device Testing**:
  - Expo Go app (iOS/Android)

## 🚀 Backend Setup

**Note:** Ensure the Flask API backend is running before starting the frontend apps.

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

4. Start MongoDB:
   ```bash
   # Windows
   mongod

   # Mac/Linux
   sudo systemctl start mongod
   ```

5. Start Flask API:
   ```bash
   python app.py
   # or
   flask run
   ```

6. Verify API is running:
   - Open: http://localhost:5000/api
   - Should see API response or documentation

## 📱 Mobile App Setup

### Step 1: Navigate to Mobile App Directory

```bash
cd frontend/shopkeeper-mobile
```

### Step 2: Install Dependencies

```bash
npm install
```

**Note:** If you encounter errors:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Step 3: Configure API Endpoint

Edit `src/services/api.js`:

```javascript
// For local development
const API_BASE_URL = 'http://localhost:5000/api';

// For physical device testing, use your computer's IP:
// const API_BASE_URL = 'http://192.168.1.XXX:5000/api';
```

**To find your IP address:**
- Windows: `ipconfig` (look for IPv4 Address)
- Mac/Linux: `ifconfig` or `ip addr`

### Step 4: Start the App

```bash
npm start
```

This will:
- Start Metro bundler
- Display QR code
- Open Expo DevTools

### Step 5: Run on Device/Simulator

**Option A: Physical Device**
1. Install Expo Go app:
   - iOS: [App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Scan QR code:
   - iOS: Use Camera app
   - Android: Use Expo Go app

**Option B: iOS Simulator (Mac only)**
```bash
npm run ios
```

**Option C: Android Emulator**
```bash
npm run android
```

## 💻 Admin Dashboard Setup

### Step 1: Navigate to Dashboard Directory

```bash
cd frontend/admin-dashboard
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure API Endpoint

Edit `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Step 4: Start Development Server

```bash
npm start
```

The dashboard will:
- Start on http://localhost:3000
- Open automatically in your browser
- Hot-reload on file changes

## 🎯 Running Everything

### Complete Startup Sequence

1. **Terminal 1 - Backend API:**
   ```bash
   cd backend
   python app.py
   ```

2. **Terminal 2 - Mobile App:**
   ```bash
   cd frontend/shopkeeper-mobile
   npm start
   ```

3. **Terminal 3 - Admin Dashboard:**
   ```bash
   cd frontend/admin-dashboard
   npm start
   ```

### Quick Start Script (Optional)

Create `start-all.sh` (Mac/Linux):

```bash
#!/bin/bash
# Start Backend
cd backend && python app.py &
BACKEND_PID=$!

# Start Mobile App
cd frontend/shopkeeper-mobile && npm start &
MOBILE_PID=$!

# Start Admin Dashboard
cd frontend/admin-dashboard && npm start &
DASHBOARD_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Mobile App PID: $MOBILE_PID"
echo "Dashboard PID: $DASHBOARD_PID"

# Wait for user interrupt
wait
```

Create `start-all.bat` (Windows):

```batch
@echo off
start "Backend" cmd /k "cd backend && python app.py"
start "Mobile App" cmd /k "cd frontend/shopkeeper-mobile && npm start"
start "Admin Dashboard" cmd /k "cd frontend/admin-dashboard && npm start"
```

## ✅ Testing

### Mobile App Testing Checklist

- [ ] App launches successfully
- [ ] Dashboard displays stats
- [ ] Voice recording works (test on physical device)
- [ ] Transaction creation works
- [ ] Credit score displays
- [ ] Inventory CRUD operations work
- [ ] Cooperative join/leave works
- [ ] Offline mode saves transactions
- [ ] Sync works when back online

### Admin Dashboard Testing Checklist

- [ ] Dashboard loads
- [ ] Overview page shows stats
- [ ] Store management table displays
- [ ] Search and filter work
- [ ] Cooperative creation works
- [ ] Analytics charts render
- [ ] Blockchain logs display
- [ ] All API calls succeed

## 🔍 Troubleshooting

### Common Issues

#### 1. Mobile App Won't Connect to API

**Problem:** "Network request failed" or connection errors

**Solutions:**
- Ensure backend is running on port 5000
- For physical device, use computer's IP instead of localhost
- Check firewall settings
- Verify API_BASE_URL in `src/services/api.js`

#### 2. CORS Errors

**Problem:** CORS policy errors in browser/console

**Solutions:**
- Ensure backend has CORS enabled
- Add frontend origins to CORS whitelist:
  ```python
  # In Flask backend
  CORS(app, origins=["http://localhost:3000", "exp://192.168.1.XXX:8081"])
  ```

#### 3. Metro Bundler Issues

**Problem:** Metro bundler won't start or crashes

**Solutions:**
```bash
# Clear cache
npm start -- --reset-cache

# Or
expo start -c
```

#### 4. Dependency Installation Errors

**Problem:** npm install fails

**Solutions:**
```bash
# Clear everything
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### 5. Voice Recording Not Working

**Problem:** Microphone permissions or recording fails

**Solutions:**
- Test on physical device (simulator may not support audio)
- Check app permissions in device settings
- Ensure expo-av is installed: `npm install expo-av`

#### 6. Charts Not Rendering

**Problem:** Recharts charts don't display

**Solutions:**
- Ensure Recharts is installed: `npm install recharts`
- Check browser console for errors
- Verify data format matches chart expectations

#### 7. Navigation Errors

**Problem:** Navigation not working in mobile app

**Solutions:**
- Ensure React Navigation is installed
- Clear cache: `npm start -- --reset-cache`
- Check navigation setup in `src/navigation/AppNavigator.js`

### Getting Help

1. Check browser/device console for errors
2. Review API response format
3. Verify all dependencies are installed
4. Check network connectivity
5. Review individual README files:
   - `frontend/shopkeeper-mobile/README.md`
   - `frontend/admin-dashboard/README.md`

## 📚 Additional Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [React Documentation](https://react.dev/)
- [Recharts Documentation](https://recharts.org/)

## 🎉 Next Steps

After setup:

1. **Configure Authentication** (if required)
2. **Set up Environment Variables** for production
3. **Test All Features** thoroughly
4. **Deploy to Production** when ready

## 📝 Notes

- Mobile app uses Expo for easier development
- Admin dashboard uses Create React App
- Both apps connect to the same Flask API backend
- Ensure backend is running before testing frontend apps
- Use physical device for testing voice recording features

---

**Happy Coding! 🚀**



