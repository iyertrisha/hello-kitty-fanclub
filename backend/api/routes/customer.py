"""
Customer routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from services.customer import (
    get_customer,
    create_customer,
    get_customer_orders,
    get_customer_credits
)
from api.middleware.validation import validate_request, validate_query_params
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('', methods=['POST'])
@validate_request(required_fields=['name', 'phone'])
def create_customer_route():
    """Create customer record"""
    try:
        data = request.validated_data
        customer = create_customer(data)
        
        return jsonify({
            'id': str(customer.id),
            'name': customer.name,
            'phone': customer.phone,
            'created_at': customer.created_at.isoformat() if customer.created_at else None
        }), 201
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating customer: {e}", exc_info=True)
        raise ValidationError(f"Failed to create customer: {str(e)}")


@customer_bp.route('/<customer_id>', methods=['GET'])
def get_customer_route(customer_id):
    """Get customer profile"""
    try:
        customer_data = get_customer(customer_id)
        return jsonify(customer_data), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting customer: {e}", exc_info=True)
        raise ValidationError(f"Failed to get customer: {str(e)}")


@customer_bp.route('/<customer_id>/orders', methods=['GET'])
def get_customer_orders_route(customer_id):
    """Get customer order history"""
    try:
        # Parse filters
        filters = {}
        if 'date_from' in request.args:
            filters['date_from'] = datetime.fromisoformat(request.args.get('date_from'))
        if 'date_to' in request.args:
            filters['date_to'] = datetime.fromisoformat(request.args.get('date_to'))
        if 'shopkeeper_id' in request.args:
            filters['shopkeeper_id'] = request.args.get('shopkeeper_id')
        
        orders = get_customer_orders(customer_id, filters)
        return jsonify({'orders': orders}), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting customer orders: {e}", exc_info=True)
        raise ValidationError(f"Failed to get customer orders: {str(e)}")


@customer_bp.route('/<customer_id>/credits', methods=['GET'])
def get_customer_credits_route(customer_id):
    """Get credit history"""
    try:
        credits = get_customer_credits(customer_id)
        return jsonify({'credits': credits}), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting customer credits: {e}", exc_info=True)
        raise ValidationError(f"Failed to get customer credits: {str(e)}")

