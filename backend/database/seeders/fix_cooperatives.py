"""
Fix existing cooperatives - set is_active=True for all cooperatives
"""
import sys
from pathlib import Path

# Add parent directory to path so imports work when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import Cooperative
from mongoengine import connect
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_cooperatives():
    """Set is_active=True for all existing cooperatives"""
    logger.info("Connecting to database...")
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    # Get all cooperatives
    cooperatives = Cooperative.objects()
    total = cooperatives.count()
    
    logger.info(f"Found {total} cooperatives")
    
    # Update all cooperatives to is_active=True
    updated = 0
    for coop in cooperatives:
        if coop.is_active != True:
            coop.is_active = True
            coop.save()
            updated += 1
            logger.info(f"Updated cooperative: {coop.name} (is_active=True)")
        else:
            logger.info(f"Cooperative {coop.name} already has is_active=True")
    
    logger.info(f"✅ Fixed {updated} cooperatives (total: {total})")
    
    # Verify
    active_count = Cooperative.objects(is_active=True).count()
    logger.info(f"✅ Active cooperatives: {active_count}")


if __name__ == '__main__':
    fix_cooperatives()

