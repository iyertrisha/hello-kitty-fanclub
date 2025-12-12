"""
Noticeboard service - Core business logic for noticeboard
"""
from datetime import datetime
from database.models import Notice, Shopkeeper
from api.middleware.error_handler import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


def get_active_notices(shopkeeper_id=None):
    """
    Get active notices
    
    Args:
        shopkeeper_id: Shopkeeper ID (optional, if None returns all active notices)
        
    Returns:
        list: Notice objects sorted by priority and date
    """
    query = Notice.objects(is_active=True)
    
    # Filter by expiration
    now = datetime.utcnow()
    query = query.filter(
        __raw__={
            '$or': [
                {'expires_at': {'$exists': False}},
                {'expires_at': None},
                {'expires_at': {'$gte': now}}
            ]
        }
    )
    
    if shopkeeper_id:
        try:
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            query = query.filter(shopkeeper_id=shopkeeper)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Sort by priority (urgent first) and then by date (newest first)
    priority_order = {'urgent': 0, 'high': 1, 'normal': 2, 'low': 3}
    notices = list(query)
    
    # Sort notices
    notices.sort(key=lambda n: (
        priority_order.get(n.priority, 2),
        -n.created_at.timestamp()  # Negative for descending (newest first)
    ))
    
    return notices


def create_notice(shopkeeper_id, title, message, priority='normal', expires_at=None):
    """
    Create a new notice
    
    Args:
        shopkeeper_id: Shopkeeper ID
        title: Notice title
        message: Notice message
        priority: Priority level (low, normal, high, urgent)
        expires_at: Optional expiration datetime
        
    Returns:
        Notice: Created notice object
    """
    # Validate inputs
    if not title or len(title.strip()) == 0:
        raise ValidationError("Title is required")
    
    if not message or len(message.strip()) == 0:
        raise ValidationError("Message is required")
    
    if len(title) > 200:
        raise ValidationError("Title must be 200 characters or less")
    
    if len(message) > 1000:
        raise ValidationError("Message must be 1000 characters or less")
    
    if priority not in ('low', 'normal', 'high', 'urgent'):
        raise ValidationError("Priority must be one of: low, normal, high, urgent")
    
    # Get shopkeeper
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Create notice
    notice = Notice(
        title=title.strip(),
        message=message.strip(),
        shopkeeper_id=shopkeeper,
        priority=priority,
        is_active=True,
        expires_at=expires_at
    )
    
    notice.save()
    
    logger.info(f"Created notice '{title}' for shopkeeper {shopkeeper_id}")
    
    return notice


def format_notices_for_display(notices):
    """
    Format notices for WhatsApp display
    
    Args:
        notices: List of Notice objects
        
    Returns:
        list: Formatted notice dictionaries
    """
    formatted = []
    
    for notice in notices:
        formatted.append({
            'id': str(notice.id),
            'title': notice.title,
            'message': notice.message,
            'priority': notice.priority,
            'created_at': notice.created_at.isoformat() if notice.created_at else None,
            'expires_at': notice.expires_at.isoformat() if notice.expires_at else None
        })
    
    return formatted

