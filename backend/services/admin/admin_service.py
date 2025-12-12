"""
Admin service - Business logic for admin operations
"""
from datetime import datetime, timedelta
from database.models import Shopkeeper, Transaction, Cooperative, Customer
from api.middleware.error_handler import ValidationError
import logging

logger = logging.getLogger(__name__)


def get_overview_stats():
    """
    Calculate overview statistics
    
    Returns:
        dict: Overview statistics matching frontend expectations
    """
    # Total stores
    total_stores = Shopkeeper.objects(is_active=True).count()
    
    # Total customers
    total_customers = Customer.objects.count()
    
    # Total cooperatives
    total_cooperatives = Cooperative.objects(is_active=True).count()
    
    # Today's transactions
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_transactions = Transaction.objects(timestamp__gte=today_start).count()
    today_revenue = sum(t.amount for t in Transaction.objects(timestamp__gte=today_start, type='sale'))
    
    # This week's transactions
    week_start = today_start - timedelta(days=today_start.weekday())
    week_transactions = Transaction.objects(timestamp__gte=week_start).count()
    week_revenue = sum(t.amount for t in Transaction.objects(timestamp__gte=week_start, type='sale'))
    
    # This month's transactions
    month_start = today_start.replace(day=1)
    month_transactions = Transaction.objects(timestamp__gte=month_start).count()
    month_revenue = sum(t.amount for t in Transaction.objects(timestamp__gte=month_start, type='sale'))
    
    # Active cooperatives
    active_cooperatives = Cooperative.objects(is_active=True, members__exists=True).count()
    
    # Sales trend (last 30 days) for chart
    sales_trend = []
    for i in range(30):
        day_start = today_start - timedelta(days=29-i)
        day_end = day_start + timedelta(days=1)
        day_sales = sum(
            t.amount for t in Transaction.objects(
                type='sale',
                timestamp__gte=day_start,
                timestamp__lt=day_end
            )
        )
        sales_trend.append({
            'date': day_start.isoformat(),
            'amount': day_sales
        })
    
    # Recent activity (last 10 transactions)
    recent_transactions = Transaction.objects().order_by('-timestamp').limit(10)
    recent_activity = []
    for tx in recent_transactions:
        activity_type = 'transaction'
        message = f"{tx.type.capitalize()} transaction of Rs. {tx.amount:.2f}"
        recent_activity.append({
            'type': activity_type,
            'message': message,
            'timestamp': tx.timestamp.isoformat() if tx.timestamp else None
        })
    
    # Return in format expected by frontend
    return {
        # Frontend expected format
        'total_stores': total_stores,
        'transactions': {
            'today': today_transactions,
            'week': week_transactions,
            'month': month_transactions
        },
        'revenue': {
            'today': today_revenue,
            'week': week_revenue,
            'month': month_revenue
        },
        'active_cooperatives': active_cooperatives,
        'sales_trend': sales_trend,
        'recent_activity': recent_activity,
        # Additional data (backwards compatible)
        'stores': {
            'total': total_stores,
            'active': total_stores
        },
        'customers': {
            'total': total_customers
        },
        'cooperatives': {
            'total': total_cooperatives,
            'active': active_cooperatives
        }
    }


def get_all_stores(filters=None, page=1, page_size=20):
    """
    Get all stores with pagination
    
    Args:
        filters: Dictionary of filters (search, status)
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        tuple: (stores list, total count, page, page_size)
    """
    if filters is None:
        filters = {}
    
    query = Shopkeeper.objects()
    
    # Apply filters
    if 'search' in filters and filters['search']:
        search_term = filters['search']
        query = query.filter(
            __raw__={
                '$or': [
                    {'name': {'$regex': search_term, '$options': 'i'}},
                    {'address': {'$regex': search_term, '$options': 'i'}},
                    {'phone': {'$regex': search_term, '$options': 'i'}}
                ]
            }
        )
    
    if 'status' in filters:
        if filters['status'] == 'active':
            query = query.filter(is_active=True)
        elif filters['status'] == 'inactive':
            query = query.filter(is_active=False)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    stores = query.skip(skip).limit(page_size)
    
    result = []
    for store in stores:
        # Calculate stats
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sales = sum(
            t.amount for t in Transaction.objects(
                shopkeeper_id=store.id,
                type='sale',
                timestamp__gte=thirty_days_ago
            )
        )
        
        result.append({
            'id': str(store.id),
            'name': store.name,
            'address': store.address,
            'phone': store.phone,
            'email': store.email,
            'wallet_address': store.wallet_address,
            'credit_score': store.credit_score,
            'is_active': store.is_active,
            'total_sales_30d': recent_sales,
            'registered_at': store.registered_at.isoformat() if store.registered_at else None
        })
    
    return result, total_count, page, page_size


