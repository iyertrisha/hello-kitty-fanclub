"""
Health check and connection test endpoint
"""
from flask import Blueprint, jsonify
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running'
    }), 200


@health_bp.route('/test', methods=['GET'])
def test_connection():
    """Test connection endpoint for Flutter app"""
    return jsonify({
        'success': True,
        'message': 'Backend connection successful',
        'timestamp': '2024-01-01T00:00:00Z'  # You can use datetime.utcnow().isoformat() if needed
    }), 200

