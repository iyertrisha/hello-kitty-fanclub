# Windows Firewall Configuration Script for Flask Development Server
# Run this script as Administrator to allow Flask server connections

Write-Host "Configuring Windows Firewall for Flask Development Server..." -ForegroundColor Green
Write-Host ""

$port = 5000
$ruleName = "Flask Development Server - Port $port"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Remove existing rule if it exists
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if ($existingRule) {
    Write-Host "Removing existing firewall rule..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
}

# Create new firewall rule for port
try {
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -LocalPort $port `
        -Protocol TCP `
        -Action Allow `
        -Description "Allows Flask development server on port $port for Android emulator connections" | Out-Null
    
    # Also allow Python.exe specifically (more permissive)
    $pythonRuleName = "Python - Flask Development Server"
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonExe) {
        $pythonExe = (Get-Command py -ErrorAction SilentlyContinue).Source
    }
    
    if ($pythonExe) {
        $existingPythonRule = Get-NetFirewallRule -DisplayName $pythonRuleName -ErrorAction SilentlyContinue
        if ($existingPythonRule) {
            Remove-NetFirewallRule -DisplayName $pythonRuleName -ErrorAction SilentlyContinue
        }
        
        New-NetFirewallRule -DisplayName $pythonRuleName `
            -Direction Inbound `
            -Program $pythonExe `
            -Action Allow `
            -Description "Allows Python Flask development server for Android emulator connections" | Out-Null
        Write-Host "✅ Also created rule for Python.exe: $pythonExe" -ForegroundColor Green
    }
    
    Write-Host "✅ Firewall rule created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Rule Details:" -ForegroundColor Cyan
    Write-Host "   Name: $ruleName" -ForegroundColor White
    Write-Host "   Port: $port" -ForegroundColor White
    Write-Host "   Protocol: TCP" -ForegroundColor White
    Write-Host "   Action: Allow" -ForegroundColor White
    Write-Host ""
    Write-Host "You can now connect from Android emulator using:" -ForegroundColor Green
    Write-Host "   http://10.0.2.2:$port/api" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Failed to create firewall rule: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Firewall configuration complete!" -ForegroundColor Green

