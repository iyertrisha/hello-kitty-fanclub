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
    # Check rate limiting (max 3 requests per 15 minutes)
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    recent_otps = OTPVerification.objects(
        email=email,
        created_at__gte=fifteen_minutes_ago
    ).count()
    
    if recent_otps >= MAX_OTP_ATTEMPTS:
        from api.middleware.error_handler import ValidationError
        raise ValidationError(f"Too many OTP requests. Please wait before requesting another OTP.")
    
    # Invalidate any existing unused OTPs for this email
    OTPVerification.objects(email=email, used=False).update(set__used=True)
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Create OTP record
    otp_record = OTPVerification(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    otp_record.save()
    
    # Send OTP email
    try:
        send_otp_email(email, otp_code)
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        # Delete the OTP record if email failed
        otp_record.delete()
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

