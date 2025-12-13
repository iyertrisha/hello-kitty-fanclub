"""
Cooperative service - Business logic for cooperatives
"""
from database.models import Cooperative, Shopkeeper, BulkOrder
from api.middleware.error_handler import NotFoundError, ValidationError
import logging
import sys
from pathlib import Path

# Add blockchain utils to path
blockchain_path = Path(__file__).parent.parent.parent / 'blockchain' / 'utils'
sys.path.insert(0, str(blockchain_path))

try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'blockchain'))
    from utils.contract_service import BlockchainService
    from config import BlockchainConfig
except ImportError:
    BlockchainService = None
    logger = logging.getLogger(__name__)
    logger.warning("Blockchain service not available")

logger = logging.getLogger(__name__)


def get_cooperatives():
    """
    Get all cooperatives
    
    Returns:
        list: List of cooperative dictionaries
    """
    # Get all cooperatives (exclude only those explicitly set to False)
    # This includes: is_active=True, is_active=None, and is_active not set
    # Simple approach: get all and filter out False
    all_coops = Cooperative.objects()
    cooperatives = [c for c in all_coops if getattr(c, 'is_active', True) != False]
    
    logger.info(f"Found {len(cooperatives)} cooperatives (out of {all_coops.count()} total)")
    
    result = []
    for coop in cooperatives:
        # Include members data for frontend
        members = []
        if coop.members:
            for member in coop.members:
                try:
                    members.append({
                        'id': str(member.id),
                        'name': member.name,
                        'address': member.address or '',
                    })
                except Exception as e:
                    logger.warning(f"Error processing member {member}: {e}")
                    continue
        
        result.append({
            'id': str(coop.id),
            'name': coop.name,
            'description': coop.description,
            'revenue_split_percent': coop.revenue_split_percent,
            'revenue_split': coop.revenue_split_percent,  # Alias for frontend
            'created_at': coop.created_at.isoformat() if coop.created_at else None,
            'member_count': len(coop.members),
            'members': members,  # Include members for frontend
            'blockchain_coop_id': coop.blockchain_coop_id,
            'is_active': coop.is_active
        })
    
    return result


def create_cooperative(data):
    """
    Create cooperative (calls blockchain)
    
    Args:
        data: Cooperative data dictionary
    
    Returns:
        Cooperative: Created cooperative object
    """
    # Validate required fields
    required_fields = ['name', 'revenue_split_percent']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate revenue split percent
    if not 0 <= data['revenue_split_percent'] <= 100:
        raise ValidationError("Revenue split percent must be between 0 and 100")
    
    # Create cooperative in database - explicitly set is_active=True
    cooperative = Cooperative(
        name=data['name'],
        description=data.get('description'),
        revenue_split_percent=data['revenue_split_percent'],
        is_active=True
    )
    
    # Save first to generate ID (needed for blockchain)
    cooperative.save()
    
    # Create on blockchain if service available
    if BlockchainService and BlockchainConfig.CONTRACT_ADDRESS:
        try:
            blockchain_service = BlockchainService(
                rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL,
                private_key=BlockchainConfig.PRIVATE_KEY,
                contract_address=BlockchainConfig.CONTRACT_ADDRESS
            )
            
            # Generate cooperative ID (use database ID as coop_id)
            coop_id = str(cooperative.id)
            terms_hash = "0x" + "0" * 64  # Placeholder hash for terms
            
            tx_hash = blockchain_service.create_cooperative(
                coop_id=coop_id,
                name=data['name'],
                terms_hash=terms_hash,
                split_percent=int(data['revenue_split_percent'] * 100)  # Convert to basis points
            )
            
            cooperative.blockchain_coop_id = coop_id
            cooperative.save()  # Save again with blockchain ID
            logger.info(f"Created cooperative {coop_id} on blockchain: {tx_hash}")
        except Exception as e:
            logger.error(f"Error creating cooperative on blockchain: {e}")
            # Continue without blockchain registration
    
    logger.info(f"Created cooperative {cooperative.id}")
    
    return cooperative


def join_cooperative(coop_id, shopkeeper_id):
    """
    Join cooperative
    
    Args:
        coop_id: Cooperative ID
        shopkeeper_id: Shopkeeper ID
    
    Returns:
        Cooperative: Updated cooperative object
    """
    try:
        from bson.errors import InvalidId
        cooperative = Cooperative.objects.get(id=coop_id)
    except (Cooperative.DoesNotExist, InvalidId):
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    try:
        from bson.errors import InvalidId
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except (Shopkeeper.DoesNotExist, InvalidId):
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Check if already a member
    if shopkeeper in cooperative.members:
        raise ValidationError("Shopkeeper is already a member of this cooperative")
    
    # Add to members list
    cooperative.members.append(shopkeeper)
    
    # Join on blockchain if service available
    if BlockchainService and BlockchainConfig.CONTRACT_ADDRESS and cooperative.blockchain_coop_id:
        try:
            blockchain_service = BlockchainService(
                rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL,
                private_key=BlockchainConfig.PRIVATE_KEY,
                contract_address=BlockchainConfig.CONTRACT_ADDRESS
            )
            
            tx_hash = blockchain_service.join_cooperative(
                coop_id=cooperative.blockchain_coop_id,
                shop_address=shopkeeper.wallet_address
            )
            
            logger.info(f"Joined cooperative {coop_id} on blockchain: {tx_hash}")
        except Exception as e:
            logger.error(f"Error joining cooperative on blockchain: {e}")
            # Continue without blockchain registration
    
    cooperative.save()
    
    logger.info(f"Shopkeeper {shopkeeper_id} joined cooperative {coop_id}")
    
    return cooperative


