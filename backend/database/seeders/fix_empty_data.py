"""
Fix empty blockchain logs and cooperatives
This script ensures there's data for testing
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timedelta
import random
from database.models import Shopkeeper, Customer, Transaction, Cooperative
from mongoengine import connect
from config import Config
import logging

logger = logging.getLogger(__name__)


def fix_cooperatives():
    """Ensure cooperatives exist and are active"""
    logger.info("Checking cooperatives...")
    
    cooperatives = Cooperative.objects()
    logger.info(f"Found {cooperatives.count()} cooperatives in database")
    
    if cooperatives.count() == 0:
        logger.info("No cooperatives found. Creating sample cooperatives...")
        
        # Get some shopkeepers
        shopkeepers = list(Shopkeeper.objects()[:8])
        if len(shopkeepers) < 2:
            logger.warning("Not enough shopkeepers to create cooperatives. Please run seed_data.py first.")
            return
        
        coop_names = [
            {'name': 'Mumbai Central Cooperative', 'split': 10.0},
            {'name': 'Delhi Market Cooperative', 'split': 15.0},
            {'name': 'Bangalore Retailers Union', 'split': 12.5},
        ]
        
        for i, coop_data in enumerate(coop_names):
            # Assign 2-3 members per cooperative
            members = random.sample(shopkeepers, min(3, len(shopkeepers)))
            
            cooperative = Cooperative(
                name=coop_data['name'],
                description=f"Cooperative for {coop_data['name']}",
                revenue_split_percent=coop_data['split'],
                members=members,
                is_active=True,  # Explicitly set to True
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 180))
            )
            cooperative.save()
            logger.info(f"✅ Created cooperative: {cooperative.name} with {len(members)} members")
    else:
        # Ensure all cooperatives are active
        inactive = Cooperative.objects(is_active=False)
        if inactive.count() > 0:
            logger.info(f"Activating {inactive.count()} inactive cooperatives...")
            inactive.update(set__is_active=True)
            logger.info("✅ All cooperatives are now active")
        else:
            logger.info("✅ All cooperatives are already active")


def fix_blockchain_logs():
    """Add blockchain_tx_id to more transactions for testing"""
    logger.info("Checking blockchain logs...")
    
    # Count transactions with blockchain_tx_id
    with_blockchain = Transaction.objects(blockchain_tx_id__exists=True).count()
    total_transactions = Transaction.objects().count()
    
    logger.info(f"Found {with_blockchain} transactions with blockchain_tx_id out of {total_transactions} total")
    
    if with_blockchain < 10:
        logger.info("Adding blockchain_tx_id to more transactions for testing...")
        
        # Get verified transactions without blockchain_tx_id
        verified_transactions = Transaction.objects(
            status='verified',
            blockchain_tx_id__exists=False
        )[:50]  # Update up to 50 transactions
        
        count = 0
        for transaction in verified_transactions:
            # Generate a fake but realistic blockchain transaction hash
            hex_chars = '0123456789abcdef'
            fake_hash = '0x' + ''.join(random.choice(hex_chars) for _ in range(64))
            transaction.blockchain_tx_id = fake_hash
            transaction.blockchain_block_number = random.randint(1000000, 2000000)
            transaction.save()
            count += 1
        
        logger.info(f"✅ Added blockchain_tx_id to {count} transactions")
        
        # Also add to some pending transactions that should be verified
        pending_transactions = Transaction.objects(
            status='pending',
            blockchain_tx_id__exists=False
        )[:20]
        
        count2 = 0
        for transaction in pending_transactions:
            # Mark as verified and add blockchain info
            hex_chars = '0123456789abcdef'
            fake_hash = '0x' + ''.join(random.choice(hex_chars) for _ in range(64))
            transaction.status = 'verified'
            transaction.blockchain_tx_id = fake_hash
            transaction.blockchain_block_number = random.randint(1000000, 2000000)
            transaction.save()
            count2 += 1
        
        logger.info(f"✅ Verified and added blockchain_tx_id to {count2} pending transactions")
        
        final_count = Transaction.objects(blockchain_tx_id__exists=True).count()
        logger.info(f"✅ Total transactions with blockchain_tx_id: {final_count}")
    else:
        logger.info("✅ Sufficient blockchain logs exist")


def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Fixing Empty Data - Cooperatives and Blockchain Logs")
    logger.info("=" * 60)
    
    # Connect to database
    connect(
        db=Config.MONGODB_DB_NAME,
        host=Config.MONGODB_URI,
        alias='default'
    )
    
    # Fix cooperatives
    logger.info("\n1. Fixing Cooperatives...")
    fix_cooperatives()
    
    # Fix blockchain logs
    logger.info("\n2. Fixing Blockchain Logs...")
    fix_blockchain_logs()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Done! Refresh your frontend to see the data.")
    logger.info("=" * 60)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()

