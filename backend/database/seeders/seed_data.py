"""
Database seed data script
Creates sample data for development and testing
"""
import sys
from pathlib import Path

# Add parent directory to path so imports work when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
import random
from database.models import Shopkeeper, Customer, Product, Transaction, Cooperative, Location, Supplier, SupplierOrder
from mongoengine import connect
from config import Config
import logging

logger = logging.getLogger(__name__)


def seed_shopkeepers(count=30):
    """Seed shopkeepers"""
    shopkeepers = []
    
    # Sample shopkeeper data - Mostly in Delhi area for supplier portal testing
    # Delhi coordinates: 28.6139, 77.2090 (Connaught Place)
    shopkeeper_data = [
        {'name': 'Rajesh Kirana Store', 'address': '123 Main Street, Connaught Place, Delhi', 'phone': '+919876543210', 'wallet': '0x1111111111111111111111111111111111111111', 'lat': 28.6300, 'lng': 77.2170},
        {'name': 'Priya Grocery', 'address': '456 Market Road, Karol Bagh, Delhi', 'phone': '+919876543211', 'wallet': '0x2222222222222222222222222222222222222222', 'lat': 28.6500, 'lng': 77.1950},
        {'name': 'Amit General Store', 'address': '789 Commercial Area, Lajpat Nagar, Delhi', 'phone': '+919876543212', 'wallet': '0x3333333333333333333333333333333333333333', 'lat': 28.5680, 'lng': 77.2430},
        {'name': 'Sunita Provision Store', 'address': '321 Residential Colony, Janakpuri, Delhi', 'phone': '+919876543213', 'wallet': '0x4444444444444444444444444444444444444444', 'lat': 28.6300, 'lng': 77.0880},
        {'name': 'Vikram Kirana', 'address': '654 High Street, Rohini, Delhi', 'phone': '+919876543214', 'wallet': '0x5555555555555555555555555555555555555555', 'lat': 28.7400, 'lng': 77.1200},
        {'name': 'Meera Groceries', 'address': '987 Shopping Complex, Dwarka, Delhi', 'phone': '+919876543215', 'wallet': '0x6666666666666666666666666666666666666666', 'lat': 28.5900, 'lng': 77.0460},
        {'name': 'Kumar Store', 'address': '147 Village Road, Saket, Delhi', 'phone': '+919876543216', 'wallet': '0x7777777777777777777777777777777777777777', 'lat': 28.5240, 'lng': 77.2060},
        {'name': 'Lakshmi Kirana', 'address': '258 Town Center, Chandni Chowk, Delhi', 'phone': '+919876543217', 'wallet': '0x8888888888888888888888888888888888888888', 'lat': 28.6510, 'lng': 77.2310},
        # Additional stores for better map coverage
        {'name': 'Sharma General Store', 'address': 'Block A, Sector 15, Noida, Delhi NCR', 'phone': '+919876543218', 'wallet': '0x9999999999999999999999999999999999999999', 'lat': 28.5800, 'lng': 77.3200},
        {'name': 'Patel Kirana', 'address': 'Main Bazaar, Paharganj, Delhi', 'phone': '+919876543219', 'wallet': '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'lat': 28.6450, 'lng': 77.2100},
        {'name': 'Gupta Provision', 'address': 'Market Complex, Rajouri Garden, Delhi', 'phone': '+919876543220', 'wallet': '0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'lat': 28.6500, 'lng': 77.1200},
        {'name': 'Singh Grocery Mart', 'address': 'Sector 18, Gurgaon, Haryana', 'phone': '+919876543221', 'wallet': '0xcccccccccccccccccccccccccccccccccccccccc', 'lat': 28.4300, 'lng': 77.0900},
        {'name': 'Verma Store', 'address': 'Model Town, North Delhi', 'phone': '+919876543222', 'wallet': '0xdddddddddddddddddddddddddddddddddddddddd', 'lat': 28.7100, 'lng': 77.2000},
        {'name': 'Yadav Kirana', 'address': 'Pitampura, North West Delhi', 'phone': '+919876543223', 'wallet': '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', 'lat': 28.6900, 'lng': 77.1400},
        {'name': 'Reddy General Store', 'address': 'Greater Kailash, South Delhi', 'phone': '+919876543224', 'wallet': '0xffffffffffffffffffffffffffffffffffffffff', 'lat': 28.5500, 'lng': 77.2400},
        {'name': 'Rao Groceries', 'address': 'Vasant Kunj, South West Delhi', 'phone': '+919876543225', 'wallet': '0x1010101010101010101010101010101010101010', 'lat': 28.5300, 'lng': 77.1500},
        {'name': 'Jain Provision Store', 'address': 'Shahdara, East Delhi', 'phone': '+919876543226', 'wallet': '0x2020202020202020202020202020202020202020', 'lat': 28.6800, 'lng': 77.2800},
        {'name': 'Agarwal Kirana', 'address': 'Patparganj, East Delhi', 'phone': '+919876543227', 'wallet': '0x3030303030303030303030303030303030303030', 'lat': 28.6200, 'lng': 77.3000},
        {'name': 'Malhotra Store', 'address': 'Paschim Vihar, West Delhi', 'phone': '+919876543228', 'wallet': '0x4040404040404040404040404040404040404040', 'lat': 28.6800, 'lng': 77.1000},
        {'name': 'Khanna Grocery', 'address': 'Rajendra Place, Central Delhi', 'phone': '+919876543229', 'wallet': '0x5050505050505050505050505050505050505050', 'lat': 28.6400, 'lng': 77.1900},
        {'name': 'Bansal Provision', 'address': 'Kirti Nagar, West Delhi', 'phone': '+919876543230', 'wallet': '0x6060606060606060606060606060606060606060', 'lat': 28.6500, 'lng': 77.1600},
        {'name': 'Mehta Kirana Store', 'address': 'Nehru Place, South Delhi', 'phone': '+919876543231', 'wallet': '0x7070707070707070707070707070707070707070', 'lat': 28.5500, 'lng': 77.2500},
        {'name': 'Seth General Store', 'address': 'Laxmi Nagar, East Delhi', 'phone': '+919876543232', 'wallet': '0x8080808080808080808080808080808080808080', 'lat': 28.6400, 'lng': 77.2800},
        {'name': 'Bhatia Groceries', 'address': 'Mayur Vihar, East Delhi', 'phone': '+919876543233', 'wallet': '0x9090909090909090909090909090909090909090', 'lat': 28.6000, 'lng': 77.3000},
        {'name': 'Chopra Store', 'address': 'Rohini Sector 7, North Delhi', 'phone': '+919876543234', 'wallet': '0xa0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0', 'lat': 28.7500, 'lng': 77.1300},
        {'name': 'Kapoor Kirana', 'address': 'Dwarka Sector 10, South West Delhi', 'phone': '+919876543235', 'wallet': '0xb0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0', 'lat': 28.5800, 'lng': 77.0500},
        {'name': 'Tandon Provision', 'address': 'Noida Sector 62, Noida', 'phone': '+919876543236', 'wallet': '0xc0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0', 'lat': 28.6200, 'lng': 77.3700},
        {'name': 'Saxena Grocery', 'address': 'Vaishali, Ghaziabad', 'phone': '+919876543237', 'wallet': '0xd0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0', 'lat': 28.6500, 'lng': 77.3400},
        {'name': 'Mathur Store', 'address': 'Sector 29, Gurgaon', 'phone': '+919876543238', 'wallet': '0xe0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0e0', 'lat': 28.4500, 'lng': 77.0800},
        {'name': 'Nair Kirana', 'address': 'Saket Market, South Delhi', 'phone': '+919876543239', 'wallet': '0xf0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0', 'lat': 28.5200, 'lng': 77.2000},
    ]
    
    for i, data in enumerate(shopkeeper_data[:count]):
        # Check if already exists
        existing = Shopkeeper.objects(wallet_address=data['wallet']).first()
        if existing:
            logger.info(f"Shopkeeper {data['name']} already exists, updating location to Delhi area")
            shopkeeper = existing
            # Update location to Delhi area if it's in Mumbai
            if shopkeeper.location and (shopkeeper.location.latitude < 19.5 or shopkeeper.location.latitude > 19.6):
                # Already in Delhi or other area, skip update
                pass
            else:
                # Update to Delhi coordinates
                base_lat = data.get('lat', 28.6139)
                base_lng = data.get('lng', 77.2090)
                shopkeeper.location = Location(
                    latitude=base_lat + random.uniform(-0.02, 0.02),
                    longitude=base_lng + random.uniform(-0.02, 0.02),
                    address=data['address']
                )
                shopkeeper.save()
                logger.info(f"Updated {shopkeeper.name} location to Delhi area")
        else:
            shopkeeper = Shopkeeper(
                name=data['name'],
                address=data['address'],
                phone=data['phone'],
                email=f"shop{i+1}@example.com",
                wallet_address=data['wallet'],
                blockchain_address=data['wallet'],
                credit_score=random.randint(400, 800),
                registered_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            
            # Add location (Delhi area coordinates - with slight variation)
            base_lat = data.get('lat', 28.6139)  # Default to Connaught Place if not specified
            base_lng = data.get('lng', 77.2090)
            shopkeeper.location = Location(
                latitude=base_lat + random.uniform(-0.02, 0.02),  # Small variation
                longitude=base_lng + random.uniform(-0.02, 0.02),
                address=data['address']
            )
            
            shopkeeper.save()
            logger.info(f"Created shopkeeper: {shopkeeper.name}")
        
        shopkeepers.append(shopkeeper)
    
    return shopkeepers


def seed_customers(count=25):
    """Seed customers"""
    customers = []
    
    first_names = ['Raj', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Meera', 'Kumar', 'Lakshmi', 'Ravi', 'Anita', 'Suresh', 'Kavita', 'Mohan', 'Deepa', 'Nitin']
    last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Verma', 'Yadav', 'Shah', 'Reddy', 'Rao']
    
    for i in range(count):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        phone = f"+9198765{random.randint(10000, 99999)}"
        
        # Check if already exists
        if Customer.objects(phone=phone).first():
            logger.info(f"Customer {name} already exists, skipping")
            customer = Customer.objects(phone=phone).first()
        else:
            customer = Customer(
                name=name,
                phone=phone,
                address=f"{random.randint(1, 999)} Street, City {i+1}",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 180))
            )
            customer.save()
            logger.info(f"Created customer: {customer.name}")
        
        customers.append(customer)
    
    return customers


def seed_products(shopkeepers, count_per_shop=12):
    """Seed products"""
    products = []
    
    product_templates = [
        {'name': 'Rice', 'category': 'Grains', 'base_price': 50},
        {'name': 'Wheat Flour', 'category': 'Grains', 'base_price': 40},
        {'name': 'Sugar', 'category': 'Essentials', 'base_price': 45},
        {'name': 'Salt', 'category': 'Essentials', 'base_price': 20},
        {'name': 'Cooking Oil', 'category': 'Essentials', 'base_price': 120},
        {'name': 'Tea', 'category': 'Beverages', 'base_price': 200},
        {'name': 'Coffee', 'category': 'Beverages', 'base_price': 300},
        {'name': 'Milk', 'category': 'Dairy', 'base_price': 60},
        {'name': 'Bread', 'category': 'Bakery', 'base_price': 30},
        {'name': 'Eggs', 'category': 'Dairy', 'base_price': 80},
        {'name': 'Onions', 'category': 'Vegetables', 'base_price': 40},
        {'name': 'Potatoes', 'category': 'Vegetables', 'base_price': 35},
        {'name': 'Tomatoes', 'category': 'Vegetables', 'base_price': 50},
        {'name': 'Soap', 'category': 'Personal Care', 'base_price': 25},
        {'name': 'Shampoo', 'category': 'Personal Care', 'base_price': 150},
    ]
    
    for shopkeeper in shopkeepers:
        for i, template in enumerate(product_templates[:count_per_shop]):
            # Vary price slightly per shop
            price = template['base_price'] * random.uniform(0.9, 1.1)
            
            product = Product(
                name=template['name'],
                category=template['category'],
                price=round(price, 2),
                stock_quantity=random.randint(0, 100),
                shopkeeper_id=shopkeeper,
                description=f"{template['name']} - {template['category']}"
            )
            product.save()
            products.append(product)
            logger.info(f"Created product: {product.name} for {shopkeeper.name}")
    
    return products


def seed_transactions(shopkeepers, customers, products, count=150):
    """Seed transactions"""
    transactions = []
    transaction_types = ['sale', 'credit', 'repay']
    
    for i in range(count):
        shopkeeper = random.choice(shopkeepers)
        customer = random.choice(customers)
        transaction_type = random.choice(transaction_types)
        
        # Random date in last 90 days
        timestamp = datetime.utcnow() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        
        if transaction_type == 'sale':
            # Pick a random product from this shopkeeper
            shop_products = [p for p in products if str(p.shopkeeper_id.id) == str(shopkeeper.id)]
            if shop_products:
                product = random.choice(shop_products)
                amount = product.price * random.randint(1, 5)
            else:
                product = None
                amount = random.uniform(50, 500)
        else:
            product = None
            amount = random.uniform(100, 1000)
        
        transaction = Transaction(
            type=transaction_type,
            amount=round(amount, 2),
            shopkeeper_id=shopkeeper,
            customer_id=customer,
            product_id=product,
            timestamp=timestamp,
            status=random.choice(['pending', 'verified', 'completed']),
            notes=f"Sample transaction {i+1}"
        )
        
        # Some transactions have blockchain records
        if transaction.status == 'verified' and random.random() > 0.5:
            transaction.blockchain_tx_id = f"0x{'0' * 64}"
            transaction.blockchain_block_number = random.randint(1000000, 2000000)
        
        transaction.save()
        transactions.append(transaction)
        
        if (i + 1) % 50 == 0:
            logger.info(f"Created {i+1} transactions")
    
    logger.info(f"Created {len(transactions)} transactions")
    return transactions


def seed_cooperatives(shopkeepers, count=3):
    """Seed cooperatives"""
    cooperatives = []
    
    coop_names = [
        {'name': 'Mumbai Central Cooperative', 'split': 10.0},
        {'name': 'Delhi Market Cooperative', 'split': 15.0},
        {'name': 'Bangalore Retailers Union', 'split': 12.5},
    ]
    
    for i, coop_data in enumerate(coop_names[:count]):
        # Assign 2-3 members per cooperative
        members = random.sample(shopkeepers, min(3, len(shopkeepers)))
        
        # Check if cooperative already exists
        existing_coop = Cooperative.objects(name=coop_data['name']).first()
        if existing_coop:
            logger.info(f"Cooperative {coop_data['name']} already exists, updating is_active")
            existing_coop.is_active = True
            existing_coop.members = members
            existing_coop.save()
            cooperatives.append(existing_coop)
        else:
            cooperative = Cooperative(
                name=coop_data['name'],
                description=f"Cooperative for {coop_data['name']}",
                revenue_split_percent=coop_data['split'],
                members=members,
                is_active=True,  # Explicitly set to True
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 180))
            )
            cooperative.save()
            cooperatives.append(cooperative)
            logger.info(f"Created cooperative: {cooperative.name} with {len(members)} members")
    
    return cooperatives


def seed_all():
    """Seed all data"""
    logger.info("Starting database seeding...")
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    # Clear existing data (optional - comment out to keep existing data)
    # logger.warning("Clearing existing data...")
    # Transaction.objects.delete()
    # Product.objects.delete()
    # Cooperative.objects.delete()
    # Customer.objects.delete()
    # Shopkeeper.objects.delete()
    
    # Seed data - Increased to 30 stores for better map coverage
    shopkeepers = seed_shopkeepers(30)
    customers = seed_customers(25)
    products = seed_products(shopkeepers, 12)
    transactions = seed_transactions(shopkeepers, customers, products, 150)
    cooperatives = seed_cooperatives(shopkeepers, 3)
    
    logger.info("✅ Database seeding completed!")
    logger.info(f"  - Shopkeepers: {len(shopkeepers)}")
    logger.info(f"  - Customers: {len(customers)}")
    logger.info(f"  - Products: {len(products)}")
    logger.info(f"  - Transactions: {len(transactions)}")
    logger.info(f"  - Cooperatives: {len(cooperatives)}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    seed_all()

