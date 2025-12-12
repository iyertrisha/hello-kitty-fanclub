"""
Script to add test products to the database
"""
import os
from dotenv import load_dotenv
from mongoengine import connect
from config import config
from database.models import Shopkeeper, Product

# Load environment variables
load_dotenv()

# Connect to MongoDB
cfg = config['default']
connect(
    db=cfg.MONGODB_DB_NAME,
    host=cfg.MONGODB_URI,
    alias='default'
)
print(f'✅ Connected to MongoDB: {cfg.MONGODB_DB_NAME}\n')

def main():
    # Get first shopkeeper
    shopkeeper = Shopkeeper.objects.first()
    
    if not shopkeeper:
        print('❌ No shopkeeper found. Please register one first.')
        print('Run: python -c "from services.shopkeeper import register_shopkeeper; register_shopkeeper({\'name\': \'Test Shop\', \'address\': \'123 Main St\', \'phone\': \'+916387905059\', \'wallet_address\': \'0x1234567890123456789012345678901234567890\'})"')
        return
    
    print(f'✅ Shopkeeper found: {shopkeeper.name} (ID: {shopkeeper.id})')
    
    # Check existing products
    existing_products = Product.objects(shopkeeper_id=shopkeeper)
    print(f'📦 Existing products: {existing_products.count()}')
    
    if existing_products.count() > 0:
        print('\nCurrent products:')
        for p in existing_products:
            print(f'  - {p.name} (₹{p.price}, Stock: {p.stock_quantity})')
    
    # Products to add
    products_to_add = [
        {'name': 'Rice', 'category': 'Grains', 'price': 50.00, 'stock_quantity': 100, 'description': 'Basmati Rice'},
        {'name': 'Sugar', 'category': 'Essentials', 'price': 45.00, 'stock_quantity': 50, 'description': 'White Sugar'},
        {'name': 'Salt', 'category': 'Essentials', 'price': 20.00, 'stock_quantity': 30, 'description': 'Iodized Salt'},
        {'name': 'Cooking Oil', 'category': 'Essentials', 'price': 120.00, 'stock_quantity': 40, 'description': 'Sunflower Oil'},
        {'name': 'Milk', 'category': 'Dairy', 'price': 60.00, 'stock_quantity': 25, 'description': 'Fresh Milk'},
        {'name': 'Bread', 'category': 'Bakery', 'price': 30.00, 'stock_quantity': 20, 'description': 'White Bread'},
        {'name': 'Eggs', 'category': 'Dairy', 'price': 80.00, 'stock_quantity': 15, 'description': 'Farm Eggs'},
        {'name': 'Onions', 'category': 'Vegetables', 'price': 40.00, 'stock_quantity': 30, 'description': 'Fresh Onions'},
        {'name': 'Potatoes', 'category': 'Vegetables', 'price': 35.00, 'stock_quantity': 25, 'description': 'Fresh Potatoes'},
        {'name': 'Tomatoes', 'category': 'Vegetables', 'price': 50.00, 'stock_quantity': 20, 'description': 'Fresh Tomatoes'},
    ]
    
    print(f'\n➕ Adding {len(products_to_add)} products...\n')
    
    added = 0
    skipped = 0
    
    for p_data in products_to_add:
        # Check if product already exists
        existing = Product.objects(shopkeeper_id=shopkeeper, name=p_data['name']).first()
        if not existing:
            product = Product(shopkeeper_id=shopkeeper, **p_data)
            product.save()
            print(f'✅ Added: {p_data["name"]} - ₹{p_data["price"]} (Stock: {p_data["stock_quantity"]})')
            added += 1
        else:
            print(f'ℹ️  Already exists: {p_data["name"]} - ₹{existing.price}')
            skipped += 1
    
    print(f'\n📊 Summary:')
    print(f'  ✅ Added: {added} new products')
    print(f'  ℹ️  Skipped: {skipped} existing products')
    print(f'  📦 Total products: {Product.objects(shopkeeper_id=shopkeeper).count()}')
    print(f'\n✅ Done! You can now test grocery ordering.')

if __name__ == '__main__':
    main()

