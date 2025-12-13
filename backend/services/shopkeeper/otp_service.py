"""
Shopkeeper OTP service - Generate, store, and verify OTP codes for phone numbers
"""
from database.models import OTPVerification
from datetime import datetime, timedelta
import random
import logging
import os

logger = logging.getLogger(__name__)

OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3  # Max OTP requests per phone per 15 minutes


def generate_otp():
    """
    Generate a 6-digit random OTP
    
    Returns:
        str: 6-digit OTP code
    """
    return str(random.randint(100000, 999999))


def create_otp_record(phone):
    """
    Create OTP record and send via WhatsApp or log in dev mode
    
    Args:
        phone: User phone number (with country code, e.g., +919876543210)
    
    Returns:
        str: Generated OTP code
    
    Raises:
        ValidationError: If too many OTP requests
    """
    # Normalize phone number (ensure + prefix)
    if not phone.startswith('+'):
        phone = f'+{phone.lstrip("+")}'
    
    # Check rate limiting (max 3 requests per 15 minutes)
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    recent_otps = OTPVerification.objects(
        phone=phone,
        created_at__gte=fifteen_minutes_ago
    ).count()
    
    if recent_otps >= MAX_OTP_ATTEMPTS:
        from api.middleware.error_handler import ValidationError
        raise ValidationError(f"Too many OTP requests. Please wait before requesting another OTP.")
    
    # Invalidate any existing unused OTPs for this phone
    OTPVerification.objects(phone=phone, used=False).update(set__used=True)
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Create OTP record with phone field
    otp_record = OTPVerification(
        phone=phone,
        otp_code=otp_code,
        expires_at=expires_at
    )
    otp_record.save()
    
    # Send OTP via WhatsApp or log in dev mode
    try:
        # Try to send via WhatsApp (Twilio)
        try:
            from integrations.whatsapp import TwilioClient
            twilio_client = TwilioClient()
            message = f"Your OTP code for shopkeeper login is: {otp_code}\n\nThis code will expire in 10 minutes."
            whatsapp_phone = f'whatsapp:{phone}'
            result = twilio_client.send_message(whatsapp_phone, message)
            logger.info(f"OTP sent via WhatsApp to {phone}, SID: {result['sid']}")
        except Exception as e:
            # Fallback to dev mode (log OTP)
            logger.warning(f"Failed to send OTP via WhatsApp: {e}. Using development mode.")
            logger.warning("=" * 80)
            logger.warning(f"⚠️  DEVELOPMENT MODE: Shopkeeper OTP")
            logger.warning("=" * 80)
            logger.warning(f"📱 Phone: {phone}")
            logger.warning(f"🔑 OTP Code: {otp_code}")
            logger.warning(f"⏰ Expires in: 10 minutes")
            logger.warning("=" * 80)
            print("\n" + "=" * 80)
            print(f"⚠️  DEVELOPMENT MODE: Shopkeeper OTP (WhatsApp unavailable)")
            print(f"📱 Phone: {phone}")
            print(f"🔑 OTP Code: {otp_code}")
            print(f"⏰ Expires in: 10 minutes")
            print("=" * 80 + "\n")
    except Exception as e:
        logger.error(f"Error sending OTP: {e}")
        # Continue anyway - OTP is stored
    
    logger.info(f"OTP created for {phone}, expires at {expires_at}")
    
    return otp_code


def verify_otp(phone, otp_code):
    """
    Verify OTP code
    
    Args:
        phone: User phone number
        otp_code: OTP code to verify
    
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    # Normalize phone number
    if not phone.startswith('+'):
        phone = f'+{phone.lstrip("+")}'
    
    try:
        # Find the most recent unused OTP for this phone
        otp_record = OTPVerification.objects(
            phone=phone,
            otp_code=otp_code,
            used=False
        ).order_by('-created_at').first()
        
        if not otp_record:
            logger.warning(f"Invalid OTP code for {phone}")
            return False
        
        # Check if OTP is expired
        if datetime.utcnow() > otp_record.expires_at:
            logger.warning(f"Expired OTP code for {phone}")
            return False
        
        # Mark OTP as used
        otp_record.used = True
        otp_record.save()
        
        logger.info(f"OTP verified successfully for {phone}")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}", exc_info=True)
        return False


def invalidate_otp(phone):
    """
    Mark all unused OTPs for a phone as used
    
    Args:
        phone: User phone number
    """
    # Normalize phone number
    if not phone.startswith('+'):
        phone = f'+{phone.lstrip("+")}'
    
    OTPVerification.objects(phone=phone, used=False).update(set__used=True)
    logger.info(f"Invalidated all OTPs for {phone}")

