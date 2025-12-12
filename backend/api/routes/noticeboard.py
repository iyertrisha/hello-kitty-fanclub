"""
Noticeboard routes - API endpoints for noticeboard
"""
from flask import Blueprint, request, jsonify
from services.noticeboard import (
    get_active_notices,
    create_notice,
    format_notices_for_display
)
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)

noticeboard_bp = Blueprint('noticeboard', __name__)


@noticeboard_bp.route('', methods=['GET'])
def get_notices_route():
    """
    Get active notices
    
    Query params: shopkeeper_id (optional)
    Returns: {
        "notices": [...]
    }
    """
    try:
        shopkeeper_id = request.args.get('shopkeeper_id')
        
        notices = get_active_notices(shopkeeper_id=shopkeeper_id)
        formatted_notices = format_notices_for_display(notices)
        
        return jsonify({
            'notices': formatted_notices
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting notices: {e}", exc_info=True)
        raise ValidationError(f"Failed to get notices: {str(e)}")


@noticeboard_bp.route('', methods=['POST'])
@validate_request(required_fields=['title', 'message', 'shopkeeper_id'])
def create_notice_route():
    """
    Create a new notice (shopkeeper only)
    
    Accepts: {
        "title": str,
        "message": str,
        "shopkeeper_id": str,
        "priority": str (optional, default: "normal"),
        "expires_at": str (optional, ISO datetime)
    }
    Returns: {
        "notice_id": str
    }
    """
    try:
        data = request.validated_data
        title = data['title']
        message = data['message']
        shopkeeper_id = data['shopkeeper_id']
        priority = data.get('priority', 'normal')
        expires_at = data.get('expires_at')
        
        # Parse expires_at if provided
        expires_at_dt = None
        if expires_at:
            from datetime import datetime
            try:
                expires_at_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Invalid expires_at format. Use ISO datetime format.")
        
        notice = create_notice(
            shopkeeper_id=shopkeeper_id,
            title=title,
            message=message,
            priority=priority,
            expires_at=expires_at_dt
        )
        
        return jsonify({
            'notice_id': str(notice.id),
            'success': True
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating notice: {e}", exc_info=True)
        raise ValidationError(f"Failed to create notice: {str(e)}")

