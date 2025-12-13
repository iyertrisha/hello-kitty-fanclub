"""
WhatsApp routes
Handles WhatsApp webhooks and message sending via Twilio

⚠️ DEPRECATED: These routes are deprecated in favor of the free WhatsApp bot
using whatsapp-web.js. See backend/whatsapp-bot/ and backend/api/routes/debt.py
for the new implementation.

These routes are kept for reference but are no longer actively used.
"""
from flask import Blueprint, request, jsonify
from functools import wraps
import os
import logging
import requests
import time
from datetime import datetime, timedelta

from integrations.whatsapp import TwilioClient
from integrations.dialogflow import DialogflowClient
from services.transaction import (
    get_transaction_by_id,
    update_transaction_status,
    create_pending_confirmation,
    get_pending_confirmation_by_phone,
    update_pending_confirmation_status
)
from services.monthly_confirmation import (
    send_monthly_confirmation,
    process_confirmation_response
)
from api.middleware.error_handler import ValidationError, NotFoundError, UnauthorizedError
from database.models import Customer, Shopkeeper

logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint('whatsapp', __name__)


def require_internal_api_key(f):
    """
    Require internal API key for internal endpoints
    
    Usage:
        @require_internal_api_key
        def my_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = os.getenv('WHATSAPP_INTERNAL_API_KEY')
        if not api_key:
            logger.warning("WHATSAPP_INTERNAL_API_KEY not set, skipping auth check")
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise UnauthorizedError("Missing or invalid authorization header")
        
        token = auth_header.split(' ')[1]
        if token != api_key:
            raise UnauthorizedError("Invalid API key")
        
        return f(*args, **kwargs)
    
    return decorated_function


def call_vineet_api_with_retry(transaction_id, max_retries=3):
    """
    Call Vineet API to confirm transaction with exponential backoff retry
    
    Args:
        transaction_id: Transaction ID to confirm
        max_retries: Maximum number of retry attempts
    
    Returns:
        bool: True if successful, False otherwise
    """
    vineet_api_base_url = os.getenv('VINEET_API_BASE_URL', 'http://localhost:5000/api')
    endpoint = f"{vineet_api_base_url}/transactions/{transaction_id}/confirm"
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                endpoint,
                json={'transaction_id': str(transaction_id)},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully confirmed transaction {transaction_id} via Vineet API")
                return True
            else:
                logger.warning(
                    f"Vineet API returned {response.status_code} for transaction {transaction_id}, "
                    f"attempt {attempt + 1}/{max_retries}"
                )
        
        except requests.exceptions.RequestException as e:
            logger.warning(
                f"Vineet API call failed for transaction {transaction_id}, "
                f"attempt {attempt + 1}/{max_retries}: {e}"
            )
        
        # Exponential backoff: wait 2^attempt seconds
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    
    logger.error(f"Failed to confirm transaction {transaction_id} via Vineet API after {max_retries} attempts")
    return False


@whatsapp_bp.route('/webhook', methods=['POST'])
def webhook_route():
    """
    Receive WhatsApp webhook from Twilio
    
    Validates signature, parses message, detects intent, and routes accordingly
    """
    try:
        # Initialize clients
        twilio_client = TwilioClient()
        dialogflow_client = DialogflowClient()
        
        # Validate Twilio signature
        if not twilio_client.validate_request(request):
            logger.warning(f"Invalid Twilio signature from {request.remote_addr}")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Parse incoming message
        message_data = twilio_client.receive_message(request.form)
        phone = message_data['from']
        body = message_data['body']
        message_sid = message_data['message_sid']
        
        logger.info(f"Webhook received from {phone}: {body[:50]}...")
        
        # Normalize phone (ensure + prefix)
        if not phone.startswith('+'):
            phone = f'+{phone.lstrip("+")}'
        
        # Check for pending confirmation
        pending_confirmation = get_pending_confirmation_by_phone(phone)
        
        # Detect intent via Dialogflow
        intent_result = dialogflow_client.detect_intent_texts(session_id=phone, text=body)
        intent = intent_result['intent']
        confidence = intent_result['confidence']
        
        logger.info(f"Detected intent: {intent} (confidence: {confidence:.2f}) for {phone}")
        
        # Route based on intent and pending confirmation
        reply_message = None
        
        # Handle credit confirmation (YES/NO response)
        if pending_confirmation and pending_confirmation.status == 'pending':
            body_upper = body.strip().upper()
            
            if body_upper in ['YES', 'Y', 'CONFIRM', 'OK']:
                # Confirm transaction
                transaction_id = pending_confirmation.transaction_id.id
                
                # Update pending confirmation status
                update_pending_confirmation_status(pending_confirmation.id, 'confirmed')
                
                # Update transaction status
                update_transaction_status(transaction_id, 'verified')
                
                # Call Vineet API
                vineet_success = call_vineet_api_with_retry(transaction_id)
                
                if vineet_success:
                    reply_message = "✅ Credit confirmed successfully! Transaction has been recorded."
                else:
                    reply_message = "✅ Credit confirmed. Note: There was an issue updating the system, but your confirmation was received."
                
                logger.info(f"Transaction {transaction_id} confirmed by {phone}")
            
            elif body_upper in ['NO', 'N', 'REJECT', 'CANCEL']:
                # Reject transaction
                transaction_id = pending_confirmation.transaction_id.id
                
                # Update pending confirmation status
                update_pending_confirmation_status(pending_confirmation.id, 'rejected')
                
                # Update transaction status
                update_transaction_status(transaction_id, 'disputed')
                
                reply_message = "❌ Credit request rejected. Transaction has been cancelled."
                
                logger.info(f"Transaction {transaction_id} rejected by {phone}")
            
            else:
                # Invalid response to pending confirmation
                reply_message = "Please reply YES to confirm or NO to reject the credit request."
        
        # Handle monthly confirmation response
        elif intent in ['monthly.response', 'monthly.confirm', 'monthly.dispute']:
            # Try to find customer by phone
            try:
                customer = Customer.objects.get(phone=phone)
                response_result = process_confirmation_response(customer.id, body)
                
                if response_result['action'] == 'confirmed':
                    reply_message = "✅ Thank you for confirming your monthly summary!"
                elif response_result['action'] == 'disputed':
                    disputed_count = len(response_result.get('disputed_transactions', []))
                    reply_message = f"⚠️ Your dispute has been recorded. {disputed_count} transaction(s) have been flagged for review."
                
            except Customer.DoesNotExist:
                reply_message = "Sorry, we couldn't find your account. Please contact support."
        
        # Handle order intents (future implementation)
        elif intent.startswith('order.'):
            # Placeholder for order routing
            reply_message = "Order functionality is coming soon! For now, please contact your shopkeeper directly."
        
        # Default fallback
        else:
            if intent_result['fulfillment_text']:
                reply_message = intent_result['fulfillment_text']
            else:
                reply_message = "I didn't understand that. Please try again or contact support."
        
        # Send reply if we have one
        if reply_message:
            try:
                whatsapp_phone = f'whatsapp:{phone}'
                send_result = twilio_client.send_message(whatsapp_phone, reply_message)
                logger.info(f"Sent reply to {phone}, SID: {send_result['sid']}")
            except Exception as e:
                logger.error(f"Failed to send reply to {phone}: {e}", exc_info=True)
        
        # Return 200 OK (Twilio expects this)
        return '', 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Still return 200 to prevent Twilio from retrying
        return '', 200


@whatsapp_bp.route('/confirm-credit', methods=['POST'])
@require_internal_api_key
def confirm_credit_route():
    """
    Internal endpoint to trigger credit confirmation flow
    
    Accepts: {"transaction_id": str}
    Returns: {"success": bool, "confirmation_id": str}
    """
    try:
        data = request.get_json()
        if not data or 'transaction_id' not in data:
            raise ValidationError("Missing required field: transaction_id")
        
        transaction_id = data['transaction_id']
        
        # Get transaction
        transaction = get_transaction_by_id(transaction_id)
        
        # Get customer phone
        customer = transaction.customer_id
        phone = customer.phone
        if not phone.startswith('+'):
            phone = f'+{phone.lstrip("+")}'
        
        # Get shopkeeper name
        shopkeeper = transaction.shopkeeper_id
        shopkeeper_name = shopkeeper.name
        
        # Create pending confirmation (24h TTL)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        pending_confirmation = create_pending_confirmation(
            transaction_id=transaction_id,
            phone=phone,
            amount=transaction.amount,
            shopkeeper_name=shopkeeper_name,
            expires_at=expires_at
        )
        
        # Send WhatsApp message
        twilio_client = TwilioClient()
        message_template = "Confirm ₹{amount} credit to {shopkeeper}? Reply YES/NO"
        message = message_template.format(
            amount=transaction.amount,
            shopkeeper=shopkeeper_name
        )
        
        whatsapp_phone = f'whatsapp:{phone}'
        send_result = twilio_client.send_message(whatsapp_phone, message)
        
        logger.info(
            f"Credit confirmation sent to {phone} for transaction {transaction_id}, "
            f"message SID: {send_result['sid']}"
        )
        
        return jsonify({
            'success': True,
            'confirmation_id': str(pending_confirmation.id),
            'message_sid': send_result['sid']
        }), 200
    
    except NotFoundError as e:
        raise
    except ValidationError as e:
        raise
    except Exception as e:
        logger.error(f"Error in confirm-credit route: {e}", exc_info=True)
        raise ValidationError(f"Failed to send credit confirmation: {str(e)}")


@whatsapp_bp.route('/monthly-confirmation', methods=['POST'])
@require_internal_api_key
def monthly_confirmation_route():
    """
    Internal endpoint to send monthly confirmation
    
    Accepts: {"customer_id": str, "month": int (optional), "year": int (optional)}
    Returns: {"success": bool, "message_sid": str}
    """
    try:
        data = request.get_json()
        if not data or 'customer_id' not in data:
            raise ValidationError("Missing required field: customer_id")
        
        customer_id = data['customer_id']
        month = data.get('month')
        year = data.get('year')
        
        # Send monthly confirmation
        result = send_monthly_confirmation(customer_id, month, year)
        
        return jsonify({
            'success': result['success'],
            'message_sid': result['message_sid'],
            'summary': result.get('summary')
        }), 200
    
    except NotFoundError as e:
        raise
    except ValidationError as e:
        raise
    except Exception as e:
        logger.error(f"Error in monthly-confirmation route: {e}", exc_info=True)
        raise ValidationError(f"Failed to send monthly confirmation: {str(e)}")


@whatsapp_bp.route('/send', methods=['POST'])
@require_internal_api_key
def send_message_route():
    """
    Internal endpoint to send WhatsApp message
    
    Accepts: {"to": str, "body": str}
    Returns: {"success": bool, "sid": str, "status": str}
    """
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        if 'to' not in data or 'body' not in data:
            raise ValidationError("Missing required fields: to, body")
        
        to = data['to']
        body = data['body']
        
        # Send message
        twilio_client = TwilioClient()
        result = twilio_client.send_message(to, body)
        
        logger.info(f"Message sent to {to} via /send endpoint, SID: {result['sid']}")
        
        return jsonify({
            'success': True,
            'sid': result['sid'],
            'status': result['status']
        }), 200
    
    except ValidationError as e:
        raise
    except Exception as e:
        logger.error(f"Error in send message route: {e}", exc_info=True)
        raise ValidationError(f"Failed to send message: {str(e)}")


@whatsapp_bp.route('/shopkeeper-by-phone', methods=['GET'])
@require_internal_api_key
def get_shopkeeper_by_phone_route():
    """Get shopkeeper by phone number (for WhatsApp bot)"""
    try:
        phone = request.args.get('phone')
        if not phone:
            raise ValidationError("Missing required parameter: phone")
        
        # Normalize phone number
        if not phone.startswith('+'):
            phone = f'+{phone.lstrip("+")}'
        
        try:
            shopkeeper = Shopkeeper.objects.get(phone=phone)
        except Shopkeeper.DoesNotExist:
            return jsonify({
                'shopkeeper': None,
                'message': 'Shopkeeper not found'
            }), 200
        
        return jsonify({
            'shopkeeper': {
                'id': str(shopkeeper.id),
                'name': shopkeeper.name,
                'phone': shopkeeper.phone,
                'address': shopkeeper.address
            }
        }), 200
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting shopkeeper by phone: {e}", exc_info=True)
        raise ValidationError(f"Failed to get shopkeeper: {str(e)}")


@whatsapp_bp.route('/products', methods=['GET'])
@require_internal_api_key
def get_products_route():
    """Get products for shopkeeper (for WhatsApp bot)"""
    try:
        shopkeeper_phone = request.args.get('shopkeeper_phone')
        if not shopkeeper_phone:
            raise ValidationError("Missing required parameter: shopkeeper_phone")
        
        # Normalize phone number
        if not shopkeeper_phone.startswith('+'):
            shopkeeper_phone = f'+{shopkeeper_phone.lstrip("+")}'
        
        # Get shopkeeper
        try:
            shopkeeper = Shopkeeper.objects.get(phone=shopkeeper_phone)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper with phone {shopkeeper_phone} not found")
        
        # Get products
        from database.models import Product
        products = Product.objects(shopkeeper_id=shopkeeper.id).order_by('name')
        
        # Format for WhatsApp (text/menu format)
        product_list = []
        for product in products:
            if product.stock_quantity > 0:
                product_list.append({
                    'id': str(product.id),
                    'name': product.name,
                    'price': product.price,
                    'stock': product.stock_quantity,
                    'category': product.category or 'General'
                })
        
        # Create formatted text for WhatsApp
        if product_list:
            text_lines = [f"📦 *{shopkeeper.name} - Product Catalog*\n"]
            current_category = None
            for product in product_list:
                if product['category'] != current_category:
                    current_category = product['category']
                    text_lines.append(f"\n*{current_category}*")
                text_lines.append(
                    f"• {product['name']} - ₹{product['price']:.2f} (Stock: {product['stock']})"
                )
            formatted_text = '\n'.join(text_lines)
        else:
            formatted_text = "No products available at the moment."
        
        return jsonify({
            'shopkeeper': {
                'id': str(shopkeeper.id),
                'name': shopkeeper.name
            },
            'products': product_list,
            'formatted_text': formatted_text
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting products: {e}", exc_info=True)
        raise ValidationError(f"Failed to get products: {str(e)}")
