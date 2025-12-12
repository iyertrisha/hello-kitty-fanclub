"""
Twilio WhatsApp Client
Handles sending/receiving WhatsApp messages via Twilio API

⚠️ DEPRECATED: This module is deprecated in favor of the free WhatsApp bot
using whatsapp-web.js. See backend/whatsapp-bot/ for the new implementation.

This file is kept for reference but is no longer actively used.
"""
import os
import logging
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from flask import request

logger = logging.getLogger(__name__)


class TwilioClient:
    """Twilio WhatsApp client for sending and receiving messages"""
    
    def __init__(self, account_sid=None, auth_token=None, whatsapp_number=None):
        """
        Initialize Twilio client
        
        Args:
            account_sid: Twilio Account SID (defaults to env var)
            auth_token: Twilio Auth Token (defaults to env var)
            whatsapp_number: Twilio WhatsApp number (defaults to env var)
        """
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = whatsapp_number or os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
        
        self.client = Client(self.account_sid, self.auth_token)
        self.validator = RequestValidator(self.auth_token)
        
        logger.info("TwilioClient initialized")
    
    def send_message(self, to, body):
        """
        Send WhatsApp message
        
        Args:
            to: Recipient phone number (e.g., 'whatsapp:+919876543210')
            body: Message body text
        
        Returns:
            dict: {"sid": str, "status": str}
        """
        try:
            # Ensure 'whatsapp:' prefix
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            message = self.client.messages.create(
                from_=self.whatsapp_number,
                body=body,
                to=to
            )
            
            logger.info(f"Message sent to {to}, SID: {message.sid}, Status: {message.status}")
            
            return {
                "sid": message.sid,
                "status": message.status
            }
        except Exception as e:
            logger.error(f"Failed to send message to {to}: {e}", exc_info=True)
            raise
    
    def send_template_message(self, to, template, params):
        """
        Send templated message with parameter substitution
        
        Args:
            to: Recipient phone number
            template: Message template with {placeholders}
            params: Dictionary of parameters to substitute
        
        Returns:
            dict: {"sid": str, "status": str}
        """
        try:
            body = template.format(**params)
            return self.send_message(to, body)
        except KeyError as e:
            logger.error(f"Missing template parameter: {e}")
            raise ValueError(f"Missing template parameter: {e}")
        except Exception as e:
            logger.error(f"Failed to send template message: {e}", exc_info=True)
            raise
    
    def validate_request(self, flask_request):
        """
        Validate Twilio webhook signature
        
        Args:
            flask_request: Flask request object
        
        Returns:
            bool: True if signature is valid
        """
        try:
            # Get the full URL
            url = flask_request.url
            
            # Get form data as dict
            form_data = {}
            for key in flask_request.form.keys():
                form_data[key] = flask_request.form.get(key)
            
            # Get signature from header
            signature = flask_request.headers.get('X-Twilio-Signature', '')
            
            if not signature:
                logger.warning("Missing X-Twilio-Signature header")
                return False
            
            # Validate signature
            is_valid = self.validator.validate(url, form_data, signature)
            
            if not is_valid:
                logger.warning(f"Invalid Twilio signature for request from {flask_request.remote_addr}")
            
            return is_valid
        except Exception as e:
            logger.error(f"Error validating Twilio request: {e}", exc_info=True)
            return False
    
    def receive_message(self, form_data):
        """
        Parse and normalize incoming WhatsApp message
        
        Args:
            form_data: Flask request.form or dict with Twilio webhook data
        
        Returns:
            dict: {
                "from": str (normalized phone, e.g., +919876543210),
                "body": str,
                "message_sid": str,
                "to": str,
                "raw_from": str (original with whatsapp: prefix)
            }
        """
        try:
            raw_from = form_data.get('From', '')
            body = form_data.get('Body', '')
            message_sid = form_data.get('MessageSid', '')
            to = form_data.get('To', '')
            
            # Normalize phone number (strip whatsapp: prefix)
            normalized_from = raw_from.replace('whatsapp:', '') if raw_from.startswith('whatsapp:') else raw_from
            
            return {
                "from": normalized_from,
                "body": body.strip(),
                "message_sid": message_sid,
                "to": to,
                "raw_from": raw_from
            }
        except Exception as e:
            logger.error(f"Error parsing incoming message: {e}", exc_info=True)
            raise ValueError(f"Invalid message format: {e}")

