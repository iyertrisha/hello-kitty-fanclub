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


@cooperative_bp.route('/<coop_id>/overview', methods=['GET'])
def get_cooperative_overview_route(coop_id):
    """Get cooperative overview statistics"""
    try:
        from database.models import Cooperative, Transaction
        from datetime import datetime, timedelta
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        cooperative = Cooperative.objects.get(id=coop_id)
        
        # Calculate revenue for today, week, month
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        
        # Get transactions from cooperative members
        member_ids = [str(m.id) for m in cooperative.members]
        today_revenue = sum(
            t.amount for t in Transaction.objects(
                shopkeeper_id__in=member_ids,
                type='sale',
                timestamp__gte=today_start
            )
        )
        week_revenue = sum(
            t.amount for t in Transaction.objects(
                shopkeeper_id__in=member_ids,
                type='sale',
                timestamp__gte=week_start
            )
        )
        month_revenue = sum(
            t.amount for t in Transaction.objects(
                shopkeeper_id__in=member_ids,
                type='sale',
                timestamp__gte=month_start
            )
        )
        
        # Get active orders
        active_orders = BulkOrder.objects(cooperative_id=coop_id, status__in=['pending', 'processing']).count()
        
        # Calculate sales growth (compare this month to last month)
        last_month_start = (month_start - timedelta(days=1)).replace(day=1)
        last_month_revenue = sum(
            t.amount for t in Transaction.objects(
                shopkeeper_id__in=member_ids,
                type='sale',
                timestamp__gte=last_month_start,
                timestamp__lt=month_start
            )
        )
        sales_growth = ((month_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
        
        # Order volume (last 30 days)
        thirty_days_ago = today_start - timedelta(days=30)
        order_volume = Transaction.objects(
            shopkeeper_id__in=member_ids,
            type='sale',
            timestamp__gte=thirty_days_ago
        ).count()
        
        # Average order value
        recent_transactions = Transaction.objects(
            shopkeeper_id__in=member_ids,
            type='sale',
            timestamp__gte=thirty_days_ago
        )
        avg_order_value = sum(t.amount for t in recent_transactions) / order_volume if order_volume > 0 else 0
        
        return jsonify({
            'name': cooperative.name,
            'member_count': len(cooperative.members),
            'revenue': {
                'today': today_revenue,
                'week': week_revenue,
                'month': month_revenue
            },
            'active_orders': active_orders,
            'sales_growth': round(sales_growth, 2),
            'order_volume': order_volume,
            'avg_order_value': round(avg_order_value, 2),
            'recent_activity': []
        }), 200
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    except Exception as e:
        logger.error(f"Error getting cooperative overview: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperative overview: {str(e)}")


@cooperative_bp.route('/<coop_id>/member-scores', methods=['GET'])
def get_cooperative_member_scores_route(coop_id):
    """Get credit scores for all cooperative members"""
    try:
        from database.models import Cooperative
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        cooperative = Cooperative.objects.get(id=coop_id)
        
        scores = []
        for member in cooperative.members:
            scores.append({
                'id': str(member.id),
                'name': member.name,
                'credit_score': member.credit_score
            })
        
        # Sort by credit score descending
        scores.sort(key=lambda x: x['credit_score'], reverse=True)
        
        return jsonify({'scores': scores}), 200
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    except Exception as e:
        logger.error(f"Error getting member scores: {e}", exc_info=True)
        raise ValidationError(f"Failed to get member scores: {str(e)}")


@cooperative_bp.route('/<coop_id>/map-data', methods=['GET'])
def get_cooperative_map_data_route(coop_id):
    """Get geographic map data for cooperative members"""
    try:
        from database.models import Cooperative
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        cooperative = Cooperative.objects.get(id=coop_id)
        
        members_data = []
        for member in cooperative.members:
            if member.location:
                members_data.append({
                    'id': str(member.id),
                    'name': member.name,
                    'latitude': member.location.latitude,
                    'longitude': member.location.longitude,
                    'address': member.location.address or member.address,
                    'credit_score': member.credit_score
                })
        
        # Calculate center point (average of all member locations)
        if members_data:
            center_lat = sum(m['latitude'] for m in members_data) / len(members_data)
            center_lng = sum(m['longitude'] for m in members_data) / len(members_data)
        else:
            center_lat = 0
            center_lng = 0
        
        return jsonify({
            'cooperative_id': str(cooperative.id),
            'cooperative_name': cooperative.name,
            'center': {
                'latitude': center_lat,
                'longitude': center_lng
            },
            'members': members_data
        }), 200
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    except Exception as e:
        logger.error(f"Error getting map data: {e}", exc_info=True)
        raise ValidationError(f"Failed to get map data: {str(e)}")


@cooperative_bp.route('/<coop_id>/blockchain-logs', methods=['GET'])
def get_cooperative_blockchain_logs_route(coop_id):
    """Get blockchain logs for cooperative transactions"""
    try:
        from database.models import Cooperative, Transaction
        from datetime import datetime
        from services.admin import get_blockchain_logs
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(coop_id)
        except InvalidId:
            raise ValidationError(f"Invalid cooperative ID format: {coop_id}")
        
        cooperative = Cooperative.objects.get(id=coop_id)
        
        # Get member IDs
        member_ids = [str(m.id) for m in cooperative.members]
        
        # Build filters
        filters = {}
        if 'date_from' in request.args:
            filters['date_from'] = datetime.fromisoformat(request.args.get('date_from'))
        if 'date_to' in request.args:
            filters['date_to'] = datetime.fromisoformat(request.args.get('date_to'))
        
        # Get all blockchain logs
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        
        logs, total_count, page, page_size = get_blockchain_logs(filters, page, page_size)
        
        # Filter to only cooperative members
        cooperative_logs = [log for log in logs if log['shopkeeper_id'] in member_ids]
        
        return jsonify({
            'logs': cooperative_logs,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': len(cooperative_logs),
                'total_pages': (len(cooperative_logs) + page_size - 1) // page_size
            }
        }), 200
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    except Exception as e:
        logger.error(f"Error getting cooperative blockchain logs: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperative blockchain logs: {str(e)}")


@cooperative_bp.route('/<coop_id>/orders/<order_id>/status', methods=['PUT'])
@validate_request(required_fields=['status'])
def update_order_status_route(coop_id, order_id):
    """Update bulk order status"""
    try:
        from database.models import BulkOrder
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(coop_id)
            ObjectId(order_id)
        except InvalidId:
            raise ValidationError(f"Invalid ID format")
        
        order = BulkOrder.objects.get(id=order_id, cooperative_id=coop_id)
        data = request.validated_data
        
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        order.status = data['status']
        order.save()
        
        return jsonify({
            'id': str(order.id),
            'status': order.status,
            'message': f'Order status updated to {order.status}'
        }), 200
    except BulkOrder.DoesNotExist:
        raise NotFoundError(f"Order {order_id} not found in cooperative {coop_id}")
    except Exception as e:
        logger.error(f"Error updating order status: {e}", exc_info=True)
        raise ValidationError(f"Failed to update order status: {str(e)}")


@cooperative_bp.route('/<coop_id>/members/<shopkeeper_id>', methods=['DELETE'])
def remove_cooperative_member_route(coop_id, shopkeeper_id):
    """Remove a member from cooperative"""
    try:
        from database.models import Cooperative, Shopkeeper
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(coop_id)
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid ID format")
        
        cooperative = Cooperative.objects.get(id=coop_id)
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        
        # Check if shopkeeper is a member
        if shopkeeper not in cooperative.members:
            raise ValidationError(f"Shopkeeper {shopkeeper_id} is not a member of cooperative {coop_id}")
        
        # Remove member
        cooperative.members.remove(shopkeeper)
        cooperative.save()
        
        logger.info(f"Removed shopkeeper {shopkeeper_id} from cooperative {coop_id}")
        
        return jsonify({
            'success': True,
            'message': f'Shopkeeper {shopkeeper.name} removed from cooperative',
            'member_count': len(cooperative.members)
        }), 200
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    except Exception as e:
        logger.error(f"Error removing cooperative member: {e}", exc_info=True)
        raise ValidationError(f"Failed to remove cooperative member: {str(e)}")

