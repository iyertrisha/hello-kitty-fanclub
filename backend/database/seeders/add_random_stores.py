"""
Quick script to add random stores to the database for supplier portal map testing
"""
import sys
from pathlib import Path

# Add parent directory to path so imports work when run directly
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import datetime, timedelta
import random
import importlib.util

# Import models directly from file to avoid Flask dependency in __init__.py
models_path = backend_dir / 'database' / 'models.py'
spec = importlib.util.spec_from_file_location('models', models_path)
models_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_module)
Shopkeeper = models_module.Shopkeeper
Location = models_module.Location

from mongoengine import connect
from config import Config
import logging

logger = logging.getLogger(__name__)

# Delhi area locations for random store placement
DELHI_LOCATIONS = [
    {'name': 'Connaught Place', 'lat': 28.6300, 'lng': 77.2170},
    {'name': 'Karol Bagh', 'lat': 28.6500, 'lng': 77.1950},
    {'name': 'Lajpat Nagar', 'lat': 28.5680, 'lng': 77.2430},
    {'name': 'Janakpuri', 'lat': 28.6300, 'lng': 77.0880},
    {'name': 'Rohini', 'lat': 28.7400, 'lng': 77.1200},
    {'name': 'Dwarka', 'lat': 28.5900, 'lng': 77.0460},
    {'name': 'Saket', 'lat': 28.5240, 'lng': 77.2060},
    {'name': 'Chandni Chowk', 'lat': 28.6510, 'lng': 77.2310},
    {'name': 'Paharganj', 'lat': 28.6450, 'lng': 77.2100},
    {'name': 'Rajouri Garden', 'lat': 28.6500, 'lng': 77.1200},
    {'name': 'Model Town', 'lat': 28.7100, 'lng': 77.2000},
    {'name': 'Pitampura', 'lat': 28.6900, 'lng': 77.1400},
    {'name': 'Greater Kailash', 'lat': 28.5500, 'lng': 77.2400},
    {'name': 'Vasant Kunj', 'lat': 28.5300, 'lng': 77.1500},
    {'name': 'Shahdara', 'lat': 28.6800, 'lng': 77.2800},
    {'name': 'Patparganj', 'lat': 28.6200, 'lng': 77.3000},
    {'name': 'Paschim Vihar', 'lat': 28.6800, 'lng': 77.1000},
    {'name': 'Rajendra Place', 'lat': 28.6400, 'lng': 77.1900},
    {'name': 'Kirti Nagar', 'lat': 28.6500, 'lng': 77.1600},
    {'name': 'Nehru Place', 'lat': 28.5500, 'lng': 77.2500},
    {'name': 'Laxmi Nagar', 'lat': 28.6400, 'lng': 77.2800},
    {'name': 'Mayur Vihar', 'lat': 28.6000, 'lng': 77.3000},
    {'name': 'Noida Sector 15', 'lat': 28.5800, 'lng': 77.3200},
    {'name': 'Gurgaon Sector 18', 'lat': 28.4300, 'lng': 77.0900},
    {'name': 'Gurgaon Sector 29', 'lat': 28.4500, 'lng': 77.0800},
]

STORE_NAMES = [
    'Kirana Store', 'Grocery', 'General Store', 'Provision Store', 
    'Super Mart', 'Daily Needs', 'Quick Mart', 'Corner Store',
    'Mini Market', 'Neighborhood Store', 'Family Store', 'City Mart'
]

OWNER_NAMES = [
    'Rajesh', 'Priya', 'Amit', 'Sunita', 'Vikram', 'Meera', 'Kumar', 
    'Lakshmi', 'Ravi', 'Anita', 'Suresh', 'Kavita', 'Mohan', 'Deepa', 
    'Nitin', 'Sharma', 'Patel', 'Gupta', 'Singh', 'Verma', 'Yadav', 
    'Reddy', 'Rao', 'Jain', 'Agarwal', 'Malhotra', 'Khanna', 'Bansal'
]


def add_random_stores(count=20):
    """Add random stores with valid locations in Delhi area"""
    logger.info(f"Adding {count} random stores...")
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    created_count = 0
    skipped_count = 0
    
    for i in range(count):
        # Pick random location and name
        location_data = random.choice(DELHI_LOCATIONS)
        owner_name = random.choice(OWNER_NAMES)
        store_type = random.choice(STORE_NAMES)
        store_name = f"{owner_name} {store_type}"
        
        # Generate unique wallet address
        wallet_hex = hex(random.randint(0, 2**160 - 1))[2:].zfill(40)
        wallet_address = f"0x{wallet_hex}"
        
        # Check if wallet already exists
        if Shopkeeper.objects(wallet_address=wallet_address).first():
            logger.warning(f"Wallet {wallet_address} already exists, generating new one...")
            wallet_hex = hex(random.randint(0, 2**160 - 1))[2:].zfill(40)
            wallet_address = f"0x{wallet_hex}"
        
        # Generate phone number
        phone = f"+9198765{random.randint(10000, 99999)}"
        
        # Check if phone already exists
        if Shopkeeper.objects(phone=phone).first():
            phone = f"+9198765{random.randint(10000, 99999)}"
        
        # Create shopkeeper
        shopkeeper = Shopkeeper(
            name=store_name,
            address=f"Shop {random.randint(1, 999)}, {location_data['name']}, Delhi",
            phone=phone,
            email=f"store{random.randint(1000, 9999)}@example.com",
            wallet_address=wallet_address,
            blockchain_address=wallet_address,
            credit_score=random.randint(400, 800),
            registered_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
            is_active=True
        )
        
        # Add location with slight random variation
        shopkeeper.location = Location(
            latitude=location_data['lat'] + random.uniform(-0.015, 0.015),
            longitude=location_data['lng'] + random.uniform(-0.015, 0.015),
            address=shopkeeper.address
        )
        
        try:
            shopkeeper.save()
            created_count += 1
            logger.info(f"✅ Created: {store_name} at {location_data['name']}")
        except Exception as e:
            skipped_count += 1
            logger.warning(f"⚠️  Skipped {store_name}: {e}")
    
    logger.info(f"\n✅ Completed! Created {created_count} stores, skipped {skipped_count}")
    return created_count


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Add random stores to database')
    parser.add_argument('--count', type=int, default=20, help='Number of stores to add (default: 20)')
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    add_random_stores(args.count)

