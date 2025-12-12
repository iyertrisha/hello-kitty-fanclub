"""
Grocery service - Core business logic for grocery ordering
"""
from database.models import Product, Shopkeeper, Customer
from api.middleware.error_handler import NotFoundError, ValidationError
from services.transaction import create_transaction
from services.debt import get_customer_by_phone
import logging

logger = logging.getLogger(__name__)

# Try to import fuzzy matching library
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process
        FUZZY_AVAILABLE = True
    except ImportError:
        FUZZY_AVAILABLE = False
        logger.warning("Fuzzy matching not available. Install 'rapidfuzz' or 'fuzzywuzzy' for better product matching.")


def get_products_for_shopkeeper(shopkeeper_id):
    """
    Get all products for a shopkeeper
    
    Args:
        shopkeeper_id: Shopkeeper ID
        
    Returns:
        list: Product objects
    """
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    products = Product.objects(shopkeeper_id=shopkeeper)
    return list(products)


def match_product_name(product_name, shopkeeper_id, threshold=60):
    """
    Match product name to database product using fuzzy matching
    
    Args:
        product_name: Product name to match
        shopkeeper_id: Shopkeeper ID
        threshold: Minimum similarity threshold (0-100)
        
    Returns:
        Product: Matched product or None
    """
    products = get_products_for_shopkeeper(shopkeeper_id)
    
    if not products:
        return None
    
    # Try exact match first (case insensitive)
    product_name_lower = product_name.lower().strip()
    for product in products:
        if product.name.lower().strip() == product_name_lower:
            return product
    
    # Use fuzzy matching if available
    if FUZZY_AVAILABLE:
        try:
            # Get best match
            result = process.extractOne(
                product_name,
                [p.name for p in products],
                scorer=fuzz.token_sort_ratio
            )
            
            if result and result[1] >= threshold:
                # Find the product object
                matched_name = result[0]
                for product in products:
                    if product.name == matched_name:
                        return product
        except Exception as e:
            logger.warning(f"Fuzzy matching error: {e}")
    
    return None


def parse_grocery_list(list_text, shopkeeper_id, parsed_items=None):
    """
    Parse grocery list and match products
    
    Args:
        list_text: Raw grocery list text
        shopkeeper_id: Shopkeeper ID
        parsed_items: Pre-parsed items from frontend (optional)
        
    Returns:
        dict: {
            'items': [{'product_id': str, 'name': str, 'quantity': float, 'unit': str, 'price': float}],
            'total': float,
            'unmatched': [str]
        }
    """
    if not parsed_items:
        # If not pre-parsed, return error (parsing should be done in frontend)
        raise ValidationError("Parsed items required")
    
    matched_items = []
    unmatched_items = []
    
    for item in parsed_items:
        product_name = item.get('name', '').strip()
        quantity = float(item.get('quantity', 1))
        unit = item.get('unit', 'piece')
        
        if not product_name:
            continue
        
        # Match product
        product = match_product_name(product_name, shopkeeper_id)
        
        if product:
            # Check stock availability
            if product.stock_quantity < quantity and unit == 'piece':
                # For pieces, check if we have enough
                if product.stock_quantity == 0:
                    unmatched_items.append(f"{product_name} (out of stock)")
                    continue
                elif product.stock_quantity < quantity:
                    # Adjust quantity to available stock
                    quantity = product.stock_quantity
                    logger.info(f"Adjusted quantity for {product_name} to available stock: {quantity}")
            
            # Calculate price based on quantity and unit
            # Product price is typically per kg for weight items, per piece for count items
            price_per_unit = product.price
            
            # Handle unit conversions for pricing
            # If product is sold by weight (kg), convert grams to kg
            if unit == 'g' or unit == 'gram' or unit == 'grams':
                # Convert grams to kg (divide by 1000)
                quantity_in_kg = quantity / 1000.0
                total_price = price_per_unit * quantity_in_kg
            elif unit == 'kg' or unit == 'kilo' or unit == 'kilogram':
                # Already in kg
                total_price = price_per_unit * quantity
            else:
                # For pieces, packs, etc., use quantity as-is
                total_price = price_per_unit * quantity
            
            matched_items.append({
                'product_id': str(product.id),
                'name': product.name,
                'quantity': quantity,
                'unit': unit,
                'price': price_per_unit,
                'total_price': total_price
                # Note: Don't store product object as it's not JSON serializable
            })
        else:
            unmatched_items.append(product_name)
    
    # Calculate total
    total = sum(item['total_price'] for item in matched_items)
    
    return {
        'items': matched_items,
        'total': round(total, 2),
        'unmatched': unmatched_items
    }


