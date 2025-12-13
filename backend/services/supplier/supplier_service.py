"""
Supplier service - Business logic for suppliers
"""
from database.models import Supplier, Shopkeeper, Product, SupplierOrder, Transaction
from api.middleware.error_handler import NotFoundError, ValidationError, UnauthorizedError
import importlib.util
from pathlib import Path
# Import from order-routing (hyphenated directory name)
_order_routing_file = Path(__file__).parent.parent / 'order-routing' / 'order_routing.py'
_spec = importlib.util.spec_from_file_location('order_routing', _order_routing_file)
_order_routing_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_order_routing_module)
calculate_distance = _order_routing_module.calculate_distance
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_or_create_supplier(email):
    """
    Get existing supplier or create new one (for first-time OTP login)
    
    Args:
        email: Supplier email address
    
    Returns:
        Supplier: Supplier object
    """
    try:
        supplier = Supplier.objects.get(email=email)
    except Supplier.DoesNotExist:
        # Create new supplier on first login
        # Extract name from email (before @) as default
        default_name = email.split('@')[0].replace('.', ' ').title()
        
        supplier = Supplier(
            name=default_name,
            email=email,
            phone='',  # Will be updated later
            password_hash='',  # No password needed for OTP auth
            is_active=True
        )
        supplier.save()
        logger.info(f"Created new supplier {supplier.id} for email {email}")
    
    if not supplier.is_active:
        raise UnauthorizedError("Supplier account is inactive")
    
    return supplier


def register_supplier(data):
    """
    Register a new supplier (optional - suppliers can be auto-created on first login)
    
    Args:
        data: Supplier registration data
    
    Returns:
        Supplier: Created supplier object
    """
    required_fields = ['email']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Check if email already exists
    if Supplier.objects(email=data['email']).first():
        raise ValidationError("Supplier with this email already exists")
    
    # Create supplier
    supplier = Supplier(
        name=data.get('name', data['email'].split('@')[0].replace('.', ' ').title()),
        email=data['email'],
        phone=data.get('phone', ''),
        password_hash='',  # No password for OTP auth
        company_name=data.get('company_name'),
        address=data.get('address')
    )
    
    # Add service area if provided
    if 'service_area_center' in data:
        from database.models import Location
        supplier.service_area_center = Location(
            latitude=data['service_area_center']['latitude'],
            longitude=data['service_area_center']['longitude'],
            address=data['service_area_center'].get('address', data.get('address'))
        )
        supplier.service_area_radius_km = data.get('service_area_radius_km', 10.0)
    
    supplier.save()
    
    logger.info(f"Registered new supplier {supplier.id} with email {data['email']}")
    
    return supplier


def get_supplier(supplier_id):
    """
    Get supplier by ID
    
    Args:
        supplier_id: Supplier ID
    
    Returns:
        dict: Supplier data
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    return {
        'id': str(supplier.id),
        'name': supplier.name,
        'email': supplier.email,
        'phone': supplier.phone,
        'company_name': supplier.company_name,
        'address': supplier.address,
        'service_area_center': supplier.service_area_center.to_dict() if supplier.service_area_center else None,
        'service_area_radius_km': supplier.service_area_radius_km,
        'registered_at': supplier.registered_at.isoformat() if supplier.registered_at else None,
        'is_active': supplier.is_active
    }


def update_supplier_service_area(supplier_id, service_area_data):
    """
    Update supplier service area
    
    Args:
        supplier_id: Supplier ID
        service_area_data: Dict with center (lat/lng) and radius_km
    
    Returns:
        Supplier: Updated supplier object
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    if 'center' in service_area_data:
        from database.models import Location
        center = service_area_data['center']
        supplier.service_area_center = Location(
            latitude=center['latitude'],
            longitude=center['longitude'],
            address=center.get('address', supplier.address)
        )
    
    if 'radius_km' in service_area_data:
        supplier.service_area_radius_km = service_area_data['radius_km']
    
    supplier.save()
    
    logger.info(f"Updated service area for supplier {supplier_id}")
    
    return supplier


