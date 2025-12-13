# Shopkeeper Mobile App

React Native CLI mobile application for shopkeepers to manage transactions, inventory, credit scores, and cooperatives.

## Prerequisites

- **Node.js** (v18 or higher)
- **npm** or **yarn**
- **Android Studio** with Android SDK (API 33+)
- **Java Development Kit (JDK)** 17 or higher
- **Physical Android device** or **Android Emulator**

## Installation

### 1. Install Dependencies

```bash
cd frontend/ShopkeeperMobile
npm install
```

### 2. Android Studio Setup

1. Install Android Studio from https://developer.android.com/studio
2. Open Android Studio and install Android SDK (API 33+)
3. Set environment variables (Windows):
   - `ANDROID_HOME` = `C:\Users\YourName\AppData\Local\Android\Sdk`
   - Add to PATH: `%ANDROID_HOME%\platform-tools`

### 3. Verify Setup

```bash
# Check Java version
java -version

# Check Android SDK
adb --version

# Check connected devices
adb devices
```

## Running the App

### Development Mode

**Terminal 1 - Start Metro Bundler:**
```bash
npm start
```

**Terminal 2 - Run on Android:**
```bash
npm run android
```

### Running on Physical Device

1. **Enable USB Debugging** on your Android device:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"
   - Connect device via USB

2. **Verify device connection:**
   ```bash
   adb devices
   ```

3. **Run the app:**
   ```bash
   npm run android
   ```

### Network Configuration for Device Testing

1. **Find your computer's IP address:**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. **Update API base URL** in `src/services/api.js`:
   ```javascript
   const API_BASE_URL = 'http://192.168.1.XXX:5000/api'; // Use your IP
   ```

3. **Ensure backend runs on network interface:**
   ```python
   # In Flask backend
   app.run(host='0.0.0.0', port=5000)
   ```

## Project Structure

```
src/
├── screens/          # Screen components
├── components/       # Reusable components
├── navigation/       # Navigation configuration
├── services/         # API and storage services
├── utils/            # Utility functions
└── hooks/            # Custom React hooks
```

## Features

- ✅ Voice recording and playback
- ✅ Transaction recording (add, view, edit)
- ✅ Credit score with blockchain verification badge
- ✅ Inventory management (list, add, update stock)
- ✅ Cooperative membership interface
- ✅ Offline data sync

## Development

### Hot Reload

- Shake device → Enable "Fast Refresh"
- Or press `R` in Metro bundler terminal

### Debugging

- Shake device → "Debug" → Opens Chrome DevTools
- View logs: `adb logcat | grep ReactNativeJS`

### Common Commands

```bash
# Clear cache
npm start -- --reset-cache

# Clean Android build
cd android && ./gradlew clean && cd ..

# Reinstall dependencies
rm -rf node_modules && npm install
```

## Testing Checklist

- [ ] App launches on device
- [ ] Navigation works between screens
- [ ] Voice recording works
- [ ] Audio playback works
- [ ] Transaction creation works
- [ ] Inventory management works
- [ ] Cooperative join/leave works
- [ ] Offline mode saves data
- [ ] Sync works when online
- [ ] API calls work with backend

## Troubleshooting

**Issue: "Android SDK not found"**
- Ensure Android Studio is installed
- Set `ANDROID_HOME` environment variable
- Restart terminal

**Issue: "Device not found"**
- Enable USB debugging on device
- Accept "Allow USB Debugging" prompt
- Try different USB cable/port

**Issue: "Network request failed"**
- Verify backend is running
- Check API_BASE_URL uses computer's IP (not localhost)
- Ensure backend runs on `0.0.0.0:5000`
- Check firewall settings

**Issue: "Voice recording not working"**
- Check microphone permissions
- Test on physical device (simulator may not support audio)
- Verify `react-native-audio-recorder-player` is properly linked

## Backend Integration

When backend is ready:

1. Update `API_BASE_URL` in `src/services/api.js`
2. Uncomment real API calls in `src/services/api.js`
3. Comment out mock API calls
4. Test all endpoints

## Building for Production

### Android APK

```bash
cd android
./gradlew assembleRelease
```

APK will be at: `android/app/build/outputs/apk/release/app-release.apk`

## License

Private project
