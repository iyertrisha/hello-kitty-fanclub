"""
Update existing shopkeeper locations to Delhi area
Run this if you have existing shopkeepers that need location updates
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import Shopkeeper, Location
from mongoengine import connect
from config import Config
import logging
import random

logger = logging.getLogger(__name__)


# Delhi area coordinates with variations
delhi_locations = [
    {'lat': 28.6300, 'lng': 77.2170, 'area': 'Connaught Place'},
    {'lat': 28.6500, 'lng': 77.1950, 'area': 'Karol Bagh'},
    {'lat': 28.5680, 'lng': 77.2430, 'area': 'Lajpat Nagar'},
    {'lat': 28.6300, 'lng': 77.0880, 'area': 'Janakpuri'},
    {'lat': 28.7400, 'lng': 77.1200, 'area': 'Rohini'},
    {'lat': 28.5900, 'lng': 77.0460, 'area': 'Dwarka'},
    {'lat': 28.5240, 'lng': 77.2060, 'area': 'Saket'},
    {'lat': 28.6510, 'lng': 77.2310, 'area': 'Chandni Chowk'},
]


def update_shopkeeper_locations():
    """Update all shopkeepers to Delhi area locations"""
    logger.info("Starting shopkeeper location update...")
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    shopkeepers = Shopkeeper.objects()
    logger.info(f"Found {shopkeepers.count()} shopkeepers")
    
    updated_count = 0
    for shopkeeper in shopkeepers:
        # Check if location exists and is not in Delhi area
        needs_update = False
        if not shopkeeper.location:
            needs_update = True
            logger.info(f"Shopkeeper {shopkeeper.name} has no location")
        elif shopkeeper.location.latitude < 28.0 or shopkeeper.location.latitude > 29.0:
            needs_update = True
            logger.info(f"Shopkeeper {shopkeeper.name} is not in Delhi area (lat: {shopkeeper.location.latitude})")
        
        if needs_update:
            # Pick a random Delhi location
            loc = random.choice(delhi_locations)
            shopkeeper.location = Location(
                latitude=loc['lat'] + random.uniform(-0.02, 0.02),
                longitude=loc['lng'] + random.uniform(-0.02, 0.02),
                address=f"{shopkeeper.address or shopkeeper.name}, {loc['area']}, Delhi"
            )
            shopkeeper.save()
            updated_count += 1
            logger.info(f"Updated {shopkeeper.name} to {loc['area']}, Delhi")
        else:
            logger.info(f"Shopkeeper {shopkeeper.name} already in Delhi area, skipping")
    
    logger.info(f"✅ Updated {updated_count} shopkeeper locations to Delhi area")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    update_shopkeeper_locations()

