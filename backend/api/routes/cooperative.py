"""
Cooperative routes
"""
from flask import Blueprint, request, jsonify
from services.cooperative import (
    get_cooperatives,
    create_cooperative,
    join_cooperative,
    get_cooperative_members,
    create_bulk_order,
    delete_cooperative,
    update_cooperative
)
from database.models import BulkOrder
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

cooperative_bp = Blueprint('cooperative', __name__)


@cooperative_bp.route('', methods=['GET'])
def get_cooperatives_route():
    """List all cooperatives"""
    try:
        cooperatives = get_cooperatives()
        return jsonify({'cooperatives': cooperatives}), 200
    except Exception as e:
        logger.error(f"Error getting cooperatives: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperatives: {str(e)}")


@cooperative_bp.route('/<coop_id>', methods=['GET'])
def get_cooperative_route(coop_id):
    """Get cooperative details"""
    try:
        cooperatives = get_cooperatives()
        cooperative = next((c for c in cooperatives if c['id'] == coop_id), None)
        
        if not cooperative:
            raise NotFoundError(f"Cooperative {coop_id} not found")
        
        return jsonify(cooperative), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting cooperative: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperative: {str(e)}")


@cooperative_bp.route('/<coop_id>', methods=['PUT'])
@validate_request()
def update_cooperative_route(coop_id):
    """Update cooperative"""
    try:
        # Validate ObjectId format
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        data = request.validated_data
        cooperative = update_cooperative(coop_id, data)
        
        return jsonify({
            'success': True,
            'id': str(cooperative.id),
            'name': cooperative.name,
            'revenue_split_percent': cooperative.revenue_split_percent
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating cooperative: {e}", exc_info=True)
        raise ValidationError(f"Failed to update cooperative: {str(e)}")


@cooperative_bp.route('/<coop_id>', methods=['DELETE'])
def delete_cooperative_route(coop_id):
    """Delete cooperative"""
    try:
        # Validate ObjectId format
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        delete_cooperative(coop_id)
        return jsonify({'success': True, 'message': 'Cooperative deleted successfully'}), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error deleting cooperative: {e}", exc_info=True)
        raise ValidationError(f"Failed to delete cooperative: {str(e)}")


@cooperative_bp.route('/<coop_id>/join', methods=['POST'])
@validate_request(required_fields=['shopkeeper_id'])
def join_cooperative_route(coop_id):
    """Join cooperative"""
    try:
        # Validate ObjectId formats
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        data = request.validated_data
        shopkeeper_id = data['shopkeeper_id']
        
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        cooperative = join_cooperative(coop_id, shopkeeper_id)
        
        return jsonify({
            'cooperative_id': str(cooperative.id),
            'member_count': len(cooperative.members),
            'success': True
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error joining cooperative: {e}", exc_info=True)
        raise ValidationError(f"Failed to join cooperative: {str(e)}")


@cooperative_bp.route('/<coop_id>/members', methods=['GET'])
def get_cooperative_members_route(coop_id):
    """Get cooperative members"""
    try:
        members = get_cooperative_members(coop_id)
        return jsonify({'members': members}), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting cooperative members: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperative members: {str(e)}")


@cooperative_bp.route('/<coop_id>/bulk-order', methods=['POST'])
@validate_request(required_fields=['product_name', 'quantity', 'unit_price'])
def create_bulk_order_route(coop_id):
    """Create bulk order"""
    try:
        data = request.validated_data
        bulk_order = create_bulk_order(coop_id, data)
        
        return jsonify({
            'id': str(bulk_order.id),
            'product_name': bulk_order.product_name,
            'quantity': bulk_order.quantity,
            'total_amount': bulk_order.total_amount,
            'status': bulk_order.status
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk order: {e}", exc_info=True)
        raise ValidationError(f"Failed to create bulk order: {str(e)}")


@cooperative_bp.route('/<coop_id>/orders', methods=['GET'])
def get_bulk_orders_route(coop_id):
    """Get bulk order history"""
    try:
        orders = BulkOrder.objects(cooperative_id=coop_id).order_by('-created_at')
        
        result = []
        for order in orders:
            result.append({
                'id': str(order.id),
                'product_name': order.product_name,
                'quantity': order.quantity,
                'unit_price': order.unit_price,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None
            })
        
        return jsonify({'orders': result}), 200
    except Exception as e:
        logger.error(f"Error getting bulk orders: {e}", exc_info=True)
        raise ValidationError(f"Failed to get bulk orders: {str(e)}")