def calculate_bill(items):
    """
    Calculate bill total from items
    
    Args:
        items: List of items with 'total_price' or 'price' and 'quantity'
        
    Returns:
        float: Total amount
    """
    total = 0.0
    
    for item in items:
        if 'total_price' in item:
            total += item['total_price']
        elif 'price' in item and 'quantity' in item:
            total += item['price'] * item['quantity']
        elif 'price' in item:
            total += item['price']
    
    return round(total, 2)


def create_grocery_order(customer_phone, items, shopkeeper_id):
    """
    Create grocery order and transaction
    
    Args:
        customer_phone: Customer phone number
        items: List of order items
        shopkeeper_id: Shopkeeper ID
        
    Returns:
        dict: {
            'order_id': str,
            'transaction_id': str,
            'bill': dict,
            'blockchain_tx_id': str (optional)
        }
    """
    # Validate inputs
    if not items or len(items) == 0:
        raise ValidationError("Order items cannot be empty")
    
    # Get customer
    customer = get_customer_by_phone(customer_phone)
    
    # Get shopkeeper
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Calculate total
    total = calculate_bill(items)
    
    # Update product stock and create order details
    order_details = []
    for item in items:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 1)
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id, shopkeeper_id=shopkeeper)
                
                # Update stock (only for pieces, not weight/volume)
                if item.get('unit') == 'piece':
                    if product.stock_quantity < quantity:
                        raise ValidationError(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")
                    product.stock_quantity -= int(quantity)
                    product.save()
                
                order_details.append({
                    'product_id': str(product.id),
                    'product_name': product.name,
                    'quantity': quantity,
                    'unit': item.get('unit', 'piece'),
                    'price': item.get('price', product.price),
                    'total': item.get('total_price', product.price * quantity)
                })
            except Product.DoesNotExist:
                logger.warning(f"Product {product_id} not found, skipping stock update")
    
    # Create transaction
    transaction_data = {
        'type': 'credit',
        'amount': float(total),
        'shopkeeper_id': str(shopkeeper.id),
        'customer_id': str(customer.id),
        'status': 'verified',
        'notes': f'Grocery order: {", ".join([d["product_name"] for d in order_details[:3]])}'
    }
    
    transaction = create_transaction(transaction_data)
    
    # Try to record on blockchain
    blockchain_tx_id = None
    try:
        import sys
        from pathlib import Path
        blockchain_path = Path(__file__).parent.parent.parent / 'blockchain'
        sys.path.insert(0, str(blockchain_path))
        
        from utils.contract_service import BlockchainService
        from config import BlockchainConfig
        
        if BlockchainConfig.CONTRACT_ADDRESS and BlockchainConfig.PRIVATE_KEY:
            blockchain_service = BlockchainService()
            blockchain_result = blockchain_service.record_transaction(
                shopkeeper_id=str(shopkeeper.id),
                customer_id=str(customer.id),
                amount=float(total),
                transaction_type='credit'
            )
            if blockchain_result and blockchain_result.get('success'):
                blockchain_tx_id = blockchain_result.get('transaction_hash')
                transaction.blockchain_tx_id = blockchain_tx_id
                transaction.save()
    except Exception as e:
        logger.warning(f"Blockchain recording failed: {e}")
    
    # Generate order ID (use transaction ID)
    order_id = str(transaction.id)
    
    return {
        'order_id': order_id,
        'transaction_id': str(transaction.id),
        'bill': {
            'items': order_details,
            'total': total,
            'customer_name': customer.name,
            'shopkeeper_name': shopkeeper.name
        },
        'blockchain_tx_id': blockchain_tx_id
    }

