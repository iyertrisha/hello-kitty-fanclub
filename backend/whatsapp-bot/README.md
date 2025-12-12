# WhatsApp Debt Tracking Bot - Setup Guide

Free WhatsApp bot for debt tracking and reminders using `whatsapp-web.js` (no API fees required).

## Features

- ✅ **100% Free** - No WhatsApp Business API fees
- ✅ **Debt Queries** - Customers can ask "How much do I owe?"
- ✅ **Debt Recording** - Record new debts via WhatsApp messages
- ✅ **Payment Tracking** - Record payments and update balances
- ✅ **Automated Reminders** - Scheduled daily reminders for outstanding debts
- ✅ **Blockchain Integration** - All debt entries recorded on blockchain for transparency

## Architecture

```
Customer WhatsApp Message
    ↓
Node.js WhatsApp Bot (whatsapp-web.js)
    ↓
HTTP POST to Flask Backend (/api/debt/*)
    ↓
Debt Service + MongoDB + Blockchain
    ↓
Response back to Bot
    ↓
WhatsApp Reply to Customer
```

## Prerequisites

1. **Node.js** (v14 or higher)
   - Check: `node --version`
   - Download: https://nodejs.org/

2. **Python Flask Backend** (already set up)
   - MongoDB running
   - Flask server running on port 5000

3. **WhatsApp Mobile App**
   - For scanning QR code to connect

## Installation

### Step 1: Install Node.js Dependencies

```bash
cd backend/whatsapp-bot
npm install
```

This installs:
- `whatsapp-web.js` - WhatsApp client library
- `axios` - HTTP client for Flask API
- `node-cron` - Scheduled tasks
- `qrcode-terminal` - QR code display

### Step 2: Configure Environment

Copy the environment template:

```bash
# Windows PowerShell
Copy-Item .env.template -Destination .env

# Linux/Mac
cp .env.template .env
```

Edit `.env` and set:

```env
# Flask backend API URL
FLASK_API_URL=http://localhost:5000

# Reminder schedule (cron expression)
# Daily at 9 AM
REMINDER_SCHEDULE=0 9 * * *

# Session storage path
WHATSAPP_SESSION_PATH=./.wwebjs_auth
```

### Step 3: Ensure Flask Backend is Running

Make sure your Flask backend is running:

```bash
cd backend
python run.py
```

The Flask server should be accessible at `http://localhost:5000`.

### Step 4: Start the WhatsApp Bot

```bash
cd backend/whatsapp-bot
npm start
```

Or for development with auto-reload:

```bash
npm run dev
```

### Step 5: Connect WhatsApp

1. The bot will display a QR code in the terminal
2. Open WhatsApp on your phone
3. Go to **Settings → Linked Devices**
4. Tap **Link a Device**
5. Scan the QR code displayed in the terminal
6. Wait for "✅ WhatsApp Bot is ready!" message

## Usage

### For Customers

Once connected, customers can send messages to the bot's WhatsApp number:

#### Check Debt Balance
```
"How much do I owe?"
"balance"
"debt"
```

#### Record a Debt
```
"Bought milk for ₹120"
"Credit ₹500"
"Purchase ₹250"
```

#### Record a Payment
```
"Paid ₹500"
"Payment ₹1000"
"Repaid ₹200"
```

### For Developers

#### Manual Reminder Trigger

You can manually trigger reminders by calling the Flask API:

```bash
curl http://localhost:5000/api/debt/reminders
```

#### Check Bot Status

The bot logs all activities to the console. Watch for:
- `📨 Message from +91...` - Incoming messages
- `🎯 Detected intent: ...` - Intent detection
- `✅ Reminder sent to ...` - Reminder notifications

## API Endpoints

The bot communicates with these Flask endpoints:

- `POST /api/debt/query` - Query customer debt
- `POST /api/debt/record` - Record new debt entry
- `POST /api/debt/payment` - Record payment
- `GET /api/debt/reminders` - Get customers needing reminders

See `backend/api/routes/debt.py` for details.

## Configuration

### Reminder Schedule

Edit the cron expression in `.env`:

