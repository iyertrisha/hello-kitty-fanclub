"""
Transaction service - Business logic for transactions
"""
from datetime import datetime, timedelta
from database.models import Transaction, Shopkeeper, Customer, Product
from api.middleware.error_handler import ValidationError, NotFoundError
import logging

logger = logging.getLogger(__name__)


def validate_transaction(data):
    """
    Validate transaction data against business rules
    
    Args:
        data: Transaction data dictionary
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['type', 'amount', 'shopkeeper_id', 'customer_id']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate transaction type
    if data['type'] not in ['sale', 'credit', 'repay']:
        return False, f"Invalid transaction type: {data['type']}"
    
    # Validate amount
    if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        return False, "Amount must be a positive number"
    
    # For sales transactions, validate product if provided
    if data['type'] == 'sale' and 'product_id' in data and data['product_id']:
        try:
            product = Product.objects.get(id=data['product_id'])
            # Check if product belongs to shopkeeper
            if str(product.shopkeeper_id.id) != str(data['shopkeeper_id']):
                return False, "Product does not belong to this shopkeeper"
            
            # Check price is within ±20% of catalog price
            catalog_price = product.price
            transaction_price = data.get('price', data['amount'])
            price_diff_percent = abs(transaction_price - catalog_price) / catalog_price * 100
            if price_diff_percent > 20:
                logger.warning(f"Price difference {price_diff_percent:.2f}% exceeds 20% threshold")
                # Don't fail, just warn
            
            # Check stock availability
            if product.stock_quantity < data.get('quantity', 1):
                return False, "Insufficient stock"
        
        except Product.DoesNotExist:
            return False, "Product not found"
    
    # Validate shopkeeper exists
    try:
        from bson.errors import InvalidId
        Shopkeeper.objects.get(id=data['shopkeeper_id'])
    except (Shopkeeper.DoesNotExist, InvalidId):
        return False, "Shopkeeper not found"
    
    # Validate customer exists
    try:
        from bson.errors import InvalidId
        Customer.objects.get(id=data['customer_id'])
    except (Customer.DoesNotExist, InvalidId):
        return False, "Customer not found"
    
    # For credit transactions, check if amount is reasonable
    if data['type'] == 'credit':
        try:
            shopkeeper = Shopkeeper.objects.get(id=data['shopkeeper_id'])
            # Get average daily sales (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sales = Transaction.objects(
                shopkeeper_id=data['shopkeeper_id'],
                type='sale',
                timestamp__gte=thirty_days_ago
            )
            
            if recent_sales:
                total_sales = sum(t.amount for t in recent_sales)
                avg_daily_sales = total_sales / 30
                # Credit should not exceed 3x average daily sales
                if data['amount'] > avg_daily_sales * 3:
                    logger.warning(f"Credit amount {data['amount']} exceeds 3x average daily sales {avg_daily_sales}")
                    # Don't fail, just warn
        except Exception as e:
            logger.warning(f"Could not validate credit amount: {e}")
    
    return True, None


def create_transaction(data):
    """
    Create a new transaction
    
    Args:
        data: Transaction data dictionary
    
    Returns:
        Transaction: Created transaction object
    """
    # Validate transaction
    is_valid, error_message = validate_transaction(data)
    if not is_valid:
        raise ValidationError(error_message)
    
    # Get shopkeeper and customer objects for references
    try:
        from bson.errors import InvalidId
        shopkeeper = Shopkeeper.objects.get(id=data['shopkeeper_id'])
        customer = Customer.objects.get(id=data['customer_id'])
    except (Shopkeeper.DoesNotExist, InvalidId):
        raise ValidationError("Shopkeeper not found")
    except (Customer.DoesNotExist, InvalidId):
        raise ValidationError("Customer not found")
    
    # Get product if provided
    product = None
    if data.get('product_id'):
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise ValidationError("Product not found")
    
    # Create transaction
    transaction = Transaction(
        type=data['type'],
        amount=data['amount'],
        shopkeeper_id=shopkeeper,
        customer_id=customer,
        product_id=product,
        timestamp=data.get('timestamp', datetime.utcnow()),
        status=data.get('status', 'pending'),
        transcript_hash=data.get('transcript_hash'),
        notes=data.get('notes')
    )
    
    transaction.save()
    
    # Update customer statistics (customer object already retrieved above)
    if data['type'] == 'sale':
        customer.total_purchases += data['amount']
    elif data['type'] == 'credit':
        customer.total_credits += data['amount']
        customer.credit_balance += data['amount']
    elif data['type'] == 'repay':
        customer.credit_balance -= data['amount']
        if customer.credit_balance < 0:
            customer.credit_balance = 0
    customer.save()
    
    logger.info(f"Created transaction {transaction.id} of type {data['type']} for amount {data['amount']}")
    
    return transaction


def get_transactions(filters=None, page=1, page_size=20):
    """
    Get transactions with filtering and pagination
    
    Args:
        filters: Dictionary of filters (shopkeeper_id, customer_id, type, date_from, date_to, status)
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        tuple: (transactions list, total count, page, page_size)
    """
    if filters is None:
        filters = {}
    
    query = Transaction.objects()
    
    # Apply filters
    if 'shopkeeper_id' in filters:
        query = query.filter(shopkeeper_id=filters['shopkeeper_id'])
    
    if 'customer_id' in filters:
        query = query.filter(customer_id=filters['customer_id'])
    
    if 'type' in filters:
        query = query.filter(type=filters['type'])
    
    if 'status' in filters:
        query = query.filter(status=filters['status'])
    
    if 'date_from' in filters:
        query = query.filter(timestamp__gte=filters['date_from'])
    
    if 'date_to' in filters:
        query = query.filter(timestamp__lte=filters['date_to'])
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    transactions = query.order_by('-timestamp').skip(skip).limit(page_size)
    
    return list(transactions), total_count, page, page_size


def get_transaction_by_id(transaction_id):
    """
    Get transaction by ID
    
    Args:
        transaction_id: Transaction ID
    
    Returns:
        Transaction: Transaction object
    """
    try:
        from bson.errors import InvalidId
        transaction = Transaction.objects.get(id=transaction_id)
    except (Transaction.DoesNotExist, InvalidId):
        raise NotFoundError(f"Transaction {transaction_id} not found")
    
    return transaction


def update_transaction_status(transaction_id, status, blockchain_tx_id=None, blockchain_block_number=None):
    """
    Update transaction status
    
    Args:
        transaction_id: Transaction ID
        status: New status ('pending', 'verified', 'disputed', 'completed')
        blockchain_tx_id: Optional blockchain transaction hash
        blockchain_block_number: Optional blockchain block number
    
    Returns:
        Transaction: Updated transaction object
    """
    try:
        from bson.errors import InvalidId
        transaction = Transaction.objects.get(id=transaction_id)
    except (Transaction.DoesNotExist, InvalidId):
        raise NotFoundError(f"Transaction {transaction_id} not found")
    
    # Validate status
    if status not in Transaction.STATUS_CHOICES:
        raise ValidationError(f"Invalid status: {status}. Must be one of {Transaction.STATUS_CHOICES}")
    
    transaction.status = status
    
    if blockchain_tx_id:
        transaction.blockchain_tx_id = blockchain_tx_id
    
    if blockchain_block_number:
        transaction.blockchain_block_number = blockchain_block_number
    
    transaction.save()
    
    logger.info(f"Updated transaction {transaction_id} status to {status}")
    
    return transaction


def aggregate_daily_sales(shopkeeper_id, start_date=None, end_date=None):
    """
    Aggregate daily sales for a shopkeeper
    
    Args:
        shopkeeper_id: Shopkeeper ID
        start_date: Start date (datetime)
        end_date: End date (datetime)
    
    Returns:
        list: List of daily sales dictionaries
    """
    query = Transaction.objects(
        shopkeeper_id=shopkeeper_id,
        type='sale',
        status='verified'
    )
    
    if start_date:
        query = query.filter(timestamp__gte=start_date)
    
    if end_date:
        query = query.filter(timestamp__lte=end_date)
    
    transactions = query.order_by('timestamp')
    
    # Group by date
    daily_sales = {}
    for transaction in transactions:
        date_key = transaction.timestamp.date().isoformat()
        if date_key not in daily_sales:
            daily_sales[date_key] = {
                'date': date_key,
                'count': 0,
                'total_amount': 0.0
            }
        
        daily_sales[date_key]['count'] += 1
        daily_sales[date_key]['total_amount'] += transaction.amount
    
    return list(daily_sales.values())

