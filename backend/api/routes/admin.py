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

