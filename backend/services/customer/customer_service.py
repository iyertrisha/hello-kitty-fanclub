"""
Customer service - Business logic for customers
"""
from database.models import Customer, Transaction
from api.middleware.error_handler import NotFoundError, ValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_customer(customer_id):
    """
    Get customer with history
    
    Args:
        customer_id: Customer ID
    
    Returns:
        dict: Customer data with statistics
    """
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        raise NotFoundError(f"Customer {customer_id} not found")
    
    return {
        'id': str(customer.id),
        'name': customer.name,
        'phone': customer.phone,
        'address': customer.address,
        'created_at': customer.created_at.isoformat() if customer.created_at else None,
        'total_purchases': customer.total_purchases,
        'total_credits': customer.total_credits,
        'credit_balance': customer.credit_balance
    }


def create_customer(data):
    """
    Create new customer
    
    Args:
        data: Customer data dictionary
    
    Returns:
        Customer: Created customer object
    """
    # Validate required fields
    required_fields = ['name', 'phone']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Check if customer with phone already exists
    if Customer.objects(phone=data['phone']).first():
        raise ValidationError("Customer with this phone number already exists")
    
    # Create customer
    customer = Customer(
        name=data['name'],
        phone=data['phone'],
        address=data.get('address')
    )
    
    customer.save()
    
    logger.info(f"Created new customer {customer.id} with phone {data['phone']}")
    
    return customer


def get_customer_orders(customer_id, filters=None):
    """
    Get customer order history
    
    Args:
        customer_id: Customer ID
        filters: Optional filters (date_from, date_to, shopkeeper_id)
    
    Returns:
        list: List of transaction dictionaries
    """
    try:
        Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        raise NotFoundError(f"Customer {customer_id} not found")
    
    if filters is None:
        filters = {}
    
    query = Transaction.objects(
        customer_id=customer_id,
        type='sale'
    )
    
    # Apply filters
    if 'date_from' in filters:
        query = query.filter(timestamp__gte=filters['date_from'])
    
    if 'date_to' in filters:
        query = query.filter(timestamp__lte=filters['date_to'])
    
    if 'shopkeeper_id' in filters:
        query = query.filter(shopkeeper_id=filters['shopkeeper_id'])
    
    transactions = query.order_by('-timestamp')
    
    result = []
    for transaction in transactions:
        result.append({
            'id': str(transaction.id),
            'type': transaction.type,
            'amount': transaction.amount,
            'shopkeeper_id': str(transaction.shopkeeper_id.id),
            'product_id': str(transaction.product_id.id) if transaction.product_id else None,
            'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,
            'status': transaction.status,
            'blockchain_tx_id': transaction.blockchain_tx_id
        })
    
    return result


def get_customer_credits(customer_id):
    """
    Get customer credit transactions
    
    Args:
        customer_id: Customer ID
    
    Returns:
        list: List of credit and repayment transactions
    """
    try:
        Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        raise NotFoundError(f"Customer {customer_id} not found")
    
    transactions = Transaction.objects(
        customer_id=customer_id,
        type__in=['credit', 'repay']
    ).order_by('-timestamp')
    
    result = []
    for transaction in transactions:
        result.append({
            'id': str(transaction.id),
            'type': transaction.type,
            'amount': transaction.amount,
            'shopkeeper_id': str(transaction.shopkeeper_id.id),
            'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,
            'status': transaction.status,
            'blockchain_tx_id': transaction.blockchain_tx_id,
            'notes': transaction.notes
        })
    
    return result

