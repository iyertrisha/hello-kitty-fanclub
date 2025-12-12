# WhatsApp Bot Usage Guide

## ✅ Current Status

Your WhatsApp bot is **authenticated and running**! It's connected to:
- ✅ WhatsApp (scanned and linked)
- ✅ Flask API at `http://localhost:5000`
- ✅ Reminder scheduler active (daily at 9 AM)

## 📱 How to Use the Bot

### **Important: Register Customers First**

Before customers can use the bot, they must be registered in the database. Here's how:

### Step 1: Register a Customer

**Option A: Using API (Recommended)**

```powershell
# Register a customer via API
$body = @{
    name = "John Doe"
    phone = "+919876543210"  # Use your actual WhatsApp number
    address = "Test Address"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/customer" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Option B: Using Python Script**

Run the helper script:
```powershell
cd backend
python -c "from services.customer import create_customer; c = create_customer({'name': 'John Doe', 'phone': '+919876543210', 'address': 'Test'}); print(f'Customer created: {c.id}')"
```

### Step 2: Use WhatsApp Bot

Once registered, send messages to the WhatsApp number that's connected to the bot:

#### **Check Debt Balance**
```
"How much do I owe?"
"balance"
"debt"
```

#### **Record a New Debt**
```
"Bought milk for ₹120"
"Credit ₹500"
"Purchase ₹250"
```

#### **Record a Payment**
```
"Paid ₹500"
"Payment ₹1000"
"Repaid ₹200"
```

#### **Get Help**
```
"hi"
"hello"
"help"
```

## 🧪 Quick Test

1. **Register yourself as a customer:**
   ```powershell
   # Replace with your actual WhatsApp number
   $phone = "+919876543210"  # Your WhatsApp number
   $body = @{
       name = "Your Name"
       phone = $phone
       address = "Your Address"
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "http://localhost:5000/api/customer" `
       -Method POST `
       -ContentType "application/json" `
       -Body $body
   ```

2. **Send a test message on WhatsApp:**
   - Open WhatsApp on your phone
   - Find the chat with the bot (the number you scanned)
   - Send: `"hi"` or `"How much do I owe?"`

3. **Record a test debt:**
   - Send: `"Bought milk for ₹120"`
   - Bot should confirm the debt was recorded

4. **Check balance:**
   - Send: `"How much do I owe?"`
   - Bot should show your balance

## 📋 Complete Workflow Example

```
1. Register Customer (via API):
   POST /api/customer
   {
     "name": "John Doe",
     "phone": "+919876543210",
     "address": "123 Main St"
   }

2. Customer sends WhatsApp: "Bought rice for ₹300"
   → Bot records debt: ₹300
   → Bot responds: "✅ Debt recorded: ₹300. New balance: ₹300"

3. Customer sends WhatsApp: "How much do I owe?"
   → Bot responds: "💰 Your outstanding balance: ₹300"

4. Customer sends WhatsApp: "Paid ₹100"
   → Bot records payment: ₹100
   → Bot responds: "✅ Payment recorded: ₹100. New balance: ₹200"
```

## 🔍 Troubleshooting

### Bot doesn't respond
- ✅ Check Flask is running: `Invoke-WebRequest http://localhost:5000/health`
- ✅ Check bot is running (Node.js process active)
- ✅ Verify customer is registered in database

### "Customer not found" error
- Customer must be registered first via `/api/customer` endpoint
- Phone number must match exactly (with country code, e.g., +919876543210)

### Bot responds but can't record debt
- Check if a shopkeeper exists in database
- Bot uses the first shopkeeper if none specified
- Register a shopkeeper if needed: `POST /api/shopkeeper/register`

## 📊 Monitoring

Watch the bot logs in the terminal where `npm start` is running. You'll see:
- `📨 Message from +91...` - Incoming messages
- `🎯 Detected intent: ...` - Intent detection
- `✅ Debt recorded` - Successful operations
- `❌ Error: ...` - Any errors

## 🎯 Next Steps

1. Register test customers
2. Test the bot with WhatsApp messages
3. Check the Flask API logs for backend activity
4. Monitor MongoDB for stored transactions

---

**Remember:** The bot works entirely through WhatsApp messages - there's no web interface. All interaction happens via WhatsApp chat!

