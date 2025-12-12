"""
Seed products for shopkeeper
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mongoengine import connect
from database.models import Shopkeeper, Product
from bson.errors import InvalidId
from bson import ObjectId
from config import Config

# Connect to database
try:
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    print(f"✅ Connected to MongoDB: {Config.MONGODB_DB_NAME}")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    sys.exit(1)

# Shopkeeper ID
shopkeeper_id = "693c53f8b19c3ce69fe57773"

try:
    # Validate ObjectId
    ObjectId(shopkeeper_id)
except InvalidId:
    print(f"❌ Invalid shopkeeper ID format: {shopkeeper_id}")
    sys.exit(1)

# Get shopkeeper
try:
    shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    print(f"✅ Found shopkeeper: {shopkeeper.name} (Phone: {shopkeeper.phone})")
except Shopkeeper.DoesNotExist:
    print(f"❌ Shopkeeper with ID {shopkeeper_id} not found")
    sys.exit(1)

# Products to add
products = [
    {'name': 'Rice', 'category': 'Grains', 'price': 50.00, 'stock_quantity': 100},
    {'name': 'Sugar', 'category': 'Essentials', 'price': 45.00, 'stock_quantity': 50},
    {'name': 'Salt', 'category': 'Essentials', 'price': 20.00, 'stock_quantity': 30},
    {'name': 'Cooking Oil', 'category': 'Essentials', 'price': 120.00, 'stock_quantity': 40},
    {'name': 'Milk', 'category': 'Dairy', 'price': 60.00, 'stock_quantity': 25},
    {'name': 'Bread', 'category': 'Bakery', 'price': 30.00, 'stock_quantity': 20},
    {'name': 'Eggs', 'category': 'Dairy', 'price': 80.00, 'stock_quantity': 15},
    {'name': 'Onions', 'category': 'Vegetables', 'price': 40.00, 'stock_quantity': 30},
    {'name': 'Potatoes', 'category': 'Vegetables', 'price': 35.00, 'stock_quantity': 25},
    {'name': 'Tomatoes', 'category': 'Vegetables', 'price': 50.00, 'stock_quantity': 20}
]

print(f"\n📦 Adding {len(products)} products to {shopkeeper.name}...\n")

added_count = 0
for product_data in products:
    try:
        # Check if product already exists
        existing = Product.objects(
            shopkeeper_id=shopkeeper,
            name=product_data['name']
        ).first()
        
        if existing:
            print(f"⏭️  Skipped: {product_data['name']} (already exists)")
            continue
        
        # Create product
        product = Product(
            shopkeeper_id=shopkeeper,
            name=product_data['name'],
            category=product_data['category'],
            price=product_data['price'],
            stock_quantity=product_data['stock_quantity'],
            description=f"{product_data['name']} - {product_data['category']}"
        )
        product.save()
        print(f"✅ Added: {product_data['name']} (₹{product_data['price']}, Stock: {product_data['stock_quantity']})")
        added_count += 1
    except Exception as e:
        print(f"❌ Failed: {product_data['name']} - {str(e)}")

print(f"\n✅ Successfully added {added_count} products!")
print(f"📊 Total products for {shopkeeper.name}: {Product.objects(shopkeeper_id=shopkeeper).count()}")

