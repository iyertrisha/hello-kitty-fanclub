# PowerShell script to start WhatsApp Bot
# Usage: .\start.ps1

Write-Host "🚀 Starting WhatsApp Debt Tracking Bot..." -ForegroundColor Green

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" -Destination ".env"
        Write-Host "✅ Created .env file. Please edit it with your configuration." -ForegroundColor Green
    } else {
        Write-Host "❌ .env.template not found" -ForegroundColor Red
        exit 1
    }
}

# Start the bot
Write-Host "✅ Starting bot..." -ForegroundColor Green
node index.js

