# cleanup.ps1 - Clean up WhatsApp bot session and processes
Write-Host "Cleaning up WhatsApp bot..." -ForegroundColor Yellow

# Stop Node.js processes related to the bot
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*whatsapp-bot*" -or $_.CommandLine -like "*whatsapp-bot*"
}

if ($nodeProcesses) {
    Write-Host "   Stopping Node.js processes..." -ForegroundColor Gray
    $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Stop Chrome/Chromium processes
$chromeProcesses = Get-Process | Where-Object {
    $_.ProcessName -like "*chrome*" -or $_.ProcessName -like "*chromium*"
}

if ($chromeProcesses) {
    Write-Host "   Stopping Chrome/Chromium processes..." -ForegroundColor Gray
    $chromeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
}

# Wait for processes to fully terminate
Start-Sleep -Seconds 3

# Delete session folder
$sessionPath = ".\.wwebjs_auth"
if (Test-Path $sessionPath) {
    Write-Host "   Deleting session folder..." -ForegroundColor Gray
    try {
        Remove-Item -Recurse -Force $sessionPath -ErrorAction Stop
        Write-Host "   [OK] Session folder deleted" -ForegroundColor Green
    } catch {
        Write-Host "   [WARNING] Could not delete session folder (may be locked)" -ForegroundColor Yellow
        Write-Host "   Try closing all browser windows and running this script again" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   [INFO] No session folder found" -ForegroundColor Gray
}

Write-Host "[OK] Cleanup complete!" -ForegroundColor Green
Write-Host "You can now run: npm start" -ForegroundColor Cyan