def get_analytics_data(date_range=None):
    """
    Get analytics data for charts
    
    Args:
        date_range: Dict with 'start' and 'end' datetime objects
    
    Returns:
        dict: Analytics data
    """
    if date_range is None:
        date_range = {
            'start': datetime.utcnow() - timedelta(days=30),
            'end': datetime.utcnow()
        }
    
    start_date = date_range['start']
    end_date = date_range['end']
    
    # Sales trends (daily)
    sales_trend = []
    current_date = start_date
    while current_date <= end_date:
        day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_sales = sum(
            t.amount for t in Transaction.objects(
                type='sale',
                timestamp__gte=day_start,
                timestamp__lt=day_end
            )
        )
        
        sales_trend.append({
            'date': day_start.isoformat(),
            'amount': day_sales
        })
        
        current_date += timedelta(days=1)
    
    # Credit score distribution
    shopkeepers = Shopkeeper.objects(is_active=True)
    credit_scores = []
    for shopkeeper in shopkeepers:
        credit_scores.append({
            'shopkeeper_id': str(shopkeeper.id),
            'shopkeeper_name': shopkeeper.name,
            'score': shopkeeper.credit_score
        })
    
    # Revenue by cooperative
    cooperatives = Cooperative.objects(is_active=True)
    revenue_by_coop = []
    for coop in cooperatives:
        # Calculate revenue from transactions by cooperative members
        coop_revenue = 0
        for member in coop.members:
            member_transactions = Transaction.objects(
                shopkeeper_id=member.id,
                type='sale',
                timestamp__gte=start_date,
                timestamp__lte=end_date
            )
            coop_revenue += sum(t.amount for t in member_transactions)
        
        revenue_by_coop.append({
            'coop_id': str(coop.id),
            'coop_name': coop.name,
            'revenue': coop_revenue
        })
    
    return {
        'sales_trend': sales_trend,
        'credit_scores': credit_scores,
        'revenue_by_coop': revenue_by_coop
    }


def get_blockchain_logs(filters=None, page=1, page_size=20):
    """
    Get blockchain transaction logs
    
    Shows all verified transactions. Those with blockchain_tx_id are marked as 
    blockchain-verified, others show their verification status.
    
    Args:
        filters: Dictionary of filters (shopkeeper_id, date_from, date_to)
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        tuple: (transactions list, total count, page, page_size)
    """
    if filters is None:
        filters = {}
    
    # Show all verified transactions (not just those with blockchain_tx_id)
    # This provides visibility into transactions even before blockchain recording
    query = Transaction.objects(status__in=['verified', 'completed'])
    
    # Apply filters
    if 'shopkeeper_id' in filters:
        query = query.filter(shopkeeper_id=filters['shopkeeper_id'])
    
    if 'date_from' in filters:
        query = query.filter(timestamp__gte=filters['date_from'])
    
    if 'date_to' in filters:
        query = query.filter(timestamp__lte=filters['date_to'])
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    transactions = query.order_by('-timestamp').skip(skip).limit(page_size)
    
    result = []
    for transaction in transactions:
        # Determine blockchain status
        has_blockchain = bool(transaction.blockchain_tx_id)
        blockchain_status = 'verified' if has_blockchain else 'pending_blockchain'
        
        result.append({
            'id': str(transaction.id),
            'type': transaction.type,
            'amount': transaction.amount,
            'shopkeeper_id': str(transaction.shopkeeper_id.id),
            'shopkeeper_name': transaction.shopkeeper_id.name if transaction.shopkeeper_id else 'Unknown',
            'customer_id': str(transaction.customer_id.id),
            'customer_name': transaction.customer_id.name if transaction.customer_id else 'Unknown',
            'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,
            # Frontend expects 'transaction_hash', backend has 'blockchain_tx_id'
            'transaction_hash': transaction.blockchain_tx_id or f"pending-{str(transaction.id)[-8:]}",
            'blockchain_tx_id': transaction.blockchain_tx_id,
            'block_number': transaction.blockchain_block_number,
            'blockchain_block_number': transaction.blockchain_block_number,
            'status': blockchain_status if has_blockchain else transaction.status,
            'db_status': transaction.status,
            'transcript_hash': transaction.transcript_hash,
            'has_blockchain_record': has_blockchain
        })
    
    return result, total_count, page, page_size

