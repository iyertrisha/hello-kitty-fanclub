"""
Debt tracking routes - API endpoints for WhatsApp bot
"""
from flask import Blueprint, request, jsonify
from services.debt import (
    get_customer_debt,
    record_debt_entry,
    record_payment,
    get_customers_for_reminder
)
from services.debt.weekly_reminder_service import (
    get_customers_for_weekly_reminder,
    format_weekly_reminder
)
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError
from database.models import Shopkeeper
import logging

logger = logging.getLogger(__name__)

debt_bp = Blueprint('debt', __name__)


@debt_bp.route('/query', methods=['POST'])
@validate_request(required_fields=['phone'])
def query_debt_route():
    """
    Query customer debt balance
    
    Accepts: {"phone": str}
    Returns: {"success": bool, "summary": dict}
    """
    try:
        data = request.validated_data
        phone = data['phone']
        
        summary = get_customer_debt(phone=phone)
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error querying debt: {e}", exc_info=True)
        raise ValidationError(f"Failed to query debt: {str(e)}")


@debt_bp.route('/record', methods=['POST'])
@validate_request(required_fields=['phone', 'amount'])
def record_debt_route():
    """
    Record a new debt entry
    
    Accepts: {"phone": str, "amount": float, "description": str (optional), "shopkeeper_id": str (optional)}
    Returns: {"success": bool, "transaction_id": str, "new_balance": float, "blockchain_tx_id": str}
    """
    try:
        data = request.validated_data
        phone = data['phone']
        amount = float(data['amount'])
        description = data.get('description', 'Debt entry via WhatsApp')
        
        # shopkeeper_id is now optional - debt service will use customer's default_shopkeeper_id
        shopkeeper_id = data.get('shopkeeper_id')
        
        result = record_debt_entry(
            phone=phone,
            shopkeeper_id=shopkeeper_id,  # Optional - will use customer's default if not provided
            amount=amount,
            description=description
        )
        
        return jsonify({
            'success': True,
            'transaction_id': result['transaction_id'],
            'amount': result['amount'],
            'new_balance': result['new_balance'],
            'blockchain_tx_id': result.get('blockchain_tx_id')
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error recording debt: {e}", exc_info=True)
        raise ValidationError(f"Failed to record debt: {str(e)}")


@debt_bp.route('/payment', methods=['POST'])
@validate_request(required_fields=['phone', 'amount'])
def record_payment_route():
    """
    Record a payment
    
    Accepts: {"phone": str, "amount": float}
    Returns: {"success": bool, "transaction_id": str, "previous_balance": float, "new_balance": float, "blockchain_tx_id": str}
    """
    try:
        data = request.validated_data
        phone = data['phone']
        amount = float(data['amount'])
        
        result = record_payment(phone=phone, amount=amount)
        
        return jsonify({
            'success': True,
            'transaction_id': result['transaction_id'],
            'amount': result['amount'],
            'previous_balance': result['previous_balance'],
            'new_balance': result['new_balance'],
            'blockchain_tx_id': result.get('blockchain_tx_id')
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error recording payment: {e}", exc_info=True)
        raise ValidationError(f"Failed to record payment: {str(e)}")


@debt_bp.route('/reminders', methods=['GET'])
def get_reminders_route():
    """
    Get list of customers needing reminders
    
    Query params: days_overdue (optional, default: 0)
    Returns: {"success": bool, "customers": list}
    """
    try:
        days_overdue = int(request.args.get('days_overdue', 0))
        
        customers = get_customers_for_reminder(days_overdue=days_overdue)
        
        return jsonify({
            'success': True,
            'customers': customers,
            'count': len(customers)
        }), 200
    except Exception as e:
        logger.error(f"Error getting reminders: {e}", exc_info=True)
        raise ValidationError(f"Failed to get reminders: {str(e)}")


@debt_bp.route('/send-reminder', methods=['POST'])
@validate_request(required_fields=['phone'])
def send_reminder_route():
    """
    Trigger reminder for a specific customer (for manual triggering)
    
    Accepts: {"phone": str}
    Returns: {"success": bool, "message": str}
    """
    try:
        data = request.validated_data
        phone = data['phone']
        
        # Get customer debt info
        summary = get_customer_debt(phone=phone)
        
        # Return customer info for bot to send reminder
        return jsonify({
            'success': True,
            'customer': {
                'phone': summary['phone'],
                'name': summary['customer_name'],
                'total_debt': summary['total_debt']
            },
            'message': f"Reminder prepared for {summary['customer_name']}"
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error sending reminder: {e}", exc_info=True)
        raise ValidationError(f"Failed to send reminder: {str(e)}")


@debt_bp.route('/weekly-reminders', methods=['GET'])
def get_weekly_reminders_route():
    """
    Get customers for weekly reminders
    
    Query params: days_threshold (optional, default: 7)
    Returns: {
        "customers": [{"phone": str, "debt": float, "days_since_first": int, "history": dict}]
    }
    """
    try:
        days_threshold = int(request.args.get('days_threshold', 7))
        
        customers = get_customers_for_weekly_reminder(days_threshold=days_threshold)
        
        return jsonify({
            'customers': customers,
            'count': len(customers)
        }), 200
    except Exception as e:
        logger.error(f"Error getting weekly reminders: {e}", exc_info=True)
        raise ValidationError(f"Failed to get weekly reminders: {str(e)}")

