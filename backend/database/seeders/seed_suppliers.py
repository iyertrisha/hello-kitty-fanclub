"""
Seed data for Suppliers and Supplier Orders
Creates sample suppliers and orders for testing the supplier portal
"""
import sys
from pathlib import Path

# Add parent directory to path so imports work when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
import random
from database.models import Supplier, SupplierOrder, Shopkeeper, Location
from mongoengine import connect
from config import Config
import logging

logger = logging.getLogger(__name__)


def seed_suppliers(count=3):
    """Seed suppliers with service areas"""
    suppliers = []
    
    supplier_data = [
        {
            'name': 'Delhi Grocery Suppliers',
            'email': 'supplier1@example.com',
            'phone': '+919876543301',
            'company_name': 'Delhi Grocery Suppliers Ltd',
            'address': 'Delhi Warehouse, Connaught Place, Delhi',
            'service_area_center': {'latitude': 28.6139, 'longitude': 77.2090},  # Connaught Place, Delhi
            'service_area_radius_km': 35.0  # Larger radius to cover more of Delhi
        },
        {
            'name': 'Mumbai Wholesale Distributors',
            'email': 'supplier2@example.com',
            'phone': '+919876543300',
            'company_name': 'Mumbai Wholesale Distributors Pvt Ltd',
            'address': 'Mumbai Distribution Center, Andheri East, Mumbai',
            'service_area_center': {'latitude': 19.1136, 'longitude': 72.8697},  # Andheri, Mumbai
            'service_area_radius_km': 25.0
        },
        {
            'name': 'Bangalore Food Distributors',
            'email': 'supplier3@example.com',
            'phone': '+919876543302',
            'company_name': 'Bangalore Food Distributors',
            'address': 'Bangalore Supply Hub, Koramangala, Bangalore',
            'service_area_center': {'latitude': 12.9352, 'longitude': 77.6245},  # Koramangala, Bangalore
            'service_area_radius_km': 20.0
        }
    ]
    
    for i, data in enumerate(supplier_data[:count]):
        # Check if already exists
        existing = Supplier.objects(email=data['email']).first()
        if existing:
            logger.info(f"Supplier {data['name']} already exists, skipping")
            supplier = existing
        else:
            supplier = Supplier(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                company_name=data['company_name'],
                address=data['address'],
                is_active=True
            )
            
            # Set service area
            center = data['service_area_center']
            supplier.service_area_center = Location(
                latitude=center['latitude'],
                longitude=center['longitude'],
                address=data['address']
            )
            supplier.service_area_radius_km = data['service_area_radius_km']
            
            supplier.save()
            logger.info(f"Created supplier: {supplier.name}")
        
        suppliers.append(supplier)
    
    return suppliers


def seed_supplier_orders(suppliers, shopkeepers, count=20):
    """Seed supplier orders"""
    orders = []
    
    # Common products for orders
    common_products = [
        {'name': 'Rice', 'quantity_range': (50, 200), 'price_range': (45, 55)},
        {'name': 'Wheat Flour', 'quantity_range': (30, 100), 'price_range': (38, 42)},
        {'name': 'Sugar', 'quantity_range': (25, 80), 'price_range': (42, 48)},
        {'name': 'Cooking Oil', 'quantity_range': (20, 60), 'price_range': (115, 125)},
        {'name': 'Tea', 'quantity_range': (10, 40), 'price_range': (190, 210)},
        {'name': 'Coffee', 'quantity_range': (5, 25), 'price_range': (290, 310)},
        {'name': 'Salt', 'quantity_range': (40, 120), 'price_range': (18, 22)},
        {'name': 'Milk Powder', 'quantity_range': (15, 50), 'price_range': (250, 300)},
        {'name': 'Spices Mix', 'quantity_range': (20, 60), 'price_range': (150, 200)},
        {'name': 'Biscuits', 'quantity_range': (30, 100), 'price_range': (25, 35)},
    ]
    
    statuses = ['pending', 'confirmed', 'dispatched', 'delivered', 'cancelled']
    status_weights = [0.15, 0.20, 0.15, 0.45, 0.05]  # More delivered orders
    
    for i in range(count):
        supplier = random.choice(suppliers)
        
        # Get shopkeepers in supplier's service area (or random if none)
        if supplier.service_area_center:
            # For simplicity, pick random shopkeeper (in real scenario, filter by distance)
            shopkeeper = random.choice(shopkeepers)
        else:
            shopkeeper = random.choice(shopkeepers)
        
        # Create order with 2-5 products
        num_products = random.randint(2, 5)
        products = random.sample(common_products, num_products)
        
        order_products = []
        for prod_template in products:
            quantity = random.randint(*prod_template['quantity_range'])
            unit_price = random.uniform(*prod_template['price_range'])
            order_products.append({
                'name': prod_template['name'],
                'quantity': quantity,
                'unit_price': round(unit_price, 2)
            })
        
        total_amount = sum(p['quantity'] * p['unit_price'] for p in order_products)
        
        # Random date in last 60 days
        created_at = datetime.utcnow() - timedelta(days=random.randint(0, 60))
        
        # Weighted random status
        status = random.choices(statuses, weights=status_weights)[0]
        
        order = SupplierOrder(
            supplier_id=supplier,
            shopkeeper_id=shopkeeper,
            products=order_products,
            total_amount=round(total_amount, 2),
            status=status,
            created_at=created_at,
            notes=f"Sample bulk order {i+1}"
        )
        
        order.save()
        orders.append(order)
        
        if (i + 1) % 5 == 0:
            logger.info(f"Created {i+1} supplier orders")
    
    logger.info(f"Created {len(orders)} supplier orders")
    return orders


def seed_all():
    """Seed all supplier data"""
    logger.info("Starting supplier data seeding...")
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    # Get existing shopkeepers (required for orders)
    shopkeepers = list(Shopkeeper.objects())
    if not shopkeepers:
        logger.warning("No shopkeepers found! Please run seed_data.py first to create shopkeepers.")
        return
    
    logger.info(f"Found {len(shopkeepers)} shopkeepers")
    
    # Seed suppliers
    suppliers = seed_suppliers(3)
    
    # Seed supplier orders
    orders = seed_supplier_orders(suppliers, shopkeepers, 20)
    
    logger.info("✅ Supplier data seeding completed!")
    logger.info(f"  - Suppliers: {len(suppliers)}")
    logger.info(f"  - Supplier Orders: {len(orders)}")
    
    # Print supplier login info
    logger.info("\n📧 Supplier Login Credentials (for OTP login):")
    for supplier in suppliers:
        logger.info(f"  - {supplier.name}: {supplier.email}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    seed_all()

