# Quick script to register a test customer for WhatsApp bot testing
# Usage: .\register_test_customer.ps1 -Name "John Doe" -Phone "+919876543210"

param(
    [Parameter(Mandatory=$true)]
    [string]$Name,
    
    [Parameter(Mandatory=$true)]
    [string]$Phone,
    
    [string]$Address = "Test Address"
)

# Normalize phone number (remove any whitespace/newlines)
$Phone = $Phone -replace '\s+', ''

$apiUrl = "http://localhost:5000/api/customer"

$body = @{
    name = $Name
    phone = $Phone
    address = $Address
} | ConvertTo-Json

Write-Host "Registering customer..." -ForegroundColor Cyan
Write-Host "   Name: $Name" -ForegroundColor Gray
Write-Host "   Phone: $Phone" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method POST -ContentType "application/json" -Body $body
    
    Write-Host "SUCCESS: Customer registered successfully!" -ForegroundColor Green
    Write-Host "   Customer ID: $($response.id)" -ForegroundColor Gray
    Write-Host "   Name: $($response.name)" -ForegroundColor Gray
    Write-Host "   Phone: $($response.phone)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Now you can send WhatsApp messages to the bot!" -ForegroundColor Yellow
    Write-Host "   Try: 'hi' or 'How much do I owe?'" -ForegroundColor Gray
}
catch {
    Write-Host "ERROR: Failed to register customer" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}
