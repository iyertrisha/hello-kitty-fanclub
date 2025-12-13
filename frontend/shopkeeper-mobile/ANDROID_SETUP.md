# Android Build Setup Guide

## Problem
You're getting: "No Java compiler found, please ensure you are running Gradle with a JDK"

## Solution: Install JDK 17

### Step 1: Download JDK 17
1. Go to: https://adoptium.net/temurin/releases/?version=17
2. Download **JDK 17** for Windows (x64)
3. Choose **.msi** installer

### Step 2: Install JDK 17
1. Run the installer
2. **Important**: Check "Set JAVA_HOME variable" during installation
3. Complete the installation

### Step 3: Verify Installation
Open PowerShell and run:
```powershell
java -version
```
Should show: `openjdk version "17.x.x"` or higher

### Step 4: Set JAVA_HOME (if not auto-set)
1. Open **System Properties** → **Environment Variables**
2. Under **System Variables**, click **New**
3. Variable name: `JAVA_HOME`
4. Variable value: `C:\Program Files\Eclipse Adoptium\jdk-17.x.x-hotspot` (or your JDK path)
5. Click **OK**

### Step 5: Update PATH
1. Find **Path** in System Variables
2. Click **Edit**
3. Add: `%JAVA_HOME%\bin`
4. Click **OK** on all dialogs

### Step 6: Configure Android Studio
1. Open **Android Studio**
2. Go to **File** → **Settings** (or **Android Studio** → **Preferences** on Mac)
3. Navigate to **Build, Execution, Deployment** → **Build Tools** → **Gradle**
4. Under **Gradle JDK**, select **JDK 17** (or **jbr-17** if available)
5. Click **Apply** and **OK**

### Step 7: Restart Everything
1. Close Android Studio
2. Close all PowerShell/Command Prompt windows
3. Restart your computer (recommended)

### Step 8: Try Building Again
```powershell
cd frontend\shopkeeper-mobile
npx expo run:android
```

## Alternative: Use Android Studio's Embedded JDK
If you have Android Studio installed:
1. Android Studio comes with its own JDK (usually JDK 17)
2. Find it at: `C:\Users\YourName\AppData\Local\Android\Sdk\jbr` or similar
3. Set JAVA_HOME to that path

## Quick Check Commands
```powershell
# Check Java version
java -version

# Check JAVA_HOME
echo $env:JAVA_HOME

# Check if javac (compiler) is available
javac -version
```



