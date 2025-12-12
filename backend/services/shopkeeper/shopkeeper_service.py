"""
Shopkeeper service - Business logic for shopkeepers
"""
from database.models import Shopkeeper, Transaction, Product
from api.middleware.error_handler import NotFoundError, ValidationError
from datetime import datetime, timedelta
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)


def get_shopkeeper(shopkeeper_id):
    """
    Get shopkeeper with statistics
    
    Args:
        shopkeeper_id: Shopkeeper ID
    
    Returns:
        dict: Shopkeeper data with statistics
    """
    try:
        from bson.errors import InvalidId
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except (Shopkeeper.DoesNotExist, InvalidId):
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Calculate statistics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_transactions = Transaction.objects(
        shopkeeper_id=shopkeeper_id,
        timestamp__gte=thirty_days_ago
    )
    
    total_sales = sum(t.amount for t in recent_transactions if t.type == 'sale')
    total_credits = sum(t.amount for t in recent_transactions if t.type == 'credit')
    total_repayments = sum(t.amount for t in recent_transactions if t.type == 'repay')
    
    # Get inventory count
    inventory_count = Product.objects(shopkeeper_id=shopkeeper_id).count()
    low_stock_count = Product.objects(shopkeeper_id=shopkeeper_id, stock_quantity__lte=10).count()
    
    return {
        'id': str(shopkeeper.id),
        'name': shopkeeper.name,
        'address': shopkeeper.address,
        'phone': shopkeeper.phone,
        'email': shopkeeper.email,
        'wallet_address': shopkeeper.wallet_address,
        'blockchain_address': shopkeeper.blockchain_address,
        'credit_score': shopkeeper.credit_score,
        'registered_at': shopkeeper.registered_at.isoformat() if shopkeeper.registered_at else None,
        'is_active': shopkeeper.is_active,
        'location': shopkeeper.location.to_dict() if shopkeeper.location else None,
        'stats': {
            'total_sales_30d': total_sales,
            'total_credits_30d': total_credits,
            'total_repayments_30d': total_repayments,
            'inventory_count': inventory_count,
            'low_stock_count': low_stock_count
        }
    }


def update_shopkeeper(shopkeeper_id, data):
    """
    Update shopkeeper profile
    
    Args:
        shopkeeper_id: Shopkeeper ID
        data: Dictionary of fields to update
    
    Returns:
        Shopkeeper: Updated shopkeeper object
    """
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Update allowed fields
    allowed_fields = ['name', 'address', 'phone', 'email', 'is_active']
    for field in allowed_fields:
        if field in data:
            setattr(shopkeeper, field, data[field])
    
    # Update location if provided
    if 'location' in data:
        from database.models import Location
        if shopkeeper.location:
            shopkeeper.location.latitude = data['location'].get('latitude', shopkeeper.location.latitude)
            shopkeeper.location.longitude = data['location'].get('longitude', shopkeeper.location.longitude)
            shopkeeper.location.address = data['location'].get('address', shopkeeper.location.address)
        else:
            shopkeeper.location = Location(
                latitude=data['location']['latitude'],
                longitude=data['location']['longitude'],
                address=data['location'].get('address')
            )
    
    shopkeeper.save()
    
    logger.info(f"Updated shopkeeper {shopkeeper_id}")
    
    return shopkeeper


def calculate_credit_score(shopkeeper_id):
    """
    Calculate credit score by calling ML service
    
    Args:
        shopkeeper_id: Shopkeeper ID
    
    Returns:
        dict: Credit score data with factors and explanation
    """
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Call ML service endpoint (Mohit's service)
    try:
        ml_service_url = Config.ML_SERVICE_URL
        response = requests.post(
            f"{ml_service_url}/creditScore",
            json={'shopkeeper_id': str(shopkeeper_id)},
            timeout=10
        )
        
        if response.status_code == 200:
            credit_data = response.json()
            # Update shopkeeper credit score
            shopkeeper.credit_score = credit_data.get('score', shopkeeper.credit_score)
            shopkeeper.save()
            return credit_data
        else:
            logger.warning(f"ML service returned {response.status_code}, using default calculation")
    except Exception as e:
        logger.error(f"Error calling ML service: {e}, using default calculation")
    
    # Fallback: Simple calculation if ML service unavailable
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    transactions = Transaction.objects(
        shopkeeper_id=shopkeeper_id,
        timestamp__gte=thirty_days_ago
    )
    
    total_sales = sum(t.amount for t in transactions if t.type == 'sale')
    total_credits = sum(t.amount for t in transactions if t.type == 'credit')
    total_repayments = sum(t.amount for t in transactions if t.type == 'repay')
    
    # Simple score calculation (300-900 range)
    base_score = 300
    sales_score = min(total_sales / 1000 * 100, 200)  # Max 200 points
    repayment_ratio = total_repayments / total_credits if total_credits > 0 else 1.0
    repayment_score = repayment_ratio * 200  # Max 200 points
    consistency_score = min(len(transactions) * 2, 200)  # Max 200 points
    
    score = int(base_score + sales_score + repayment_score + consistency_score)
    score = min(900, max(300, score))  # Clamp to 300-900
    
    return {
        'score': score,
        'factors': {
            'sales_volume': sales_score,
            'repayment_history': repayment_score,
            'transaction_consistency': consistency_score
        },
        'explanation': f"Credit score calculated from sales volume, repayment history, and transaction consistency",
        'blockchain_verified': False
    }


def get_inventory(shopkeeper_id, include_low_stock=True):
    """
    Get shopkeeper inventory with stock alerts
    
    Args:
        shopkeeper_id: Shopkeeper ID
        include_low_stock: Whether to include low stock flag
    
    Returns:
        list: List of product dictionaries
    """
    try:
        Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    products = Product.objects(shopkeeper_id=shopkeeper_id)
    
    result = []
    for product in products:
        product_data = {
            'id': str(product.id),
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'description': product.description,
            'created_at': product.created_at.isoformat() if product.created_at else None
        }
        
        if include_low_stock:
            product_data['low_stock'] = product.stock_quantity <= 10
            product_data['out_of_stock'] = product.stock_quantity == 0
        
        result.append(product_data)
    
    return result


def register_shopkeeper(data):
    """
    Register a new shopkeeper
    
    Args:
        data: Shopkeeper registration data
    
    Returns:
        Shopkeeper: Created shopkeeper object
    """
    # Validate required fields
    required_fields = ['name', 'address', 'phone', 'wallet_address']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Check if wallet address already exists
    if Shopkeeper.objects(wallet_address=data['wallet_address']).first():
        raise ValidationError("Shopkeeper with this wallet address already exists")
    
    # Create shopkeeper
    shopkeeper = Shopkeeper(
        name=data['name'],
        address=data['address'],
        phone=data['phone'],
        email=data.get('email'),
        wallet_address=data['wallet_address'],
        blockchain_address=data.get('blockchain_address', data['wallet_address'])
    )
    
    # Add location if provided
    if 'location' in data:
        from database.models import Location
        shopkeeper.location = Location(
            latitude=data['location']['latitude'],
            longitude=data['location']['longitude'],
            address=data['location'].get('address', data['address'])
        )
    
    shopkeeper.save()
    
    logger.info(f"Registered new shopkeeper {shopkeeper.id} with wallet {data['wallet_address']}")
    
    return shopkeeper

