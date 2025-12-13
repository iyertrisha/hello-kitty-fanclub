"""
Admin routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from services.admin import (
    get_overview_stats,
    get_all_stores,
    get_analytics_data,
    get_blockchain_logs
)
from services.cooperative import create_cooperative
from api.middleware.validation import validate_request, validate_query_params
from api.middleware.error_handler import ValidationError
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/overview', methods=['GET'])
def get_overview_route():
    """Get overview statistics"""
    try:
        stats = get_overview_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}", exc_info=True)
        raise ValidationError(f"Failed to get overview stats: {str(e)}")


@admin_bp.route('/stores', methods=['GET'])
@validate_query_params(param_types={'page': int, 'page_size': int})
def get_stores_route():
    """Get all stores with filters"""
    try:
        filters = {}
        if 'search' in request.args:
            filters['search'] = request.args.get('search')
        if 'status' in request.args:
            filters['status'] = request.args.get('status')
        
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        
        stores, total_count, page, page_size = get_all_stores(filters, page, page_size)
        
        return jsonify({
            'stores': stores,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting stores: {e}", exc_info=True)
        raise ValidationError(f"Failed to get stores: {str(e)}")


@admin_bp.route('/cooperatives', methods=['GET'])
def get_cooperatives_admin_route():
    """Get all cooperatives"""
    try:
        from services.cooperative import get_cooperatives
        cooperatives = get_cooperatives()
        logger.info(f"Returning {len(cooperatives)} cooperatives to frontend")
        return jsonify({'cooperatives': cooperatives}), 200
    except Exception as e:
        logger.error(f"Error getting cooperatives: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperatives: {str(e)}")


@admin_bp.route('/cooperatives', methods=['POST'])
@validate_request(required_fields=['name', 'revenue_split_percent'])
def create_cooperative_admin_route():
    """Create cooperative"""
    try:
        data = request.validated_data
        cooperative = create_cooperative(data)
        
        return jsonify({
            'id': str(cooperative.id),
            'name': cooperative.name,
            'revenue_split_percent': cooperative.revenue_split_percent
        }), 201
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating cooperative: {e}", exc_info=True)
        raise ValidationError(f"Failed to create cooperative: {str(e)}")


@admin_bp.route('/analytics', methods=['GET'])
def get_analytics_route():
    """Get analytics data"""
    try:
        date_range = None
        if 'start' in request.args and 'end' in request.args:
            date_range = {
                'start': datetime.fromisoformat(request.args.get('start')),
                'end': datetime.fromisoformat(request.args.get('end'))
            }
        
        analytics_data = get_analytics_data(date_range)
        return jsonify(analytics_data), 200
    except Exception as e:
        logger.error(f"Error getting analytics: {e}", exc_info=True)
        raise ValidationError(f"Failed to get analytics: {str(e)}")


@admin_bp.route('/blockchain-logs', methods=['GET'])
@validate_query_params(param_types={'page': int, 'page_size': int})
def get_blockchain_logs_route():
    """Get blockchain transaction logs"""
    try:
        filters = {}
        if 'shopkeeper_id' in request.args:
            filters['shopkeeper_id'] = request.args.get('shopkeeper_id')
        if 'date_from' in request.args:
            filters['date_from'] = datetime.fromisoformat(request.args.get('date_from'))
        if 'date_to' in request.args:
            filters['date_to'] = datetime.fromisoformat(request.args.get('date_to'))
        
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        
        logs, total_count, page, page_size = get_blockchain_logs(filters, page, page_size)
        
        return jsonify({
            'logs': logs,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting blockchain logs: {e}", exc_info=True)
        raise ValidationError(f"Failed to get blockchain logs: {str(e)}")


@admin_bp.route('/stores/<store_id>/flag', methods=['POST'])
@validate_request(required_fields=['reason'])
def flag_store_route(store_id):
    """Flag a store for review (Platform Admin only)"""
    try:
        from database.models import Shopkeeper
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(store_id)
        except InvalidId:
            raise ValidationError(f"Invalid store ID format: {store_id}")
        
        shopkeeper = Shopkeeper.objects.get(id=store_id)
        data = request.validated_data
        
        shopkeeper.flagged = True
        shopkeeper.flag_reason = data.get('reason', '')
        shopkeeper.flagged_at = datetime.utcnow()
        shopkeeper.save()
        
        logger.info(f"Store {store_id} flagged by admin: {data.get('reason')}")
        
        return jsonify({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'flagged': shopkeeper.flagged,
            'flag_reason': shopkeeper.flag_reason,
            'message': f'Store {shopkeeper.name} flagged for review'
        }), 200
    except Shopkeeper.DoesNotExist:
        raise ValidationError(f"Store {store_id} not found")
    except Exception as e:
        logger.error(f"Error flagging store: {e}", exc_info=True)
        raise ValidationError(f"Failed to flag store: {str(e)}")


@admin_bp.route('/stores/<store_id>/flag', methods=['DELETE'])
def unflag_store_route(store_id):
    """Remove flag from a store"""
    try:
        from database.models import Shopkeeper
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(store_id)
        except InvalidId:
            raise ValidationError(f"Invalid store ID format: {store_id}")
        
        shopkeeper = Shopkeeper.objects.get(id=store_id)
        
        shopkeeper.flagged = False
        shopkeeper.flag_reason = None
        shopkeeper.flagged_at = None
        shopkeeper.save()
        
        logger.info(f"Flag removed from store {store_id}")
        
        return jsonify({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'flagged': shopkeeper.flagged,
            'message': f'Flag removed from store {shopkeeper.name}'
        }), 200
    except Shopkeeper.DoesNotExist:
        raise ValidationError(f"Store {store_id} not found")
    except Exception as e:
        logger.error(f"Error unflagging store: {e}", exc_info=True)
        raise ValidationError(f"Failed to unflag store: {str(e)}")


@admin_bp.route('/credit-scores', methods=['GET'])
def get_all_credit_scores_route():
    """Get all shopkeeper credit scores (Platform Admin)"""
    try:
        from database.models import Shopkeeper
        
        shopkeepers = Shopkeeper.objects(is_active=True).only('id', 'name', 'credit_score', 'wallet_address')
        
        scores = []
        for shopkeeper in shopkeepers:
            scores.append({
                'shopkeeper_id': str(shopkeeper.id),
                'shopkeeper_name': shopkeeper.name,
                'credit_score': shopkeeper.credit_score,
                'wallet_address': shopkeeper.wallet_address
            })
        
        # Sort by credit score descending
        scores.sort(key=lambda x: x['credit_score'], reverse=True)
        
        return jsonify({
            'scores': scores,
            'total': len(scores)
        }), 200
    except Exception as e:
        logger.error(f"Error getting credit scores: {e}", exc_info=True)
        raise ValidationError(f"Failed to get credit scores: {str(e)}")


# ========== Inventory Seeding ==========

@admin_bp.route('/inventory/seed', methods=['POST'])
@validate_request(required_fields=['products'])
def seed_inventory_route():
    """Seed products from supplier catalog (shared inventory)"""
    try:
        data = request.validated_data
        products_data = data['products']
        
        if not isinstance(products_data, list):
            raise ValidationError("products must be a list")
        
        from database.models import Product, Shopkeeper
        
        # Optional: shopkeeper_id to seed products for specific shopkeeper
        # If not provided, products are seeded for all shopkeepers or as template
        shopkeeper_id = data.get('shopkeeper_id')
        
        seeded_products = []
        errors = []
        
        for product_data in products_data:
            try:
                # Validate required fields
                if 'name' not in product_data or 'price' not in product_data:
                    errors.append(f"Product missing required fields: {product_data.get('name', 'Unknown')}")
                    continue
                
                if shopkeeper_id:
                    # Seed for specific shopkeeper
                    try:
                        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
                        
                        # Check if product already exists
                        existing = Product.objects(
                            shopkeeper_id=shopkeeper_id,
                            name=product_data['name']
                        ).first()
                        
                        if existing:
                            # Update existing product
                            existing.price = product_data['price']
                            existing.category = product_data.get('category', existing.category or 'General')
                            existing.stock_quantity = product_data.get('stock_quantity', existing.stock_quantity)
                            existing.description = product_data.get('description', existing.description)
                            existing.save()
                            seeded_products.append({
                                'id': str(existing.id),
                                'name': existing.name,
                                'action': 'updated'
                            })
                        else:
                            # Create new product
                            product = Product(
                                name=product_data['name'],
                                category=product_data.get('category', 'General'),
                                price=product_data['price'],
                                stock_quantity=product_data.get('stock_quantity', 0),
                                description=product_data.get('description', ''),
                                shopkeeper_id=shopkeeper_id
                            )
                            product.save()
                            seeded_products.append({
                                'id': str(product.id),
                                'name': product.name,
                                'action': 'created'
                            })
                    except Shopkeeper.DoesNotExist:
                        errors.append(f"Shopkeeper {shopkeeper_id} not found")
                else:
                    # Seed as template products (no shopkeeper association)
                    # This would require a ProductTemplate model or similar
                    # For now, skip if no shopkeeper_id
                    errors.append("shopkeeper_id required for seeding")
                    continue
            except Exception as e:
                errors.append(f"Error seeding product {product_data.get('name', 'Unknown')}: {str(e)}")
        
        return jsonify({
            'success': True,
            'seeded_count': len(seeded_products),
            'products': seeded_products,
            'errors': errors,
            'message': f'Successfully seeded {len(seeded_products)} products'
        }), 201
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error seeding inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to seed inventory: {str(e)}")
