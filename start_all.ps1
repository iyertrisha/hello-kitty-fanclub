# Start All Services - Frontend, Backend, Blockchain
# This script opens 3 separate PowerShell windows for each service

Write-Host "Starting All Services..." -ForegroundColor Green
Write-Host ""

# Get the current directory (should be helloKittyFanclub)
$currentDir = Get-Location
$blockchainDir = Join-Path $currentDir "backend\blockchain"
$backendDir = Join-Path $currentDir "backend"
$frontendDir = Join-Path $currentDir "frontend\admin-dashboard"
$projectRoot = Split-Path -Parent $currentDir

# Terminal 1: Start Hardhat Node (Blockchain)
Write-Host "Starting Hardhat Node (Terminal 1)..." -ForegroundColor Yellow
$blockchainCmd = "cd '$blockchainDir'; Write-Host 'Hardhat Node Starting...' -ForegroundColor Cyan; npm run node"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $blockchainCmd

# Wait for Hardhat to start
Write-Host "   Waiting 5 seconds for Hardhat to start..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Terminal 2: Start Flask Backend
Write-Host "Starting Flask Backend (Terminal 2)..." -ForegroundColor Yellow
$backendCmd = "cd '$projectRoot'; .\venv\Scripts\Activate.ps1; cd '$backendDir'; Write-Host 'Flask Backend Starting...' -ForegroundColor Cyan; python run.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# Wait for Flask to start
Write-Host "   Waiting 3 seconds for Flask to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Terminal 3: Start React Frontend
Write-Host "Starting React Frontend (Terminal 3)..." -ForegroundColor Yellow
$frontendCmd = "cd '$frontendDir'; Write-Host 'React Frontend Starting...' -ForegroundColor Cyan; npm start"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "All services are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "   1. Hardhat Node    -> http://localhost:8545" -ForegroundColor White
Write-Host "   2. Flask Backend    -> http://localhost:5000" -ForegroundColor White
Write-Host "   3. React Frontend   -> http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Wait for all services to start, then open:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Tip: Check each terminal window for startup messages" -ForegroundColor Gray
