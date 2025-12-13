# Test Android Emulator Connectivity to Flask Server
# This script helps diagnose network connectivity issues

Write-Host "Testing Android Emulator Connectivity..." -ForegroundColor Green
Write-Host ""

$port = 5000

# Test 1: Check if Flask server is listening
Write-Host "Test 1: Checking if port $port is listening..." -ForegroundColor Cyan
$listening = Test-NetConnection -ComputerName localhost -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
if ($listening) {
    Write-Host "✅ Port $port is listening on localhost" -ForegroundColor Green
} else {
    Write-Host "❌ Port $port is NOT listening. Is Flask server running?" -ForegroundColor Red
    exit 1
}

# Test 2: Check firewall rule
Write-Host ""
Write-Host "Test 2: Checking firewall rules..." -ForegroundColor Cyan
$firewallRule = Get-NetFirewallRule -DisplayName "Flask Development Server - Port $port" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "✅ Firewall rule exists:" -ForegroundColor Green
    $firewallRule | Format-Table DisplayName, Enabled, Direction, Action -AutoSize
} else {
    Write-Host "❌ Firewall rule not found. Run configure_firewall.ps1 as Administrator" -ForegroundColor Red
}

# Test 3: Get network IP addresses
Write-Host ""
Write-Host "Test 3: Network configuration..." -ForegroundColor Cyan
$networkIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object IPAddress, InterfaceAlias
if ($networkIPs) {
    Write-Host "✅ Network IP addresses found:" -ForegroundColor Green
    $networkIPs | Format-Table -AutoSize
    Write-Host ""
    Write-Host "Try using one of these IPs in your Flutter app instead of 10.0.2.2:" -ForegroundColor Yellow
    foreach ($ip in $networkIPs) {
        Write-Host "   http://$($ip.IPAddress):$port/api" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  No network IP addresses found" -ForegroundColor Yellow
}

# Test 4: Test connection from localhost
Write-Host ""
Write-Host "Test 4: Testing localhost connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$port/api/test" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Localhost connection successful" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Localhost connection failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 60
Write-Host "Diagnostics complete!" -ForegroundColor Green
Write-Host ""
Write-Host "If emulator still can't connect:" -ForegroundColor Yellow
Write-Host "1. Try using the network IP address shown above instead of 10.0.2.2" -ForegroundColor White
Write-Host "2. Check Windows Defender Firewall for additional blocking rules" -ForegroundColor White
Write-Host "3. Disable antivirus temporarily to test" -ForegroundColor White
Write-Host "4. Restart the Android emulator" -ForegroundColor White
Write-Host "=" * 60

