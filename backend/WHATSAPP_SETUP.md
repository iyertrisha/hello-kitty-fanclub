# WhatsApp/Twilio Integration Setup Guide

⚠️ **DEPRECATED**: This guide is for the old Twilio-based WhatsApp integration, which required paid API access.

**For the new FREE WhatsApp bot implementation, see:**
- `backend/whatsapp-bot/README.md` - Setup and usage guide
- Uses `whatsapp-web.js` (free, no API fees)

---

# WhatsApp/Twilio Integration Setup Guide (DEPRECATED)

## Step 1: Create .env File

Copy the template to create your `.env` file:

**PowerShell:**
```powershell
cd backend
Copy-Item env.template -Destination .env
```

**Linux/Mac:**
```bash
cd backend
cp env.template .env
```

## Step 2: Fill in Required Environment Variables

Edit `backend/.env` and replace the placeholder values:

### Twilio Configuration

1. **TWILIO_ACCOUNT_SID**
   - Get from: https://console.twilio.com/
   - Go to: Account → Account Info
   - Copy the "Account SID" (starts with `AC`)
   - Example: `TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **TWILIO_AUTH_TOKEN**
   - Get from: https://console.twilio.com/
   - Go to: Account → Account Info
   - Click "View" next to Auth Token
   - Copy the token
   - Example: `TWILIO_AUTH_TOKEN=your_32_character_auth_token_here`

3. **TWILIO_WHATSAPP_NUMBER**
   - For sandbox testing: `whatsapp:+14155238886` (already set)
   - For production: Your approved WhatsApp Business number

### Dialogflow Configuration

4. **DIALOGFLOW_PROJECT_ID**
   - Get from: https://console.cloud.google.com/
   - Go to: Dialogflow → Settings → General
   - Copy the "Project ID"
   - Example: `DIALOGFLOW_PROJECT_ID=my-kirana-project`

5. **DIALOGFLOW_CREDENTIALS_PATH**
   - Download service account JSON key:
     1. Go to: https://console.cloud.google.com/apis/credentials
     2. Click "Create Credentials" → "Service Account"
     3. Create service account with "Dialogflow API User" role
     4. Download JSON key file
   - Place the file in your project (e.g., `backend/credentials/dialogflow-key.json`)
   - Set path: `DIALOGFLOW_CREDENTIALS_PATH=credentials/dialogflow-key.json`
   - **Important:** Add `credentials/` to `.gitignore`!

### Vineet API Configuration

6. **VINEET_API_BASE_URL**
   - Local development: `http://localhost:5000/api`
   - Production: Your actual API URL
   - Example: `VINEET_API_BASE_URL=http://localhost:5000/api`

### WhatsApp Internal API Key

7. **WHATSAPP_INTERNAL_API_KEY**
   - Generate a secure random string:
   
   **PowerShell:**
   ```powershell
   -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
   ```
   
   **Linux/Mac:**
   ```bash
   openssl rand -hex 32
   ```
   
   **Python:**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```
   
   - Example: `WHATSAPP_INTERNAL_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

## Step 3: Verify Your .env File

Your complete `.env` file should look like this (with your actual values):

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SECRET_KEY=dev-secret-key-change-in-production

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/kirana_db
MONGODB_DB_NAME=kirana_db

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8081,http://127.0.0.1:3000

# Blockchain Configuration
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=
PRIVATE_KEY=
ADMIN_ADDRESS=
CHAIN_ID=80002
GAS_LIMIT=3000000

# ML Service Configuration
ML_SERVICE_URL=http://localhost:5000/api/ml

# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Dialogflow Configuration
DIALOGFLOW_PROJECT_ID=your-dialogflow-project-id
DIALOGFLOW_CREDENTIALS_PATH=credentials/dialogflow-key.json

# Vineet API Configuration
VINEET_API_BASE_URL=http://localhost:5000/api

# WhatsApp Internal API Key
WHATSAPP_INTERNAL_API_KEY=your_generated_api_key_here
```

## Step 4: Install Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

This will install:
- `twilio>=8.0.0`
- `google-cloud-dialogflow>=2.0.0`
- All other required packages

## Step 5: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. In "Sandbox Configuration", set:
   - **When a message comes in:** `https://your-ngrok-url.ngrok-free.dev/api/whatsapp/webhook`
   - Or use your production URL if deployed
3. Save the configuration

## Step 6: Configure Dialogflow Intents

Ensure these intents are configured in Dialogflow:

1. **credit.confirm** - For credit confirmation responses (YES/NO)
2. **monthly.response** - For monthly summary responses (OK/DISPUTE)
3. **order.*** - For order-related intents (order.place, order.confirm, etc.)

## Step 7: Test the Setup

1. Start your Flask server:
   ```powershell
   cd backend
   python run.py
   ```

2. Test the webhook endpoint (if using ngrok):
   ```powershell
   # In another terminal
   ngrok http 5000
   # Update Twilio webhook URL with the ngrok URL
   ```

3. Send a test WhatsApp message to your Twilio sandbox number

## Troubleshooting

### Twilio Errors
- Verify Account SID and Auth Token are correct
- Check that WhatsApp sandbox is joined (send "join [code]" to +1 415 523 8886)
- Verify webhook URL is accessible (use ngrok for local testing)

### Dialogflow Errors
- Verify Project ID is correct
- Check service account JSON key path is correct
- Ensure service account has "Dialogflow API User" role
- Verify credentials file is not corrupted

### API Key Errors
- Ensure `WHATSAPP_INTERNAL_API_KEY` is set
- Use the same key in Authorization header: `Bearer YOUR_API_KEY`

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to git (already in `.gitignore`)
- Never commit service account JSON keys
- Use strong, random API keys
- Rotate keys regularly in production
- Use environment-specific values (dev/staging/prod)