```env
# Daily at 9 AM
REMINDER_SCHEDULE=0 9 * * *

# Twice daily (9 AM and 6 PM)
REMINDER_SCHEDULE=0 9,18 * * *

# Every Monday at 9 AM
REMINDER_SCHEDULE=0 9 * * 1
```

Cron format: `minute hour day month day-of-week`

### Session Storage

WhatsApp authentication is stored in `.wwebjs_auth/` directory. This allows the bot to stay connected without re-scanning QR code every time.

**Important:** Keep this directory secure and don't share it. It contains your WhatsApp session.

## Troubleshooting

### Bot Won't Connect

1. **Check Flask Backend**
   ```bash
   curl http://localhost:5000/health
   ```
   Should return `{"status": "healthy"}`

2. **Check MongoDB**
   - Ensure MongoDB is running
   - Check connection in Flask logs

3. **QR Code Issues**
   - Make sure terminal supports QR code display
   - Try resizing terminal window
   - QR code expires after ~20 seconds, restart bot if needed

### Messages Not Being Received

1. **Check Bot Status**
   - Look for "✅ WhatsApp Bot is ready!" in logs
   - If not ready, check for connection errors

2. **Check Phone Number Format**
   - Bot expects phone numbers with country code (e.g., +919876543210)
   - Customer must be registered in database first

3. **Check Flask API**
   - Test endpoints manually:
   ```bash
   curl -X POST http://localhost:5000/api/debt/query \
     -H "Content-Type: application/json" \
     -d '{"phone": "+919876543210"}'
   ```

### Reminders Not Sending

1. **Check Cron Schedule**
   - Verify `REMINDER_SCHEDULE` in `.env`
   - Check timezone (default: Asia/Kolkata)

2. **Check Customer Data**
   - Ensure customers have `credit_balance > 0`
   - Verify phone numbers are correct

3. **Manual Test**
   - Call `/api/debt/reminders` endpoint
   - Check if customers are returned

### Blockchain Recording Fails

Blockchain recording is optional. If it fails:
- Check blockchain configuration in `backend/blockchain/config.py`
- Verify `CONTRACT_ADDRESS` and `PRIVATE_KEY` are set
- Transactions will still be saved to MongoDB even if blockchain fails

## Security Notes

⚠️ **Important:**

1. **Session Security**
   - Don't commit `.wwebjs_auth/` to git (already in `.gitignore`)
   - Keep session files secure

2. **Phone Number Privacy**
   - Phone numbers are stored in MongoDB
   - Ensure database access is restricted

3. **API Security**
   - Flask API endpoints don't require authentication by default
   - Add authentication for production use

## Development

### Project Structure

```
whatsapp-bot/
├── index.js              # Main entry point
├── config.js             # Configuration
├── messageHandler.js      # Message routing
├── reminderScheduler.js   # Scheduled reminders
├── handlers/
│   ├── debtQuery.js      # Debt query handler
│   ├── debtRecord.js     # Debt recording handler
│   └── payment.js        # Payment handler
├── package.json          # Dependencies
└── .env                  # Environment variables
```

### Adding New Handlers

1. Create handler in `handlers/` directory
2. Export `handle` function
3. Add intent detection in `messageHandler.js`
4. Route to handler in `messageHandler.js`

### Testing

Test individual components:

```bash
# Test message handler
node -e "const mh = require('./messageHandler'); console.log(mh.detectIntent('How much do I owe?'));"

# Test Flask API
curl http://localhost:5000/api/debt/reminders
```

## Production Deployment

### Running as a Service

**Linux (systemd):**

Create `/etc/systemd/system/whatsapp-bot.service`:

```ini
[Unit]
Description=WhatsApp Debt Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend/whatsapp-bot
ExecStart=/usr/bin/node index.js
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot
```

**Windows (Task Scheduler):**

Create a scheduled task to run `npm start` on system boot.

### Monitoring

- Monitor bot logs for errors
- Set up alerts for connection failures
- Monitor Flask API health
- Track reminder delivery rates

## Support

For issues or questions:
1. Check logs in terminal
2. Review Flask API logs
3. Check MongoDB connection
4. Verify customer data in database

## License

MIT

