# Opening Shopkeeper Mobile in Android Studio

This is an **Expo React Native** project. To open it in Android Studio, you need to generate the native Android project first.

## Prerequisites

1. **Android Studio** (latest version)
2. **Android SDK** (installed via Android Studio)
3. **Java JDK** (11 or higher)
4. **Node.js** and **npm** (already installed)
5. **Expo CLI**: `npm install -g expo-cli`

## Method 1: Generate Native Android Project (Recommended)

### Step 1: Navigate to Project Directory

```powershell
cd helloKittyFanclub\frontend\shopkeeper-mobile
```

### Step 2: Install Dependencies

```powershell
npm install
```

### Step 3: Generate Android Project

Expo can generate native Android/iOS folders without ejecting:

```powershell
npx expo prebuild --platform android
```

This will create an `android/` folder in your project.

### Step 4: Open in Android Studio

1. **Open Android Studio**
2. Click **"Open"** or **File → Open**
3. Navigate to: `helloKittyFanclub\frontend\shopkeeper-mobile\android`
4. Click **"OK"**
5. Wait for Gradle sync to complete

### Step 5: Run the App

**Option A: From Android Studio**
1. Click the green **"Run"** button
2. Select an emulator or connected device
3. The app will build and launch

**Option B: From Terminal (with Expo)**
```powershell
npm run android
```

## Method 2: Use Android Studio Emulator with Expo (Easier)

You can use Android Studio's emulator while keeping Expo's workflow:

### Step 1: Start Android Emulator

1. Open **Android Studio**
2. Go to **Tools → Device Manager**
3. Create/Start an Android Virtual Device (AVD)
4. Wait for emulator to boot

### Step 2: Run Expo

```powershell
cd helloKittyFanclub\frontend\shopkeeper-mobile
npm start
```

### Step 3: Launch on Android

```powershell
npm run android
```

Or press `a` in the Expo terminal to launch on Android emulator.

## Method 3: Full Eject (Advanced - Not Recommended)

⚠️ **Warning**: This permanently removes Expo's managed workflow. Only do this if you need full native control.

```powershell
npx expo eject
```

Then open the `android/` folder in Android Studio.

## Project Structure After Prebuild

After running `expo prebuild`, your structure will be:

```
shopkeeper-mobile/
├── android/          # Native Android project (generated)
│   ├── app/
│   ├── build.gradle
│   └── ...
├── ios/              # Native iOS project (if generated)
├── src/              # React Native source code
├── package.json
└── app.json
```

## Troubleshooting

### Issue: "expo prebuild" fails

**Solution:**
```powershell
# Clear cache and try again
npx expo prebuild --clean
```

### Issue: Gradle sync fails in Android Studio

**Solution:**
1. File → Invalidate Caches → Invalidate and Restart
2. Check Android SDK is installed: Tools → SDK Manager
3. Ensure Java JDK is set: File → Project Structure → SDK Location

### Issue: Build fails with "SDK not found"

**Solution:**
1. Open Android Studio
2. Tools → SDK Manager
3. Install:
   - Android SDK Platform 33 (or latest)
   - Android SDK Build-Tools
   - Android SDK Platform-Tools
4. Set `ANDROID_HOME` environment variable:
   ```powershell
   # In PowerShell
   $env:ANDROID_HOME = "C:\Users\YourName\AppData\Local\Android\Sdk"
   ```

### Issue: Metro bundler connection issues

**Solution:**
1. Ensure backend API is running
2. Check `API_BASE_URL` in `src/services/api.js`
3. For emulator, use `10.0.2.2` instead of `localhost`:
   ```javascript
   const API_BASE_URL = 'http://10.0.2.2:5000/api';
   ```

## Quick Start Commands

```powershell
# 1. Navigate to project
cd helloKittyFanclub\frontend\shopkeeper-mobile

# 2. Install dependencies
npm install

# 3. Generate Android project
npx expo prebuild --platform android

# 4. Open in Android Studio
# (Manually open android/ folder in Android Studio)

# OR use Expo workflow:
npm start
# Then press 'a' for Android
```

## Development Workflow

### With Native Android Project (Android Studio)

1. Make changes in `src/` folder
2. Build and run from Android Studio
3. Native code changes require rebuild

### With Expo (Recommended for React Native development)

1. Make changes in `src/` folder
2. Hot reload automatically updates
3. No rebuild needed for JS changes

## Notes

- **Expo Managed Workflow**: Use `npm start` and Expo Go app (easiest)
- **Bare Workflow**: Use `expo prebuild` + Android Studio (more control)
- **Native Code**: Only needed if you're adding native modules

## Recommended Approach

For most development, use **Method 2** (Expo + Android Studio Emulator):
- Faster development cycle
- Hot reload works
- No need to rebuild native code
- Can still debug in Android Studio

Only use **Method 1** if you need to:
- Modify native Android code
- Add custom native modules
- Debug native crashes
- Build production APK manually

