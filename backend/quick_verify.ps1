# Quick Verification Script
Write-Host "=== Backend Verification ===" -ForegroundColor Cyan
Write-Host ""

# Check .env file
Write-Host "1. Checking .env file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "   [OK] .env file exists" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] .env file missing! Run: Copy-Item env.template -Destination .env" -ForegroundColor Red
}

# Check MongoDB
Write-Host "2. Checking MongoDB..." -ForegroundColor Yellow
$mongoService = Get-Service -Name MongoDB -ErrorAction SilentlyContinue
if ($mongoService -and $mongoService.Status -eq 'Running') {
    Write-Host "   [OK] MongoDB service is running" -ForegroundColor Green
} else {
    Write-Host "   [WARN] MongoDB service not found or not running" -ForegroundColor Yellow
    Write-Host "      Run: Start-Service MongoDB" -ForegroundColor Yellow
}

# Check port 27017
$portTest = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($portTest) {
    Write-Host "   [OK] MongoDB port 27017 is accessible" -ForegroundColor Green
} else {
    Write-Host "   [WARN] MongoDB port 27017 is not accessible" -ForegroundColor Yellow
}

# Check venv
Write-Host "3. Checking virtual environment..." -ForegroundColor Yellow
if (Test-Path venv) {
    Write-Host "   [OK] Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Virtual environment missing! Run: python -m venv venv" -ForegroundColor Red
}

# Check dependencies
Write-Host "4. Checking dependencies..." -ForegroundColor Yellow
if (Test-Path venv) {
    & .\venv\Scripts\python.exe verify_dependencies.py 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] All dependencies verified" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] Dependency verification failed" -ForegroundColor Red
    }
} else {
    Write-Host "   [SKIP] Skipping (venv not found)" -ForegroundColor Yellow
}

# Check MongoDB connection
Write-Host "5. Checking MongoDB connection..." -ForegroundColor Yellow
if (Test-Path venv) {
    & .\venv\Scripts\python.exe test_mongodb.py 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] MongoDB connection successful" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] MongoDB connection failed" -ForegroundColor Red
    }
} else {
    Write-Host "   [SKIP] Skipping (venv not found)" -ForegroundColor Yellow
}

# Check backend server
Write-Host "6. Checking backend server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:5000/health -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   [OK] Backend server is running on port 5000" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Backend server responded with status $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [WARN] Backend server is not running or not accessible" -ForegroundColor Yellow
    Write-Host "      Run: .\venv\Scripts\python.exe run.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Verification Complete ===" -ForegroundColor Cyan

