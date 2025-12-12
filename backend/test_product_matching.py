"""
Test product matching
"""
import os
from dotenv import load_dotenv
from mongoengine import connect
from config import config
from services.grocery.grocery_service import get_products_for_shopkeeper, match_product_name
from database.models import Shopkeeper

# Load environment variables
load_dotenv()

# Connect to MongoDB
cfg = config['default']
connect(
    db=cfg.MONGODB_DB_NAME,
    host=cfg.MONGODB_URI,
    alias='default'
)

shopkeeper = Shopkeeper.objects.first()
if shopkeeper:
    print(f'Testing product matching for: {shopkeeper.name}\n')
    
    # Test matching
    test_names = ['rice', 'sugar', 'salt', 'Rice', 'Sugar', 'Salt', 'cooking oil', 'milk']
    for name in test_names:
        product = match_product_name(name, str(shopkeeper.id))
        if product:
            print(f'✅ "{name}" → Matched: {product.name} (₹{product.price})')
        else:
            print(f'❌ "{name}" → No match')
    
    print(f'\n📦 Total products available: {get_products_for_shopkeeper(str(shopkeeper.id)).__len__()}')
else:
    print('No shopkeeper found')

