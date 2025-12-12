"""
Shopkeeper routes
"""
from flask import Blueprint, request, jsonify
from services.shopkeeper import (
    register_shopkeeper,
    get_shopkeeper,
    update_shopkeeper,
    calculate_credit_score,
    get_inventory
)
from database.models import Product
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

shopkeeper_bp = Blueprint('shopkeeper', __name__)


@shopkeeper_bp.route('/register', methods=['POST'])
@validate_request(required_fields=['name', 'address', 'phone', 'wallet_address'])
def register_shopkeeper_route():
    """Register new shopkeeper"""
    try:
        data = request.validated_data
        shopkeeper = register_shopkeeper(data)
        
        return jsonify({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'wallet_address': shopkeeper.wallet_address,
            'registered_at': shopkeeper.registered_at.isoformat() if shopkeeper.registered_at else None
        }), 201
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error registering shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to register shopkeeper: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>', methods=['GET'])
def get_shopkeeper_route(shopkeeper_id):
    """Get shopkeeper profile"""
    try:
        # Validate ObjectId format
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        shopkeeper_data = get_shopkeeper(shopkeeper_id)
        return jsonify(shopkeeper_data), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to get shopkeeper: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>', methods=['PUT'])
@validate_request()
def update_shopkeeper_route(shopkeeper_id):
    """Update shopkeeper profile"""
    try:
        data = request.validated_data
        shopkeeper = update_shopkeeper(shopkeeper_id, data)
        
        return jsonify({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'address': shopkeeper.address,
            'phone': shopkeeper.phone,
            'email': shopkeeper.email
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to update shopkeeper: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/credit-score', methods=['GET'])
def get_credit_score_route(shopkeeper_id):
    """Get credit score"""
    try:
        credit_data = calculate_credit_score(shopkeeper_id)
        return jsonify(credit_data), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting credit score: {e}", exc_info=True)
        raise ValidationError(f"Failed to get credit score: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/inventory', methods=['GET'])
def get_inventory_route(shopkeeper_id):
    """Get shopkeeper inventory"""
    try:
        inventory = get_inventory(shopkeeper_id)
        return jsonify({'inventory': inventory}), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to get inventory: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/inventory/<product_id>', methods=['PUT'])
@validate_request()
def update_inventory_route(shopkeeper_id, product_id):
    """Update inventory item"""
    try:
        data = request.validated_data
        
        # Get product
        try:
            product = Product.objects.get(id=product_id, shopkeeper_id=shopkeeper_id)
        except Product.DoesNotExist:
            raise NotFoundError(f"Product {product_id} not found for shopkeeper {shopkeeper_id}")
        
        # Update allowed fields
        if 'price' in data:
            product.price = data['price']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stock_quantity']
        if 'name' in data:
            product.name = data['name']
        if 'category' in data:
            product.category = data['category']
        if 'description' in data:
            product.description = data['description']
        
        product.save()
        
        return jsonify({
            'id': str(product.id),
            'name': product.name,
            'price': product.price,
            'stock_quantity': product.stock_quantity
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to update inventory: {str(e)}")

