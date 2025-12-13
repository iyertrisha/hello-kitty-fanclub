"""
Product routes for Flutter app integration
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from database.models import Product, Shopkeeper
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)


@products_bp.route('', methods=['GET'])
def get_products_route():
    """
    Get products for a shopkeeper
    
    Query params: shopkeeper_id (optional - if not provided, returns all products)
    Returns: {
        "data": [...]
    }
    """
    try:
        shopkeeper_id = request.args.get('shopkeeper_id')
        
        if shopkeeper_id:
            # Get products for specific shopkeeper
            try:
                shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            except Shopkeeper.DoesNotExist:
                raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
            
            products = Product.objects(shopkeeper_id=shopkeeper)
        else:
            # Get all products (for Flutter app - may need shopkeeper_id in session later)
            products = Product.objects()
        
        products_list = []
        for product in products:
            products_list.append({
                'id': str(product.id),
                'name': product.name,
                'description': product.description or '',
                'price': product.price,
                'stock': product.stock_quantity,
                'category': product.category or '',
                'imageUrl': None,  # Not in backend model yet
                'createdAt': product.created_at.isoformat() if product.created_at else datetime.utcnow().isoformat(),
                'updatedAt': None,  # Not in backend model yet
                'synced': True  # Products from backend are synced
            })
        
        return jsonify({
            'data': products_list,
            'count': len(products_list)
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting products: {e}", exc_info=True)
        raise ValidationError(f"Failed to get products: {str(e)}")


@products_bp.route('', methods=['POST'])
@validate_request(required_fields=['name', 'price', 'stock'])
def create_product_route():
    """
    Create a new product
    
    Request body: {
        "name": "...",
        "description": "...",
        "price": 100.0,
        "stock": 50,
        "category": "...",
        "shopkeeper_id": "..." (optional - may come from session later)
    }
    Returns: {
        "data": {...}
    }
    """
    try:
        data = request.validated_data
        
        # Get shopkeeper_id from request or use default (for now)
        shopkeeper_id = data.get('shopkeeper_id')
        if not shopkeeper_id:
            # Try to get first shopkeeper as default (for testing)
            shopkeeper = Shopkeeper.objects(is_active=True).first()
            if not shopkeeper:
                raise ValidationError("No active shopkeeper found. Please provide shopkeeper_id.")
            shopkeeper_id = str(shopkeeper.id)
        
        try:
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        # Create product
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            stock_quantity=int(data.get('stock', 0)),
            category=data.get('category', ''),
            shopkeeper_id=shopkeeper
        )
        product.save()
        
        product_data = {
            'id': str(product.id),
            'name': product.name,
            'description': product.description or '',
            'price': product.price,
            'stock': product.stock_quantity,
            'category': product.category or '',
            'imageUrl': None,
            'createdAt': product.created_at.isoformat() if product.created_at else datetime.utcnow().isoformat(),
            'updatedAt': None,
            'synced': True
        }
        
        logger.info(f"Created product {product.id} for shopkeeper {shopkeeper_id}")
        return jsonify({
            'data': product_data,
            'success': True
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        raise ValidationError(f"Failed to create product: {str(e)}")


@products_bp.route('/<product_id>', methods=['PUT'])
@validate_request()
def update_product_route(product_id):
    """
    Update a product
    
    Request body: {
        "name": "...",
        "description": "...",
        "price": 100.0,
        "stock": 50,
        "category": "..."
    }
    Returns: {
        "data": {...}
    }
    """
    try:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFoundError(f"Product {product_id} not found")
        
        data = request.validated_data
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data.get('description', '')
        if 'price' in data:
            product.price = float(data['price'])
        if 'stock' in data:
            product.stock_quantity = int(data['stock'])
        if 'category' in data:
            product.category = data.get('category', '')
        
        product.save()
        
        product_data = {
            'id': str(product.id),
            'name': product.name,
            'description': product.description or '',
            'price': product.price,
            'stock': product.stock_quantity,
            'category': product.category or '',
            'imageUrl': None,
            'createdAt': product.created_at.isoformat() if product.created_at else datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat(),
            'synced': True
        }
        
        logger.info(f"Updated product {product_id}")
        return jsonify({
            'data': product_data,
            'success': True
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}", exc_info=True)
        raise ValidationError(f"Failed to update product: {str(e)}")


@products_bp.route('/<product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    """
    Delete a product
    
    Returns: {
        "success": true
    }
    """
    try:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFoundError(f"Product {product_id} not found")
        
        product.delete()
        
        logger.info(f"Deleted product {product_id}")
        return jsonify({
            'success': True
        }), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}", exc_info=True)
        raise ValidationError(f"Failed to delete product: {str(e)}")