def get_stores_in_service_area(supplier_id):
    """
    Get all kirana stores within supplier's service area with performance metrics
    
    Args:
        supplier_id: Supplier ID
    
    Returns:
        list: List of store dictionaries with performance metrics
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    # If no service area is set, use Delhi center as default (for testing)
    if not supplier.service_area_center:
        logger.warning(f"Supplier {supplier_id} has no service area center set, using default Delhi center")
        center_location = {
            'latitude': 28.6139,  # Delhi center (Connaught Place)
            'longitude': 77.2090
        }
        radius_km = 50.0  # Large radius to show all Delhi stores
    else:
        center_location = {
            'latitude': supplier.service_area_center.latitude,
            'longitude': supplier.service_area_center.longitude
        }
        radius_km = supplier.service_area_radius_km or 10.0  # Default to 10km if not set
    
    # Get all active stores - check for location in Python rather than query
    # MongoEngine's location__exists might not work correctly
    all_stores = Shopkeeper.objects(is_active=True)
    logger.info(f"Found {all_stores.count()} active shopkeepers in database")
    
    stores_in_area = []
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    stores_without_location = 0
    
    for store in all_stores:
        # Skip stores without valid locations
        if not store.location or store.location.latitude is None or store.location.longitude is None:
            stores_without_location += 1
            continue
        
        store_location = {
            'latitude': store.location.latitude,
            'longitude': store.location.longitude
        }
        
        distance = calculate_distance(center_location, store_location)
        
        if distance <= radius_km:
            # Calculate performance metrics
            recent_transactions = Transaction.objects(
                shopkeeper_id=store.id,
                timestamp__gte=thirty_days_ago
            )
            
            total_sales_30d = sum(t.amount for t in recent_transactions if t.type == 'sale')
            transaction_count = recent_transactions.count()
            
            # Get inventory info
            products = Product.objects(shopkeeper_id=store.id)
            inventory_count = products.count()
            low_stock_count = products.filter(stock_quantity__lte=10).count()
            out_of_stock_count = products.filter(stock_quantity=0).count()
            
            # Get low stock products
            low_stock_products = []
            for product in products.filter(stock_quantity__lte=10):
                low_stock_products.append({
                    'id': str(product.id),
                    'name': product.name,
                    'category': product.category,
                    'current_stock': product.stock_quantity,
                    'price': product.price
                })
            
            stores_in_area.append({
                'id': str(store.id),
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'email': store.email,
                'location': store.location.to_dict(),
                'distance_km': round(distance, 2),
                'credit_score': store.credit_score,
                'performance': {
                    'total_sales_30d': total_sales_30d,
                    'transaction_count_30d': transaction_count,
                    'inventory_count': inventory_count,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'low_stock_products': low_stock_products
                }
            })
    
    # Sort by distance
    stores_in_area.sort(key=lambda x: x['distance_km'])
    
    logger.info(f"Found {len(stores_in_area)} stores within {radius_km}km of center ({center_location['latitude']}, {center_location['longitude']})")
    if stores_without_location > 0:
        logger.warning(f"Skipped {stores_without_location} stores without valid locations")
    
    return stores_in_area


def create_bulk_order(supplier_id, shopkeeper_id, products_data):
    """
    Create a bulk order from supplier to shopkeeper
    
    Args:
        supplier_id: Supplier ID
        shopkeeper_id: Shopkeeper ID
        products_data: List of product dicts with name, quantity, unit_price
    
    Returns:
        SupplierOrder: Created order object
    """
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        raise NotFoundError(f"Supplier {supplier_id} not found")
    
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    if not products_data:
        raise ValidationError("Products list cannot be empty")
    
    # Calculate total amount
    total_amount = sum(p['quantity'] * p['unit_price'] for p in products_data)
    
    # Create order
    order = SupplierOrder(
        supplier_id=supplier,
        shopkeeper_id=shopkeeper,
        products=products_data,
        total_amount=total_amount,
        status='pending'
    )
    
    order.save()
    
    logger.info(f"Created bulk order {order.id} from supplier {supplier_id} to shopkeeper {shopkeeper_id}")
    
    return order

