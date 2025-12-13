"""
OTP service - Generate, store, and verify OTP codes
"""
from database.models import OTPVerification
from services.email import send_otp_email
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3  # Max OTP requests per email per 15 minutes


def generate_otp():
    """
    Generate a 6-digit random OTP
    
    Returns:
        str: 6-digit OTP code
    """
    return str(random.randint(100000, 999999))


def create_otp_record(email):
    """
    Create OTP record and send email
    
    Args:
        email: User email address
    
    Returns:
        str: Generated OTP code
    
    Raises:
        ValidationError: If too many OTP requests
    """
    # #region agent log
    try:
        import json
        from pathlib import Path
        log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"otp_service.py:26","message":"create_otp_record entry","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except Exception:
        pass  # Ignore debug log errors
    # #endregion
    # Check rate limiting (max 3 requests per 15 minutes)
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    recent_otps = OTPVerification.objects(
        email=email,
        created_at__gte=fifteen_minutes_ago
    ).count()
    # #region agent log
    try:
        import json
        from pathlib import Path
        log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"otp_service.py:44","message":"rate limit check","data":{"email":email,"recent_otps":recent_otps,"max_allowed":MAX_OTP_ATTEMPTS,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except Exception:
        pass  # Ignore debug log errors
    # #endregion
    
    if recent_otps >= MAX_OTP_ATTEMPTS:
        from api.middleware.error_handler import ValidationError
        raise ValidationError(f"Too many OTP requests. Please wait before requesting another OTP.")
    
    # Invalidate any existing unused OTPs for this email
    OTPVerification.objects(email=email, used=False).update(set__used=True)
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    # #region agent log
    try:
        import json
        from pathlib import Path
        log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"otp_service.py:54","message":"OTP generated","data":{"email":email,"otp_code":otp_code,"expires_at":str(expires_at),"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except Exception:
        pass  # Ignore debug log errors
    # #endregion
    
    # Create OTP record
    otp_record = OTPVerification(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    otp_record.save()
    # #region agent log
    try:
        import json
        from pathlib import Path
        log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"otp_service.py:63","message":"OTP record saved to DB","data":{"email":email,"otp_id":str(otp_record.id),"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except Exception:
        pass  # Ignore debug log errors
    # #endregion
    
    # Send OTP email
    # #region agent log
    try:
        import json
        from pathlib import Path
        log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"otp_service.py:66","message":"before send_otp_email","data":{"email":email,"otp_code":otp_code,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except Exception:
        pass  # Ignore debug log errors
    # #endregion
    try:
        send_otp_email(email, otp_code)
        # #region agent log
        try:
            import json
            from pathlib import Path
            log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"otp_service.py:69","message":"send_otp_email returned successfully","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except Exception:
            pass  # Ignore debug log errors
        # #endregion
    except Exception as e:
        # #region agent log
        try:
            import json
            from pathlib import Path
            log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"otp_service.py:72","message":"send_otp_email exception","data":{"email":email,"error":str(e),"error_type":type(e).__name__,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except Exception:
            pass  # Ignore debug log errors
        # #endregion
        logger.error(f"Failed to send OTP email: {e}")
        # Delete the OTP record if email failed
        otp_record.delete()
        # #region agent log
        try:
            import json
            from pathlib import Path
            log_path = Path(r'c:\hello-kitty-fanclub\.cursor\debug.log')
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"otp_service.py:75","message":"OTP record deleted after email failure","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except Exception:
            pass  # Ignore debug log errors
        # #endregion
        raise
    
    logger.info(f"OTP created for {email}, expires at {expires_at}")
    
    return otp_code


def verify_otp(email, otp_code):
    """
    Verify OTP code
    
    Args:
        email: User email address
        otp_code: OTP code to verify
    
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    try:
        # Find the most recent unused OTP for this email
        otp_record = OTPVerification.objects(
            email=email,
            otp_code=otp_code,
            used=False
        ).order_by('-created_at').first()
        
        if not otp_record:
            logger.warning(f"Invalid OTP code for {email}")
            return False
        
        # Check if OTP is expired
        if datetime.utcnow() > otp_record.expires_at:
            logger.warning(f"Expired OTP code for {email}")
            return False
        
        # Mark OTP as used
        otp_record.used = True
        otp_record.save()
        
        logger.info(f"OTP verified successfully for {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}", exc_info=True)
        return False


def invalidate_otp(email):
    """
    Mark all unused OTPs for an email as used
    
    Args:
        email: User email address
    """
    OTPVerification.objects(email=email, used=False).update(set__used=True)
    logger.info(f"Invalidated all OTPs for {email}")


def cleanup_expired_otps():
    """
    Clean up expired OTPs (can be called as a background task)
    """
    try:
        expired_count = OTPVerification.objects(expires_at__lt=datetime.utcnow()).delete()
        logger.info(f"Cleaned up {expired_count} expired OTP records")
    except Exception as e:
        logger.error(f"Error cleaning up expired OTPs: {e}")

