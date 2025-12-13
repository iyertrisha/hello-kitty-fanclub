"""
Email service - Send emails via SendGrid
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config
import logging

logger = logging.getLogger(__name__)


def _fallback_to_dev_mode(email, otp_code, error_reason, fix_instruction=None):
    """
    Fallback to development mode when SendGrid fails
    Logs OTP to console instead of sending email
    """
    logger.warning("=" * 80)
    logger.warning("⚠️  SendGrid Error - Using DEVELOPMENT MODE")
    logger.warning("=" * 80)
    logger.warning(f"Error: {error_reason}")
    if fix_instruction:
        logger.warning(f"Fix: {fix_instruction}")
    logger.warning(f"📧 OTP for {email}: {otp_code}")
    logger.warning(f"⏰ This OTP will expire in 10 minutes")
    logger.warning("=" * 80)
    logger.warning("To enable email sending, configure SendGrid in .env:")
    logger.warning("  SENDGRID_API_KEY=SG.your_actual_api_key_here")
    logger.warning("  SENDGRID_FROM_EMAIL=your-verified-email@domain.com")
    logger.warning("=" * 80)
    
    # Print to console for easy visibility
    print("\n" + "=" * 80)
    print(f"⚠️  DEVELOPMENT MODE: OTP Email (SendGrid Error)")
    print(f"Error: {error_reason}")
    print(f"📧 Email: {email}")
    print(f"🔑 OTP Code: {otp_code}")
    print(f"⏰ Expires in: 10 minutes")
    if fix_instruction:
        print(f"💡 {fix_instruction}")
    print("=" * 80 + "\n")
    return True  # Return success so OTP flow continues


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
        
        # Check if API key is placeholder or missing
        if not api_key or not api_key.strip() or api_key == 'your_sendgrid_api_key_here':
            # Development mode: Log OTP to console instead of sending email
            logger.warning("=" * 80)
            logger.warning("⚠️  SendGrid API key not configured - Using DEVELOPMENT MODE")
            logger.warning("=" * 80)
            logger.warning(f"📧 OTP for {email}: {otp_code}")
            logger.warning(f"⏰ This OTP will expire in 10 minutes")
            logger.warning("=" * 80)
            logger.warning("To enable email sending, add your SendGrid API key to .env:")
            logger.warning("  SENDGRID_API_KEY=SG.your_actual_api_key_here")
            logger.warning("  SENDGRID_FROM_EMAIL=your-verified-email@domain.com")
            logger.warning("=" * 80)
            # Print to console for easy visibility
            print("\n" + "=" * 80)
            print(f"⚠️  DEVELOPMENT MODE: OTP Email (SendGrid not configured)")
            print(f"📧 Email: {email}")
            print(f"🔑 OTP Code: {otp_code}")
            print(f"⏰ Expires in: 10 minutes")
            print("=" * 80 + "\n")
            return True  # Return success so OTP flow continues
        
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
        
        # Validate API key format before attempting to send
        if not api_key.startswith('SG.') or len(api_key) < 20:
            # Invalid API key format - use development mode
            logger.warning("=" * 80)
            logger.warning("⚠️  Invalid SendGrid API key format - Using DEVELOPMENT MODE")
            logger.warning("=" * 80)
            logger.warning(f"📧 OTP for {email}: {otp_code}")
            logger.warning(f"⏰ This OTP will expire in 10 minutes")
            logger.warning("=" * 80)
            print("\n" + "=" * 80)
            print(f"⚠️  DEVELOPMENT MODE: OTP Email (Invalid SendGrid API key)")
            print(f"📧 Email: {email}")
            print(f"🔑 OTP Code: {otp_code}")
            print(f"⏰ Expires in: 10 minutes")
            print("=" * 80 + "\n")
            return True
        
        # Send email via SendGrid
        sg = SendGridAPIClient(api_key)
        try:
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"OTP email sent successfully to {email}")
                return True
            else:
                # Non-success status code - fallback to development mode
                logger.error(f"Failed to send OTP email. Status: {response.status_code}, Body: {response.body}")
                error_reason = f"SendGrid returned status {response.status_code}"
                if response.status_code == 401:
                    error_reason = "SendGrid 401 Unauthorized - Invalid API key"
                    return _fallback_to_dev_mode(email, otp_code, error_reason, 
                                               "Get API key from https://app.sendgrid.com/ and add to .env")
                elif response.status_code == 403:
                    error_reason = "SendGrid 403 Forbidden - Email not verified or insufficient permissions"
                    return _fallback_to_dev_mode(email, otp_code, error_reason,
                                               f"Verify '{from_email}' in SendGrid Dashboard > Settings > Sender Authentication")
                else:
                    return _fallback_to_dev_mode(email, otp_code, error_reason)
        except Exception as send_error:
            # Catch all SendGrid errors (HTTP errors, connection errors, etc.)
            error_msg = str(send_error)
            error_type = type(send_error).__name__
            
            # Check for 401 Unauthorized in error message
            if "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
                return _fallback_to_dev_mode(email, otp_code, "SendGrid 401 Unauthorized", 
                                           "Get API key from https://app.sendgrid.com/ and add to .env")
            elif "403" in error_msg or "Forbidden" in error_msg:
                return _fallback_to_dev_mode(email, otp_code, "SendGrid 403 Forbidden",
                                           f"Verify '{from_email}' in SendGrid Dashboard > Settings > Sender Authentication")
            else:
                # Other errors - still fallback to development mode
                return _fallback_to_dev_mode(email, otp_code, f"SendGrid error ({error_type}): {error_msg[:100]}")
            
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {e}", exc_info=True)
        raise
