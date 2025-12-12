"""
Quick script to check cooperatives in the database
"""
import sys
from pathlib import Path

# Add parent directory to path so imports work when run directly
sys.path.insert(0, str(Path(__file__).parent))

from database.models import Cooperative
from mongoengine import connect
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_cooperatives():
    """Check cooperatives in database"""
    logger.info("Connecting to database...")
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    # Get all cooperatives (no filter)
    all_cooperatives = Cooperative.objects()
    total = all_cooperatives.count()
    
    # Get active cooperatives
    active_cooperatives = Cooperative.objects(is_active=True)
    active_count = active_cooperatives.count()
    
    # Get cooperatives with is_active=None or not set
    from mongoengine import Q
    inactive_or_none = Cooperative.objects(Q(is_active=False) | Q(is_active__exists=False) | Q(is_active=None))
    inactive_count = inactive_or_none.count()
    
    print("\n" + "="*60)
    print("COOPERATIVES DATABASE CHECK")
    print("="*60)
    print(f"Total Cooperatives: {total}")
    print(f"Active (is_active=True): {active_count}")
    print(f"Inactive/None/Not Set: {inactive_count}")
    print("="*60)
    
    if total > 0:
        print("\n📋 All Cooperatives:")
        print("-" * 60)
        for i, coop in enumerate(all_cooperatives, 1):
            print(f"\n{i}. {coop.name}")
            print(f"   ID: {coop.id}")
            print(f"   is_active: {coop.is_active}")
            print(f"   Members: {len(coop.members)}")
            print(f"   Revenue Split: {coop.revenue_split_percent}%")
            print(f"   Created: {coop.created_at}")
            if coop.blockchain_coop_id:
                print(f"   Blockchain ID: {coop.blockchain_coop_id}")
    else:
        print("\n⚠️  No cooperatives found in database!")
        print("   Run: python database/seeders/seed_data.py")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    check_cooperatives()

