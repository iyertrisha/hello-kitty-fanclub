"""
Diagnostic script to check OTP setup issues
Run this to see what's wrong with your OTP configuration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# #region agent log
LOG_PATH = r'c:\hello-kitty-fanclub\.cursor\debug.log'
def debug_log(hypothesis_id, location, message, data):
    import time
    with open(LOG_PATH, 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"env-check","hypothesisId":hypothesis_id,"location":location,"message":message,"data":data,"timestamp":int(time.time()*1000)}) + '\n')
# #endregion

# Load .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .env file found at: {env_path}\n")
    
    # #region agent log
    # Read raw .env content to check for issues
    with open(env_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()
    lines = raw_content.split('\n')
    sendgrid_lines = [l for l in lines if 'SENDGRID' in l.upper()]
    mongodb_lines = [l for l in lines if 'MONGO' in l.upper()]
    debug_log("A", "check_otp_setup.py:env_read", "Raw .env content analysis", {
        "total_lines": len(lines),
        "sendgrid_lines": sendgrid_lines,
        "mongodb_lines": mongodb_lines,
        "has_sendgrid_api_key": any('SENDGRID_API_KEY' in l for l in lines),
        "env_path": str(env_path)
    })
    # #endregion
else:
    print(f"❌ .env file NOT found at: {env_path}")
    print("   Please create a .env file in whackiest/backend/\n")
    sys.exit(1)

# Check MongoDB
print("=" * 60)
print("1. MONGODB CONFIGURATION")
print("=" * 60)
mongodb_uri = os.getenv('MONGODB_URI', '')
if mongodb_uri:
    print(f"✅ MONGODB_URI found")
    if 'mongodb+srv://' in mongodb_uri:
        print("   Type: MongoDB Atlas (Cloud)")
        # Mask password in URI
        if '@' in mongodb_uri:
            parts = mongodb_uri.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split('://')[1]
                if ':' in user_pass:
                    user = user_pass.split(':')[0]
                    print(f"   Username: {user}")
                    print(f"   Password: {'*' * 10} (hidden)")
    elif 'mongodb://localhost' in mongodb_uri:
        print("   Type: Local MongoDB")
    else:
        print(f"   URI: {mongodb_uri[:50]}...")
    
    # Try to connect
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        print("   ✅ MongoDB connection successful!")
    except ServerSelectionTimeoutError as e:
        print(f"   ❌ MongoDB connection FAILED: {str(e)[:100]}")
        print("   → Check if MongoDB is running or if your IP is whitelisted")
    except ConfigurationError as e:
        print(f"   ❌ MongoDB configuration error: {str(e)[:100]}")
        print("   → Check your connection string format")
    except Exception as e:
        print(f"   ❌ MongoDB error: {str(e)[:100]}")
else:
    print("❌ MONGODB_URI not found in .env")
    print("   Add: MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/kirana_db")

print()

# Check SendGrid
print("=" * 60)
print("2. SENDGRID CONFIGURATION")
print("=" * 60)
sendgrid_key = os.getenv('SENDGRID_API_KEY', '')
sendgrid_email = os.getenv('SENDGRID_FROM_EMAIL', '')

# #region agent log
debug_log("A", "check_otp_setup.py:sendgrid_check", "SendGrid env vars after load", {
    "sendgrid_key_exists": bool(sendgrid_key),
    "sendgrid_key_length": len(sendgrid_key) if sendgrid_key else 0,
    "sendgrid_key_prefix": sendgrid_key[:15] if sendgrid_key and len(sendgrid_key) > 15 else sendgrid_key,
    "sendgrid_email": sendgrid_email,
    "all_env_keys_with_send": [k for k in os.environ.keys() if 'SEND' in k.upper()]
})
# #endregion

if sendgrid_key:
    if sendgrid_key.startswith('SG.'):
        print(f"✅ SENDGRID_API_KEY found: {sendgrid_key[:10]}...{sendgrid_key[-10:]}")
        print(f"   Length: {len(sendgrid_key)} characters (should be ~70)")
    else:
        print(f"⚠️  SENDGRID_API_KEY doesn't start with 'SG.' - might be invalid")
        print(f"   Value: {sendgrid_key[:20]}...")
else:
    print("❌ SENDGRID_API_KEY not found in .env")
    print("   Add: SENDGRID_API_KEY=SG.your_api_key_here")

if sendgrid_email:
    print(f"✅ SENDGRID_FROM_EMAIL: {sendgrid_email}")
else:
    print("⚠️  SENDGRID_FROM_EMAIL not set (will use default: noreply@kirana.com)")

# Test SendGrid connection
if sendgrid_key:
    try:
        from sendgrid import SendGridAPIClient
        sg = SendGridAPIClient(sendgrid_key)
        # Try to get API key info (this will fail if key is invalid)
        print("   → Testing API key...")
        # Note: We can't easily test without making an API call, so we'll just check format
        if len(sendgrid_key) > 50:
            print("   ✅ API key format looks valid")
        else:
            print("   ⚠️  API key seems too short - might be invalid")
    except Exception as e:
        print(f"   ❌ SendGrid error: {str(e)[:100]}")

print()

# Check other required config
print("=" * 60)
print("3. OTHER CONFIGURATION")
print("=" * 60)
flask_port = os.getenv('FLASK_PORT', '5000')
print(f"✅ FLASK_PORT: {flask_port}")

cors_origins = os.getenv('CORS_ORIGINS', '')
if cors_origins:
    print(f"✅ CORS_ORIGINS: {cors_origins}")
else:
    print("⚠️  CORS_ORIGINS not set (might cause CORS errors)")

print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
issues = []

if not mongodb_uri:
    issues.append("❌ MongoDB URI not configured")
elif 'mongodb://localhost' in mongodb_uri:
    issues.append("⚠️  Using local MongoDB - make sure it's running")

if not sendgrid_key:
    issues.append("❌ SendGrid API key not configured")
elif not sendgrid_key.startswith('SG.'):
    issues.append("⚠️  SendGrid API key format might be invalid")

if not sendgrid_email:
    issues.append("⚠️  SendGrid FROM_EMAIL not set (might cause issues)")

if issues:
    print("\nIssues found:")
    for issue in issues:
        print(f"  {issue}")
    print("\nFix these issues and restart your Flask server.")
else:
    print("\n✅ All configurations look good!")
    print("If OTP still fails, check:")
    print("  1. Flask server is running")
    print("  2. Flask server was restarted after .env changes")
    print("  3. SendGrid sender email is verified in SendGrid dashboard")
    print("  4. Check Flask server console for error messages")

print()

