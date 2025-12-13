# How to Update JDK Globally on Windows

## Step-by-Step Guide

### Step 1: Download JDK 17

1. Go to: **https://adoptium.net/temurin/releases/?version=17**
2. Select:
   - **Version**: 17 (LTS)
   - **Operating System**: Windows
   - **Architecture**: x64
   - **Package Type**: JDK
3. Click **Download** (choose the `.msi` installer)

### Step 2: Uninstall Old Java (Optional but Recommended)

1. Open **Settings** → **Apps** → **Apps & features**
2. Search for "Java"
3. Uninstall all old Java versions (Java 8, etc.)
4. **Keep Android Studio's JDK** if you have it installed

### Step 3: Install JDK 17

1. Run the downloaded `.msi` installer
2. Click **Next** through the installation wizard
3. **IMPORTANT**: Check these options:
   - ✅ **Set JAVA_HOME variable**
   - ✅ **Add to PATH**
   - ✅ **Install JavaSoft (Oracle) registry keys**
4. Click **Install**
5. Wait for installation to complete
6. Click **Close**

### Step 4: Verify Installation

Open **PowerShell** (as Administrator) and run:

```powershell
java -version
```

Should show:
```
openjdk version "17.0.x" ...
```

### Step 5: Set JAVA_HOME Manually (If Not Auto-Set)

1. Press **Windows Key + R**
2. Type: `sysdm.cpl` and press Enter
3. Go to **Advanced** tab
4. Click **Environment Variables**
5. Under **System Variables**, click **New**
6. Enter:
   - **Variable name**: `JAVA_HOME`
   - **Variable value**: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot`
     (Replace `x` with your actual version number)
7. Click **OK**

**To find your JDK path:**
- Usually: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot`
- Or: `C:\Program Files\Java\jdk-17`
- Check: `C:\Program Files` folder

### Step 6: Update PATH Variable

1. In **Environment Variables** window
2. Find **Path** in **System Variables**
3. Click **Edit**
4. Check if these exist (if not, add them):
   - `%JAVA_HOME%\bin`
   - `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot\bin`
5. Click **OK** on all dialogs

### Step 7: Verify Everything Works

Open **NEW PowerShell** window and run:

```powershell
# Check Java version
java -version

# Check compiler
javac -version

# Check JAVA_HOME
echo $env:JAVA_HOME

# Should show the JDK path
```

### Step 8: Restart Applications

1. **Close all**:
   - PowerShell windows
   - Command Prompt windows
   - Android Studio
   - Any IDE (VS Code, etc.)
2. **Restart your computer** (recommended)
3. Open new terminal and verify again

## Quick PowerShell Commands (Alternative Method)

If you prefer command line, run PowerShell **as Administrator**:

```powershell
# Set JAVA_HOME permanently
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot', 'Machine')

# Add to PATH
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
$newPath = "$currentPath;C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot\bin"
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')
```

**Replace the path** with your actual JDK installation path.

## Troubleshooting

### If `java -version` still shows old version:

1. Check which Java is being used:
   ```powershell
   where.exe java
   ```

2. Remove old Java paths from PATH:
   - Remove any paths pointing to Java 8 or older versions
   - Keep only JDK 17 path

3. Restart computer

### If JAVA_HOME is not set:

1. Find your JDK installation:
   ```powershell
   dir "C:\Program Files\Eclipse Adoptium"
   ```

2. Set it manually (see Step 5 above)

### Verify in Android Studio:

1. Open Android Studio
2. **File** → **Settings** → **Build, Execution, Deployment** → **Build Tools** → **Gradle**
3. Under **Gradle JDK**, select **JDK 17** or your installed JDK
4. Click **Apply** and **OK**

## After Update

Try building your Android app:

```powershell
cd frontend\shopkeeper-mobile
npx expo run:android
```

It should now work! 🎉



