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
from database.models import Shopkeeper, Customer, Product, Transaction, Cooperative, Location
from mongoengine import connect
from config import Config
import logging

logger = logging.getLogger(__name__)


def seed_shopkeepers(count=8):
    """Seed shopkeepers"""
    shopkeepers = []
    
    # Sample shopkeeper data
    shopkeeper_data = [
        {'name': 'Rajesh Kirana Store', 'address': '123 Main Street, Mumbai', 'phone': '+919876543210', 'wallet': '0x1111111111111111111111111111111111111111'},
        {'name': 'Priya Grocery', 'address': '456 Market Road, Delhi', 'phone': '+919876543211', 'wallet': '0x2222222222222222222222222222222222222222'},
        {'name': 'Amit General Store', 'address': '789 Commercial Area, Bangalore', 'phone': '+919876543212', 'wallet': '0x3333333333333333333333333333333333333333'},
        {'name': 'Sunita Provision Store', 'address': '321 Residential Colony, Pune', 'phone': '+919876543213', 'wallet': '0x4444444444444444444444444444444444444444'},
        {'name': 'Vikram Kirana', 'address': '654 High Street, Hyderabad', 'phone': '+919876543214', 'wallet': '0x5555555555555555555555555555555555555555'},
        {'name': 'Meera Groceries', 'address': '987 Shopping Complex, Chennai', 'phone': '+919876543215', 'wallet': '0x6666666666666666666666666666666666666666'},
        {'name': 'Kumar Store', 'address': '147 Village Road, Ahmedabad', 'phone': '+919876543216', 'wallet': '0x7777777777777777777777777777777777777777'},
        {'name': 'Lakshmi Kirana', 'address': '258 Town Center, Kolkata', 'phone': '+919876543217', 'wallet': '0x8888888888888888888888888888888888888888'},
    ]
    
    for i, data in enumerate(shopkeeper_data[:count]):
        # Check if already exists
        if Shopkeeper.objects(wallet_address=data['wallet']).first():
            logger.info(f"Shopkeeper {data['name']} already exists, skipping")
            shopkeeper = Shopkeeper.objects(wallet_address=data['wallet']).first()
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
            
            # Add location (Mumbai area coordinates)
            shopkeeper.location = Location(
                latitude=19.0760 + random.uniform(-0.1, 0.1),
                longitude=72.8777 + random.uniform(-0.1, 0.1),
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
    
    # Seed data
    shopkeepers = seed_shopkeepers(8)
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