def leave_cooperative(coop_id, shopkeeper_id):
    """
    Leave cooperative (remove shopkeeper from members)
    
    Args:
        coop_id: Cooperative ID
        shopkeeper_id: Shopkeeper ID
    
    Returns:
        Cooperative: Updated cooperative object
    """
    try:
        from bson.errors import InvalidId
        cooperative = Cooperative.objects.get(id=coop_id)
    except (Cooperative.DoesNotExist, InvalidId):
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    try:
        from bson.errors import InvalidId
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except (Shopkeeper.DoesNotExist, InvalidId):
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Check if shopkeeper is a member
    if shopkeeper not in cooperative.members:
        raise ValidationError("Shopkeeper is not a member of this cooperative")
    
    # Remove from members list
    cooperative.members.remove(shopkeeper)
    cooperative.save()
    
    logger.info(f"Shopkeeper {shopkeeper_id} left cooperative {coop_id}")
    
    return cooperative


def get_cooperative_members(coop_id):
    """
    Get cooperative members
    
    Args:
        coop_id: Cooperative ID
    
    Returns:
        list: List of shopkeeper dictionaries
    """
    try:
        cooperative = Cooperative.objects.get(id=coop_id)
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    result = []
    for shopkeeper in cooperative.members:
        result.append({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'address': shopkeeper.address,
            'phone': shopkeeper.phone,
            'wallet_address': shopkeeper.wallet_address
        })
    
    return result


def create_bulk_order(coop_id, order_data):
    """
    Create bulk order for cooperative
    
    Args:
        coop_id: Cooperative ID
        order_data: Order data dictionary
    
    Returns:
        BulkOrder: Created bulk order object
    """
    try:
        cooperative = Cooperative.objects.get(id=coop_id)
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    # Validate required fields
    required_fields = ['product_name', 'quantity', 'unit_price']
    for field in required_fields:
        if field not in order_data:
            raise ValidationError(f"Missing required field: {field}")
    
    total_amount = order_data['quantity'] * order_data['unit_price']
    
    bulk_order = BulkOrder(
        cooperative_id=coop_id,
        product_name=order_data['product_name'],
        quantity=order_data['quantity'],
        unit_price=order_data['unit_price'],
        total_amount=total_amount,
        order_details=order_data.get('order_details', {})
    )
    
    bulk_order.save()
    
    logger.info(f"Created bulk order {bulk_order.id} for cooperative {coop_id}")
    
    return bulk_order


def calculate_revenue_split(coop_id, total_revenue):
    """
    Calculate revenue split for cooperative members
    
    Args:
        coop_id: Cooperative ID
        total_revenue: Total revenue to split
    
    Returns:
        dict: Revenue split details
    """
    try:
        cooperative = Cooperative.objects.get(id=coop_id)
    except Cooperative.DoesNotExist:
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    if not cooperative.members:
        raise ValidationError("Cooperative has no members")
    
    # Calculate split per member (equal split for now)
    # In future, could use revenue_split_percent or other logic
    member_count = len(cooperative.members)
    split_per_member = total_revenue / member_count
    
    splits = []
    for shopkeeper in cooperative.members:
        splits.append({
            'shopkeeper_id': str(shopkeeper.id),
            'shopkeeper_name': shopkeeper.name,
            'wallet_address': shopkeeper.wallet_address,
            'amount': split_per_member
        })
    
    return {
        'cooperative_id': str(coop_id),
        'cooperative_name': cooperative.name,
        'total_revenue': total_revenue,
        'member_count': member_count,
        'splits': splits
    }


def delete_cooperative(coop_id):
    """
    Delete a cooperative
    
    Args:
        coop_id: Cooperative ID
    
    Returns:
        bool: True if deleted successfully
    """
    try:
        from bson.errors import InvalidId
        cooperative = Cooperative.objects.get(id=coop_id)
    except (Cooperative.DoesNotExist, InvalidId):
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    # Hard delete - remove from database
    cooperative.delete()
    
    logger.info(f"Deleted cooperative {coop_id}")
    
    return True


def update_cooperative(coop_id, data):
    """
    Update cooperative details
    
    Args:
        coop_id: Cooperative ID
        data: Dictionary of fields to update
    
    Returns:
        Cooperative: Updated cooperative object
    """
    try:
        from bson.errors import InvalidId
        cooperative = Cooperative.objects.get(id=coop_id)
    except (Cooperative.DoesNotExist, InvalidId):
        raise NotFoundError(f"Cooperative {coop_id} not found")
    
    # Update allowed fields
    allowed_fields = ['name', 'description', 'revenue_split_percent', 'is_active']
    for field in allowed_fields:
        if field in data:
            setattr(cooperative, field, data[field])
    
    cooperative.save()
    
    logger.info(f"Updated cooperative {coop_id}")
    
    return cooperative

