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
    # #region agent log
    import json
    with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"email_service.py:13","message":"send_otp_email entry","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
    try:
        api_key = os.getenv('SENDGRID_API_KEY', Config.SENDGRID_API_KEY if hasattr(Config, 'SENDGRID_API_KEY') else None)
        from_email = os.getenv('SENDGRID_FROM_EMAIL', Config.SENDGRID_FROM_EMAIL if hasattr(Config, 'SENDGRID_FROM_EMAIL') else 'noreply@kirana.com')
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"email_service.py:26","message":"API key retrieved","data":{"api_key_exists":bool(api_key),"api_key_length":len(api_key) if api_key else 0,"api_key_prefix":api_key[:10] if api_key and len(api_key) > 10 else None,"from_email":from_email,"hasattr_config":hasattr(Config,'SENDGRID_API_KEY'),"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        
        if not api_key:
            # #region agent log
            with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"email_service.py:30","message":"API key check failed","data":{"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            logger.error("SENDGRID_API_KEY not configured")
            raise ValueError("SendGrid API key not configured")
        
        # Create email message
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"email_service.py:35","message":"before Mail creation","data":{"from_email":from_email,"to_email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
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
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"email_service.py:52","message":"Mail object created","data":{"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        
        # Send email
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"email_service.py:54","message":"before SendGrid API call","data":{"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"email_service.py:56","message":"SendGrid API response received","data":{"status_code":response.status_code,"headers":dict(response.headers) if hasattr(response,'headers') else None,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        
        if response.status_code in [200, 201, 202]:
            # #region agent log
            with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"email_service.py:58","message":"email send success","data":{"status_code":response.status_code,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            logger.info(f"OTP email sent successfully to {email}")
            return True
        else:
            # #region agent log
            with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"F","location":"email_service.py:61","message":"email send failed - bad status","data":{"status_code":response.status_code,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            # #endregion
            logger.error(f"Failed to send OTP email. Status: {response.status_code}")
            return False
            
    except Exception as e:
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"email_service.py:65","message":"exception in send_otp_email","data":{"error":str(e),"error_type":type(e).__name__,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        logger.error(f"Error sending OTP email to {email}: {e}", exc_info=True)
        raise

