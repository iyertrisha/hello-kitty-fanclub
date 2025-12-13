# SendGrid Setup Instructions

## Why am I not receiving OTP emails?

If you're not receiving OTP emails, the most common reasons are:

1. **`.env` file doesn't exist** - The email service falls back to development mode (logs OTP to console)
2. **SendGrid API key not configured** - Missing or placeholder value in `.env`
3. **SendGrid FROM_EMAIL not verified** - The sender email must be verified in SendGrid
4. **Flask server not restarted** - Changes to `.env` require a server restart

## Quick Diagnostic

Run this to check your setup:
```bash
cd helloKittyFanclub/backend
python diagnose_otp_email.py
```

## Configuration Steps

### Step 1: Create .env file (if it doesn't exist)

**PowerShell:**
```powershell
cd helloKittyFanclub/backend
Copy-Item env.template -Destination .env
```

**Or manually:**
- Copy `env.template` to `.env` in the `backend` directory

### Step 2: Get SendGrid API Key

1. Go to [SendGrid API Keys](https://app.sendgrid.com/settings/api_keys)
2. Click **"Create API Key"**
3. Give it a name (e.g., "Kirana OTP Service")
4. Select **"Full Access"** or **"Mail Send"** permissions
5. Click **"Create & View"**
6. **Copy the API key immediately** (starts with `SG.` and is ~70 characters long)
   - ⚠️ You won't be able to see it again!

### Step 3: Verify Sender Email

1. Go to [SendGrid Sender Authentication](https://app.sendgrid.com/settings/sender_auth/senders/new)
2. Click **"Create New Sender"**
3. Fill in your email details:
   - **From Email**: The email you want to send from (e.g., `noreply@yourdomain.com`)
   - **From Name**: Your name or company name
   - **Reply To**: Same as From Email (or your support email)
4. Verify the email by clicking the link in the verification email SendGrid sends

### Step 4: Update .env file

Open `helloKittyFanclub/backend/.env` and update these lines:

```env
SENDGRID_API_KEY=SG.your_actual_api_key_here
SENDGRID_FROM_EMAIL=your-verified-email@domain.com
```

**Important:**
- Replace `SG.your_actual_api_key_here` with your actual API key from Step 2
- Replace `your-verified-email@domain.com` with the email you verified in Step 3
- Make sure there are **no spaces** around the `=` sign
- Don't use quotes around the values

### Step 5: Restart Flask Server

**Stop your Flask server** (Ctrl+C) and **restart it** for the changes to take effect.

## Testing

After setup, test the OTP flow:
1. Navigate to the supplier portal login page
2. Enter an email address
3. Check your email for the OTP code
4. Check spam/junk folder if not in inbox
5. Enter the OTP to complete login

## Troubleshooting

### Still not receiving emails?

1. **Check Flask server console** - Look for error messages or "DEVELOPMENT MODE" warnings
2. **Check SendGrid Activity Feed** - Go to [SendGrid Activity](https://app.sendgrid.com/activity) to see if emails are being sent
3. **Verify API key is correct** - Run `python diagnose_otp_email.py` to check configuration
4. **Check email address** - Make sure you're using the correct recipient email
5. **Check spam folder** - Emails might be going to spam
6. **Verify sender email** - The FROM_EMAIL must be verified in SendGrid

### Development Mode

If SendGrid is not configured, the system will automatically fall back to **development mode**:
- OTP codes are **printed to the Flask server console**
- Look for messages like: `⚠️  DEVELOPMENT MODE: OTP Email`
- The OTP code will be displayed in the console output

## Notes

- OTP codes expire after 10 minutes
- Rate limiting: Maximum 3 OTP requests per email per 15 minutes
- OTPs are one-time use only
- SendGrid free tier allows 100 emails per day

