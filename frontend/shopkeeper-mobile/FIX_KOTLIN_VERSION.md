# Fix: Kotlin Version Error in Android Studio

## Problem
```
Can't find KSP version for Kotlin version '1.9.24'. 
You're probably using an unsupported version of Kotlin. 
Supported versions are: '2.2.20, 2.2.10, 2.2.0, 2.1.21, 2.1.20, 2.1.10, 2.1.0, 2.0.21, 2.0.20, 2.0.10, 2.0.0'
```

## Solution Applied

### 1. Updated `android/build.gradle`
Added explicit Kotlin version:
```gradle
buildscript {
  ext {
    kotlinVersion = '2.0.21'
  }
  dependencies {
    classpath("org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlinVersion")
  }
}
```

### 2. Updated `android/gradle.properties`
Added Kotlin version property:
```properties
kotlinVersion=2.0.21
```

## Next Steps

1. **Sync Gradle in Android Studio:**
   - Click "Sync Now" when prompted
   - Or: File → Sync Project with Gradle Files

2. **If sync still fails, try:**
   ```powershell
   cd helloKittyFanclub\frontend\shopkeeper-mobile\android
   .\gradlew clean
   ```

3. **Then rebuild:**
   - In Android Studio: Build → Rebuild Project
   - Or from terminal: `.\gradlew build`

## Alternative: Regenerate Android Project

If the issue persists, you can regenerate the Android project:

```powershell
cd helloKittyFanclub\frontend\shopkeeper-mobile

# Remove existing android folder
Remove-Item -Recurse -Force android

# Regenerate with latest Expo
npx expo prebuild --platform android --clean
```

## Verification

After syncing, check that:
- ✅ Gradle sync completes without errors
- ✅ Kotlin version shows as 2.0.21 in build output
- ✅ Project builds successfully

## Notes

- Expo SDK 54+ requires Kotlin 2.0.0 or higher
- The error occurred because Expo's plugin couldn't find a KSP (Kotlin Symbol Processing) version for Kotlin 1.9.24
- KSP is required for code generation in modern Android projects

