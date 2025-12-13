"""
Quick diagnostic script to check why OTP emails aren't being sent
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

print("=" * 80)
print("OTP EMAIL DIAGNOSTIC")
print("=" * 80)
print()

# Check if .env exists
backend_dir = Path(__file__).parent
env_path = backend_dir / '.env'

if not env_path.exists():
    print("❌ PROBLEM FOUND: .env file does not exist!")
    print(f"   Expected location: {env_path}")
    print()
    print("📝 SOLUTION:")
    print("   1. Copy env.template to .env:")
    print(f"      PowerShell: Copy-Item env.template -Destination .env")
    print(f"      Or manually: Copy {backend_dir / 'env.template'} to {env_path}")
    print()
    print("   2. Edit .env and add your SendGrid credentials:")
    print("      SENDGRID_API_KEY=SG.your_actual_api_key_here")
    print("      SENDGRID_FROM_EMAIL=your-verified-email@domain.com")
    print()
    print("   3. Get SendGrid API key from: https://app.sendgrid.com/settings/api_keys")
    print("   4. Verify your sender email in SendGrid Dashboard")
    print("   5. Restart your Flask server")
    sys.exit(1)

print(f"✅ .env file found at: {env_path}")
print()

# Load .env
load_dotenv(dotenv_path=env_path, override=True)

# Check SendGrid configuration
print("Checking SendGrid configuration...")
print()

sendgrid_key = os.getenv('SENDGRID_API_KEY', '').strip()
sendgrid_email = os.getenv('SENDGRID_FROM_EMAIL', '').strip()

issues = []

if not sendgrid_key:
    issues.append("❌ SENDGRID_API_KEY is missing or empty")
elif sendgrid_key == 'your_sendgrid_api_key_here':
    issues.append("❌ SENDGRID_API_KEY is still set to placeholder value")
elif not sendgrid_key.startswith('SG.'):
    issues.append(f"⚠️  SENDGRID_API_KEY doesn't start with 'SG.' (might be invalid)")
    print(f"   Current value: {sendgrid_key[:20]}...")
elif len(sendgrid_key) < 50:
    issues.append(f"⚠️  SENDGRID_API_KEY seems too short (should be ~70 characters)")
    print(f"   Current length: {len(sendgrid_key)} characters")
else:
    print(f"✅ SENDGRID_API_KEY found: {sendgrid_key[:10]}...{sendgrid_key[-10:]}")

if not sendgrid_email:
    issues.append("⚠️  SENDGRID_FROM_EMAIL is missing (will use default: noreply@kirana.com)")
elif sendgrid_email == 'noreply@yourdomain.com':
    issues.append("❌ SENDGRID_FROM_EMAIL is still set to placeholder value")
else:
    print(f"✅ SENDGRID_FROM_EMAIL: {sendgrid_email}")

print()

if issues:
    print("=" * 80)
    print("ISSUES FOUND:")
    print("=" * 80)
    for issue in issues:
        print(f"  {issue}")
    print()
    print("=" * 80)
    print("HOW TO FIX:")
    print("=" * 80)
    print()
    print("1. Get your SendGrid API Key:")
    print("   - Go to: https://app.sendgrid.com/settings/api_keys")
    print("   - Click 'Create API Key'")
    print("   - Give it a name (e.g., 'Kirana OTP Service')")
    print("   - Select 'Full Access' or 'Mail Send' permissions")
    print("   - Copy the API key (starts with 'SG.')")
    print()
    print("2. Verify your sender email in SendGrid:")
    print("   - Go to: https://app.sendgrid.com/settings/sender_auth/senders/new")
    print("   - Add and verify the email you want to use as FROM_EMAIL")
    print()
    print("3. Update your .env file:")
    print(f"   Open: {env_path}")
    print("   Set:")
    print("   SENDGRID_API_KEY=SG.your_actual_api_key_here")
    print("   SENDGRID_FROM_EMAIL=your-verified-email@domain.com")
    print()
    print("4. Restart your Flask server for changes to take effect")
    print()
    sys.exit(1)
else:
    print("=" * 80)
    print("✅ CONFIGURATION LOOKS GOOD!")
    print("=" * 80)
    print()
    print("If you're still not receiving emails, check:")
    print("  1. Flask server console for error messages")
    print("  2. SendGrid Activity Feed: https://app.sendgrid.com/activity")
    print("  3. Check spam/junk folder")
    print("  4. Verify the recipient email address is correct")
    print("  5. Make sure Flask server was restarted after .env changes")
    print()
    
    # Try to test SendGrid connection
    if sendgrid_key and sendgrid_key.startswith('SG.'):
        try:
            from sendgrid import SendGridAPIClient
            print("Testing SendGrid connection...")
            sg = SendGridAPIClient(sendgrid_key)
            # We can't easily test without making an API call, but we can check format
            print("✅ SendGrid client initialized successfully")
            print("   (Note: This doesn't verify the API key is valid, just that format is correct)")
        except Exception as e:
            print(f"⚠️  Error initializing SendGrid client: {e}")

print()

