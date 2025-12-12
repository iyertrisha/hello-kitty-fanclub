"""
Email service - Send emails via SendGrid
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config
import logging

logger = logging.getLogger(__name__)


def send_otp_email(email, otp_code):
    """
    Send OTP email via SendGrid
    
    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        # Always try loading .env explicitly first
        from dotenv import load_dotenv
        from pathlib import Path
        
        # Try multiple possible paths
        # From services/email/email_service.py, we need to go up 3 levels to reach backend/
        possible_paths = [
            Path(__file__).parent.parent.parent / '.env',  # backend/.env (from services/email/email_service.py)
            Path(__file__).parent.parent.parent.parent / 'backend' / '.env',  # project/backend/.env
            Path(__file__).parent.parent / '.env',  # services/.env (fallback)
            Path('.env'),  # Current directory
        ]
        
        api_key = None
        from_email = None
        
        # Try to load from .env file
        for env_path in possible_paths:
            abs_path = env_path.resolve()
            if abs_path.exists():
                logger.info(f"Trying to load .env from: {abs_path}")
                load_dotenv(dotenv_path=abs_path, override=True)
                api_key = os.getenv('SENDGRID_API_KEY')
                from_email = os.getenv('SENDGRID_FROM_EMAIL')
                logger.info(f"After loading from {abs_path}, api_key found: {bool(api_key)}, length: {len(api_key) if api_key else 0}")
                if api_key and api_key.strip():
                    logger.info(f"Successfully loaded SENDGRID_API_KEY from {abs_path}")
                    break
            else:
                logger.debug(f".env file not found at: {abs_path}")
        
        # If still not found, try environment variables directly
        if not api_key or not api_key.strip():
            api_key = os.getenv('SENDGRID_API_KEY')
            from_email = os.getenv('SENDGRID_FROM_EMAIL')
            if api_key and api_key.strip():
                logger.info("Found SENDGRID_API_KEY in environment variables")
        
        # If still not found, try Config class
        if not api_key or not api_key.strip():
            if hasattr(Config, 'SENDGRID_API_KEY'):
                config_key = Config.SENDGRID_API_KEY
                if config_key and config_key.strip():
                    api_key = config_key
                    logger.info("Found SENDGRID_API_KEY in Config class")
        
        if not from_email:
            if hasattr(Config, 'SENDGRID_FROM_EMAIL') and Config.SENDGRID_FROM_EMAIL:
                from_email = Config.SENDGRID_FROM_EMAIL
            else:
                from_email = 'noreply@kirana.com'
        
        if not api_key or not api_key.strip():
            logger.error(f"SENDGRID_API_KEY not configured. Checked paths: {[str(p) for p in possible_paths]}")
            logger.error(f"Config.SENDGRID_API_KEY: {getattr(Config, 'SENDGRID_API_KEY', 'NOT_SET')}")
            raise ValueError("SendGrid API key not configured")
        
        # Create email message
        message = Mail(
            from_email=from_email,
            to_emails=email,
            subject='Your OTP Code for Supplier Portal',
            html_content=f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #667eea;">Supplier Portal - OTP Verification</h2>
                    <p>Your OTP code is:</p>
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #667eea; font-size: 32px; letter-spacing: 5px; margin: 0;">{otp_code}</h1>
                    </div>
                    <p>This code will expire in 10 minutes.</p>
                    <p style="color: #666; font-size: 12px;">If you didn't request this code, please ignore this email.</p>
                </body>
            </html>
            """
        )
        
        # Send email
        sg = SendGridAPIClient(api_key)
        try:
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"OTP email sent successfully to {email}")
                return True
            else:
                logger.error(f"Failed to send OTP email. Status: {response.status_code}, Body: {response.body}")
                return False
        except Exception as send_error:
            # Provide more helpful error messages
            error_msg = str(send_error)
            if "403" in error_msg or "Forbidden" in error_msg:
                logger.error(f"SendGrid 403 Forbidden - Common causes:")
                logger.error(f"  1. 'From' email ({from_email}) is not verified in SendGrid")
                logger.error(f"  2. API key doesn't have 'Mail Send' permissions")
                logger.error(f"  3. API key is invalid or expired")
                logger.error(f"  To fix: Go to SendGrid Dashboard > Settings > Sender Authentication")
                logger.error(f"  and verify the email address: {from_email}")
            raise
            
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {e}", exc_info=True)
        raise
