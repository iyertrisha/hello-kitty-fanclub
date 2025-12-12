"""
Order routing service - Find nearest stores and route orders
"""
import math
from database.models import Shopkeeper, Product
from api.middleware.error_handler import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


def calculate_distance(location1, location2):
    """
    Calculate distance between two locations using Haversine formula
    
    Args:
        location1: Dict with 'latitude' and 'longitude'
        location2: Dict with 'latitude' and 'longitude'
    
    Returns:
        float: Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    lat1 = math.radians(location1['latitude'])
    lon1 = math.radians(location1['longitude'])
    lat2 = math.radians(location2['latitude'])
    lon2 = math.radians(location2['longitude'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def check_inventory(store_id, product_id, quantity):
    """
    Check if store has sufficient inventory
    
    Args:
        store_id: Shopkeeper ID
        product_id: Product ID
        quantity: Required quantity
    
    Returns:
        bool: True if sufficient inventory available
    """
    try:
        product = Product.objects.get(id=product_id, shopkeeper_id=store_id)
        return product.stock_quantity >= quantity
    except Product.DoesNotExist:
        return False


def find_nearest_store(product_id, quantity, customer_location, max_distance_km=10):
    """
    Find nearest store with inventory
    
    Args:
        product_id: Product ID
        quantity: Required quantity
        customer_location: Dict with 'latitude' and 'longitude'
        max_distance_km: Maximum distance in kilometers (default: 10)
    
    Returns:
        dict: Store details with distance, or None if not found
    """
    # Find all products with matching name/category
    try:
        target_product = Product.objects.get(id=product_id)
        product_name = target_product.name
    except Product.DoesNotExist:
        raise NotFoundError(f"Product {product_id} not found")
    
    # Find all stores with this product in stock
    products = Product.objects(
        name=product_name,
        stock_quantity__gte=quantity
    )
    
    if not products:
        return None
    
    # Calculate distances and find nearest
    nearest_store = None
    min_distance = float('inf')
    
    for product in products:
        shopkeeper = product.shopkeeper_id
        if not shopkeeper.location:
            continue
        
        store_location = {
            'latitude': shopkeeper.location.latitude,
            'longitude': shopkeeper.location.longitude
        }
        
        distance = calculate_distance(customer_location, store_location)
        
        if distance <= max_distance_km and distance < min_distance:
            min_distance = distance
            nearest_store = {
                'shopkeeper_id': str(shopkeeper.id),
                'shopkeeper_name': shopkeeper.name,
                'address': shopkeeper.address,
                'phone': shopkeeper.phone,
                'distance_km': round(distance, 2),
                'product_id': str(product.id),
                'price': product.price,
                'stock_quantity': product.stock_quantity
            }
    
    return nearest_store


def route_order(order_data):
    """
    Route order to best store
    
    Args:
        order_data: Order data with product_id, quantity, customer_location
    
    Returns:
        dict: Routing result with store details and estimated delivery
    """
    required_fields = ['product_id', 'quantity', 'customer_location']
    for field in required_fields:
        if field not in order_data:
            raise ValidationError(f"Missing required field: {field}")
    
    customer_location = order_data['customer_location']
    if 'latitude' not in customer_location or 'longitude' not in customer_location:
        raise ValidationError("customer_location must have 'latitude' and 'longitude'")
    
    # Find nearest store
    nearest_store = find_nearest_store(
        product_id=order_data['product_id'],
        quantity=order_data['quantity'],
        customer_location=customer_location,
        max_distance_km=order_data.get('max_distance_km', 10)
    )
    
    if not nearest_store:
        raise NotFoundError("No store found with sufficient inventory within range")
    
    # Estimate delivery time (simple calculation: 30 min base + 5 min per km)
    estimated_delivery_minutes = 30 + (nearest_store['distance_km'] * 5)
    
    return {
        'routed_to': nearest_store,
        'estimated_delivery_minutes': int(estimated_delivery_minutes),
        'total_amount': nearest_store['price'] * order_data['quantity']
    }

