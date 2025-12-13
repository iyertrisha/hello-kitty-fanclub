# Quick Fix: OTP Email Not Working

## The Problem

You're not receiving OTP emails because **SendGrid is not configured**. The system is currently running in **development mode**, which means OTP codes are only printed to the Flask server console, not sent via email.

## Quick Solution (3 Steps)

### 1. Create .env file (if missing)

```powershell
cd helloKittyFanclub/backend
Copy-Item env.template -Destination .env
```

### 2. Get SendGrid API Key

- Go to: https://app.sendgrid.com/settings/api_keys
- Click "Create API Key"
- Copy the key (starts with `SG.`)

### 3. Update .env file

Open `helloKittyFanclub/backend/.env` and set:

```env
SENDGRID_API_KEY=SG.your_actual_key_here
SENDGRID_FROM_EMAIL=your-email@domain.com
```

**Important:** 
- Replace with your actual SendGrid API key
- Verify the FROM_EMAIL in SendGrid dashboard
- Restart Flask server after changes

## Verify Setup

Run the diagnostic:
```powershell
python diagnose_otp_email.py
```

## Check Console for OTP

If SendGrid isn't configured yet, check your **Flask server console** - the OTP code will be printed there with a message like:

```
⚠️  DEVELOPMENT MODE: OTP Email (SendGrid not configured)
📧 Email: your-email@example.com
🔑 OTP Code: 123456
```

## Full Instructions

See `SENDGRID_SETUP.md` for detailed step-by-step instructions.

