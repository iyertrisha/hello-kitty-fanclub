"""
Quick script to check if .env file exists and has SendGrid API key
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'

if env_path.exists():
    print(f"✅ .env file found at: {env_path}")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv('SENDGRID_API_KEY', '')
    from_email = os.getenv('SENDGRID_FROM_EMAIL', '')
    
    if api_key:
        print(f"✅ SENDGRID_API_KEY found: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''}")
    else:
        print("❌ SENDGRID_API_KEY not found in .env")
    
    if from_email:
        print(f"✅ SENDGRID_FROM_EMAIL: {from_email}")
    else:
        print("⚠️  SENDGRID_FROM_EMAIL not set, will use default")
else:
    print(f"❌ .env file not found at: {env_path}")
    print("\nPlease create .env file with:")
    print("SENDGRID_API_KEY=SG.your_api_key_here")
    print("SENDGRID_FROM_EMAIL=noreply@kirana.com")

