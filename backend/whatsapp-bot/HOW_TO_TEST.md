# How to Test the WhatsApp Bot

## The Problem

When you scan the QR code, you're linking **YOUR WhatsApp account** to the bot. The bot receives messages sent **TO your phone number**, but you can't easily message yourself on WhatsApp.

## Solution 1: Enable Test Mode (Easiest)

I've added a **TEST_MODE** feature that allows you to test the bot by messaging yourself.

### Step 1: Enable Test Mode

The `.env` file has been updated with `TEST_MODE=true`. If you need to add it manually:

```powershell
# Add this line to backend/whatsapp-bot/.env
TEST_MODE=true
```

### Step 2: Restart the Bot

```powershell
# Stop the bot (Ctrl+C in the terminal running it)
# Then restart:
cd backend\whatsapp-bot
npm start
```

### Step 3: Test Using WhatsApp's "Message Yourself" Feature

1. **Open WhatsApp on your phone**
2. **Go to your own chat** (search for your own name/number in WhatsApp)
3. **Send a message to yourself**, for example:
   - `"hi"`
   - `"How much do I owe?"`
   - `"Bought milk for ₹120"`

The bot should now respond to your messages!

## Solution 2: Use Another WhatsApp Number

If test mode doesn't work, use a different WhatsApp number:

1. **Get another phone with WhatsApp** (friend, family, or second phone)
2. **Have them message your number** (+918690576334)
3. The bot will respond to their messages

## Solution 3: Use WhatsApp Web/Desktop

1. **Open WhatsApp Web** in your browser (web.whatsapp.com)
2. **Scan the QR code** with your phone
3. **Open a chat with yourself** (if available)
4. **Send messages** from WhatsApp Web

## How to Verify It's Working

1. **Check the bot terminal logs** - you should see:
   ```
   📨 Message from +918690576334: hi...
   🎯 Detected intent: greeting
   ```

2. **Check your WhatsApp** - you should receive a response from the bot

3. **Test commands:**
   - `"hi"` → Should get greeting message
   - `"How much do I owe?"` → Should show balance
   - `"Bought milk for ₹120"` → Should record debt
   - `"Paid ₹50"` → Should record payment

## Troubleshooting

### Bot doesn't respond
- ✅ Check if TEST_MODE=true is in `.env`
- ✅ Restart the bot after enabling test mode
- ✅ Check bot terminal for error messages
- ✅ Verify Flask API is running: `Invoke-WebRequest http://localhost:5000/health`

### "Customer not found" error
- Make sure you registered the customer first:
  ```powershell
  .\register_test_customer.ps1 -Name "Hello Kitty" -Phone "+918690576334"
  ```

### Still can't message yourself
- Use Solution 2 (another WhatsApp number)
- Or use WhatsApp Business API (requires setup)

## Current Status

✅ Test mode enabled in `.env`
✅ Bot code updated to support self-messaging
✅ Customer "Hello Kitty" registered with phone +918690576334

**Next step:** Restart the bot and try messaging yourself!

