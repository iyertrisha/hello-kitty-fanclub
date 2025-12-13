"""
Analytics service for suppliers
"""
from database.models import Supplier, SupplierOrder, Shopkeeper
from api.middleware.error_handler import NotFoundError
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def get_analytics_overview(supplier_id):
    """
    Get overview statistics for supplier
    
    Args:
        supplier_id: Supplier ID
    
    Returns:
        dict: Overview statistics
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    # Get stores in service area
    stores = _get_stores_in_service_area(supplier)
    total_stores = len(stores)
    
    # Get all orders for supplier
    orders = SupplierOrder.objects(supplier_id=supplier_id)
    total_orders = orders.count()
    
    # Calculate order statistics
    pending_orders = orders.filter(status='pending').count()
    confirmed_orders = orders.filter(status='confirmed').count()
    dispatched_orders = orders.filter(status='dispatched').count()
    completed_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()
    
    # Calculate revenue
    completed_order_objects = orders.filter(status='delivered')
    total_revenue = sum(order.total_amount for order in completed_order_objects)
    
    # Calculate average order value
    avg_order_value = total_revenue / completed_orders if completed_orders > 0 else 0
    
    # Order status distribution
    status_distribution = {
        'pending': pending_orders,
        'confirmed': confirmed_orders,
        'dispatched': dispatched_orders,
        'delivered': completed_orders,
        'cancelled': cancelled_orders
    }
    
    return {
        'total_stores': total_stores,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
        'order_status_distribution': status_distribution
    }


def get_analytics_orders(supplier_id, days=30):
    """
    Get order analytics data over time
    
    Args:
        supplier_id: Supplier ID
        days: Number of days to look back
    
    Returns:
        dict: Order analytics data
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get orders in date range
    orders = SupplierOrder.objects(
        supplier_id=supplier_id,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('created_at')
    
    # Group by date
    orders_by_date = defaultdict(lambda: {'count': 0, 'total_value': 0})
    
    for order in orders:
        date_key = order.created_at.date().isoformat()
        orders_by_date[date_key]['count'] += 1
        orders_by_date[date_key]['total_value'] += order.total_amount
    
    # Convert to list format
    orders_over_time = []
    for date_str in sorted(orders_by_date.keys()):
        orders_over_time.append({
            'date': date_str,
            'count': orders_by_date[date_str]['count'],
            'total_value': orders_by_date[date_str]['total_value']
        })
    
    return {
        'orders_over_time': orders_over_time,
        'days': days
    }


def get_analytics_stores(supplier_id):
    """
    Get store analytics data
    
    Args:
        supplier_id: Supplier ID
    
    Returns:
        dict: Store analytics data
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    # Get stores in service area
    stores = _get_stores_in_service_area(supplier)
    
    # Get all orders for supplier
    orders = SupplierOrder.objects(supplier_id=supplier_id)
    
    # Calculate revenue per store
    store_revenue = defaultdict(float)
    store_order_count = defaultdict(int)
    
    for order in orders:
        shopkeeper_id = str(order.shopkeeper_id.id)
        store_revenue[shopkeeper_id] += order.total_amount if order.status == 'delivered' else 0
        store_order_count[shopkeeper_id] += 1
    
    # Build top stores list
    top_stores = []
    for store in stores:
        store_id = store['id']
        total_revenue = store_revenue.get(store_id, 0)
        order_count = store_order_count.get(store_id, 0)
        
        top_stores.append({
            'id': store_id,
            'name': store['name'],
            'total_revenue': total_revenue,
            'order_count': order_count,
            'credit_score': store.get('credit_score', 0)
        })
    
    # Sort by revenue descending
    top_stores.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    return {
        'top_stores': top_stores,
        'total_stores': len(stores)
    }


def get_analytics_revenue(supplier_id, days=30):
    """
    Get revenue analytics data over time
    
    Args:
        supplier_id: Supplier ID
        days: Number of days to look back
    
    Returns:
        dict: Revenue analytics data
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get delivered orders in date range
    orders = SupplierOrder.objects(
        supplier_id=supplier_id,
        status='delivered',
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by('created_at')
    
    # Group by date
    revenue_by_date = defaultdict(float)
    
    for order in orders:
        date_key = order.created_at.date().isoformat()
        revenue_by_date[date_key] += order.total_amount
    
    # Convert to list format
    revenue_over_time = []
    for date_str in sorted(revenue_by_date.keys()):
        revenue_over_time.append({
            'date': date_str,
            'revenue': revenue_by_date[date_str]
        })
    
    return {
        'revenue_over_time': revenue_over_time,
        'days': days,
        'total_revenue': sum(revenue_by_date.values())
    }


def _get_stores_in_service_area(supplier):
    """
    Helper function to get stores in service area (reused logic)
    """
    if not supplier.service_area_center:
        return []
    
    from services.supplier.supplier_service import get_stores_in_service_area as get_stores
    return get_stores(str(supplier.id))

