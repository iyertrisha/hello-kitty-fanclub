"""
Grocery routes - API endpoints for grocery ordering
"""
from flask import Blueprint, request, jsonify
from services.grocery import (
    parse_grocery_list,
    calculate_bill,
    create_grocery_order,
    get_products_for_shopkeeper
)
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

grocery_bp = Blueprint('grocery', __name__)


@grocery_bp.route('/parse', methods=['POST'])
@validate_request(required_fields=['list', 'shopkeeper_id'])
def parse_grocery_list_route():
    """
    Parse grocery list and match products
    
    Accepts: {
        "list": str,
        "shopkeeper_id": str,
        "parsed_items": [{"name": str, "quantity": float, "unit": str}] (optional)
    }
    Returns: {
        "items": [...],
        "total": float,
        "unmatched": [...]
    }
    """
    try:
        data = request.validated_data
        list_text = data['list']
        shopkeeper_id = data['shopkeeper_id']
        parsed_items = data.get('parsed_items', [])
        
        if not parsed_items:
            return jsonify({
                'error': 'parsed_items required. Please parse the list on the frontend first.'
            }), 400
        
        result = parse_grocery_list(list_text, shopkeeper_id, parsed_items)
        
        return jsonify({
            'items': result['items'],
            'total': result['total'],
            'unmatched': result['unmatched']
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error parsing grocery list: {e}", exc_info=True)
        raise ValidationError(f"Failed to parse grocery list: {str(e)}")


@grocery_bp.route('/create-order', methods=['POST'])
@validate_request(required_fields=['customer_phone', 'items', 'shopkeeper_id'])
def create_grocery_order_route():
    """
    Create grocery order
    
    Accepts: {
        "customer_phone": str,
        "items": [...],
        "shopkeeper_id": str
    }
    Returns: {
        "success": bool,
        "order_id": str,
        "transaction_id": str,
        "bill": {...},
        "blockchain_tx_id": str (optional)
    }
    """
    try:
        data = request.validated_data
        customer_phone = data['customer_phone']
        items = data['items']
        shopkeeper_id = data['shopkeeper_id']
        
        result = create_grocery_order(customer_phone, items, shopkeeper_id)
        
        return jsonify({
            'success': True,
            'order_id': result['order_id'],
            'transaction_id': result['transaction_id'],
            'bill': result['bill'],
            'blockchain_tx_id': result.get('blockchain_tx_id')
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating grocery order: {e}", exc_info=True)
        raise ValidationError(f"Failed to create order: {str(e)}")


@grocery_bp.route('/products', methods=['GET'])
def get_products_route():
    """
    Get products for a shopkeeper
    
    Query params: shopkeeper_id (required)
    Returns: {
        "products": [...]
    }
    """
    try:
        shopkeeper_id = request.args.get('shopkeeper_id')
        
        if not shopkeeper_id:
            raise ValidationError("shopkeeper_id is required")
        
        products = get_products_for_shopkeeper(shopkeeper_id)
        
        # Convert to dict format
        products_list = []
        for product in products:
            products_list.append({
                'id': str(product.id),
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'stock_quantity': product.stock_quantity,
                'description': product.description
            })
        
        return jsonify({
            'products': products_list
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting products: {e}", exc_info=True)
        raise ValidationError(f"Failed to get products: {str(e)}")

