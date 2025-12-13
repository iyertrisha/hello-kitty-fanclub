"""
Transaction service - Business logic for transactions
"""
from datetime import datetime, timedelta
from database.models import Transaction, Shopkeeper, Customer, Product, PendingConfirmation
from api.middleware.error_handler import ValidationError, NotFoundError
from services.transaction.shopkeeper_history_helper import get_shopkeeper_history
from services.transaction.amount_utils import rupees_to_paise, paise_to_rupees
from services.transaction_verification import (
    TransactionVerificationService,
    VerificationStatus,
    get_verification_service
)
import logging
import sys
from pathlib import Path

# Add blockchain directory to path for imports
blockchain_path = Path(__file__).parent.parent.parent / 'blockchain'
sys.path.insert(0, str(blockchain_path))

try:
    from utils.contract_service import BlockchainService
    from config import BlockchainConfig
    BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    BlockchainService = None
    BlockchainConfig = None
    BLOCKCHAIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Blockchain service not available: {e}")

logger = logging.getLogger(__name__)

# Global blockchain service instance (initialized lazily)
_blockchain_service: BlockchainService = None


def get_blockchain_service() -> BlockchainService:
    """
    Initialize and return blockchain service instance with error handling.
    
    Returns:
        BlockchainService instance or None if initialization fails
    """
    global _blockchain_service
    
    if not BLOCKCHAIN_AVAILABLE or BlockchainService is None or BlockchainConfig is None:
        logger.warning("Blockchain service not available - transactions will be stored in MongoDB only")
        return None
    
    if _blockchain_service is not None:
        return _blockchain_service
    
    try:
        # Validate blockchain config
        BlockchainConfig.validate(require_contract=True)
        
        # Initialize blockchain service
        # FIXED: Use POLYGON_AMOY_RPC_URL instead of RPC_URL to match blockchain routes
        rpc_url = BlockchainConfig.POLYGON_AMOY_RPC_URL or BlockchainConfig.RPC_URL
        _blockchain_service = BlockchainService(
            rpc_url=rpc_url,
            private_key=BlockchainConfig.PRIVATE_KEY,
            contract_address=BlockchainConfig.CONTRACT_ADDRESS
        )
        
        logger.info("Blockchain service initialized successfully")
        return _blockchain_service
        
    except Exception as e:
        logger.error(f"Failed to initialize blockchain service: {e}. "
                     f"Transactions will be stored in MongoDB only.")
        # FIXED: Still return None but log as error, not warning
        return None


def create_transaction_with_verification(data):
    """
    Create a new transaction with verification and blockchain integration.
    
    This function:
    1. Generates shopkeeper history from MongoDB
    2. Calls verification service with transcript
    3. Creates transaction in MongoDB with verification status
    4. Writes to blockchain if verified
    5. Updates transaction with blockchain TX hash
    
    Args:
        data: Transaction data dictionary with optional 'transcript' field
    
    Returns:
        Transaction: Created transaction object with verification metadata
    """
    # Get shopkeeper and customer objects
    try:
        from bson.errors import InvalidId
        shopkeeper = Shopkeeper.objects.get(id=data['shopkeeper_id'])
        customer = Customer.objects.get(id=data['customer_id'])
    except (Shopkeeper.DoesNotExist, InvalidId):
        raise ValidationError("Shopkeeper not found")
    except (Customer.DoesNotExist, InvalidId):
        raise ValidationError("Customer not found")
    
    # Get product if provided
    product = None
    if data.get('product_id'):
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise ValidationError("Product not found")
    
    # Generate shopkeeper history for fraud detection
    shopkeeper_history = get_shopkeeper_history(str(data['shopkeeper_id']))
    
    # Prepare transaction data for verification
    transcript = data.get('transcript', '')
    amount_paise = int(rupees_to_paise(data['amount']))
    
    verification_data = {
        'transcript': transcript,
        'type': data['type'],
        'amount': amount_paise,
        'customer_id': str(data['customer_id']),
        'shopkeeper_id': str(data['shopkeeper_id']),
        'customer_confirmed': data.get('customer_confirmed', False),
        'shopkeeper_history': shopkeeper_history,
        'language': data.get('language', 'hi-IN')
    }
    
    # Initialize verification service with blockchain service
    blockchain_service = get_blockchain_service()
    verification_service = get_verification_service(blockchain_service)
    
    # Run verification based on transaction type
    if data['type'] == 'credit':
        verification_result = verification_service.verify_credit_transaction(verification_data)
    elif data['type'] == 'sale':
        verification_result = verification_service.verify_sales_transaction(verification_data)
    else:
        # For repay transactions, use credit verification logic
        verification_result = verification_service.verify_credit_transaction(verification_data)
    
    # Extract fraud check details
    fraud_check = verification_result.fraud_check or {}
    fraud_score = fraud_check.get('score', 0.0) * 100  # Convert to 0-100 scale
    fraud_risk_level = fraud_check.get('risk_level', 'low')
    
    # Create transaction in MongoDB
    transaction = Transaction(
        type=data['type'],
        amount=data['amount'],
        shopkeeper_id=shopkeeper,
        customer_id=customer,
        product_id=product,
        timestamp=data.get('timestamp', datetime.now()),
        status='verified',  # TEMPORARY: Default to verified for testing
        transcript=transcript,
        transcript_hash=verification_result.transcript_hash,
        verification_status=verification_result.status.value,
        fraud_score=fraud_score,
        fraud_risk_level=fraud_risk_level,
        verification_metadata={
            'storage_location': verification_result.storage_location.value,
            'fraud_check': fraud_check,
            'errors': verification_result.errors,
            'warnings': verification_result.warnings,
            'metadata': verification_result.metadata
        },
        notes=data.get('notes')
    )
    
    # Update status based on verification result
    # TEMPORARY: Force all transactions to 'verified' for testing
    transaction.status = 'verified'
    # if verification_result.status == VerificationStatus.VERIFIED:
    #     transaction.status = 'verified'
    # elif verification_result.status == VerificationStatus.FLAGGED:
    #     transaction.status = 'pending'  # Flagged transactions need review
    # elif verification_result.status == VerificationStatus.REJECTED:
    #     transaction.status = 'disputed'
    # # PENDING status keeps transaction as 'pending'
    
    transaction.save()
    
    # Write to blockchain if verified
    blockchain_result = None
    if verification_result.should_write_to_blockchain and blockchain_service:
        try:
            # Determine transaction type for blockchain (0=SALE, 1=CREDIT, 2=REPAY)
            tx_type_map = {'sale': 0, 'credit': 1, 'repay': 2}
            tx_type = tx_type_map.get(data['type'], 1)
            
            # Get shopkeeper's blockchain address
            shop_address = shopkeeper.wallet_address or shopkeeper.blockchain_address
            if not shop_address:
                logger.warning(f"Shopkeeper {shopkeeper.id} has no blockchain address")
            else:
                blockchain_result = blockchain_service.record_transaction(
                    voice_hash=verification_result.transcript_hash,
                    shop_address=shop_address,
                    amount=amount_paise,  # Blockchain expects paise/wei
                    tx_type=tx_type
                )
                
                if blockchain_result.get('success'):
                    transaction.blockchain_tx_id = blockchain_result['tx_hash']
                    transaction.blockchain_block_number = blockchain_result.get('block_number')
                    transaction.save()
                    logger.info(f"Transaction {transaction.id} written to blockchain: {blockchain_result['tx_hash']}")
                else:
                    logger.error(f"Failed to write transaction {transaction.id} to blockchain: "
                               f"{blockchain_result.get('error')}")
        except Exception as e:
            logger.error(f"Error writing transaction {transaction.id} to blockchain: {e}", exc_info=True)
    
    # Update customer statistics
    if data['type'] == 'sale':
        customer.total_purchases += data['amount']
    elif data['type'] == 'credit':
        customer.total_credits += data['amount']
        customer.credit_balance += data['amount']
    elif data['type'] == 'repay':
        customer.credit_balance -= data['amount']
        if customer.credit_balance < 0:
            customer.credit_balance = 0
    customer.save()
    
    logger.info(f"Created transaction {transaction.id} with verification: "
               f"status={verification_result.status.value}, "
               f"blockchain={verification_result.should_write_to_blockchain}")
    
    return transaction


def validate_transaction(data):
    """
    Validate transaction data against business rules
    
    Args:
        data: Transaction data dictionary
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['type', 'amount', 'shopkeeper_id', 'customer_id']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate transaction type
    if data['type'] not in ['sale', 'credit', 'repay']:
        return False, f"Invalid transaction type: {data['type']}"
    
    # Validate amount
    if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        return False, "Amount must be a positive number"
    
    # For sales transactions, validate product if provided
    if data['type'] == 'sale' and 'product_id' in data and data['product_id']:
        try:
            product = Product.objects.get(id=data['product_id'])
            # Check if product belongs to shopkeeper
            if str(product.shopkeeper_id.id) != str(data['shopkeeper_id']):
                return False, "Product does not belong to this shopkeeper"
            
            # Check price is within ±20% of catalog price
            catalog_price = product.price
            transaction_price = data.get('price', data['amount'])
            price_diff_percent = abs(transaction_price - catalog_price) / catalog_price * 100
            if price_diff_percent > 20:
                logger.warning(f"Price difference {price_diff_percent:.2f}% exceeds 20% threshold")
                # Don't fail, just warn
            
            # Check stock availability
            if product.stock_quantity < data.get('quantity', 1):
                return False, "Insufficient stock"
        
        except Product.DoesNotExist:
            return False, "Product not found"
    
    # Validate shopkeeper exists
    try:
        from bson.errors import InvalidId
        Shopkeeper.objects.get(id=data['shopkeeper_id'])
    except (Shopkeeper.DoesNotExist, InvalidId):
        return False, "Shopkeeper not found"
    
    # Validate customer exists
    try:
        from bson.errors import InvalidId
        Customer.objects.get(id=data['customer_id'])
    except (Customer.DoesNotExist, InvalidId):
        return False, "Customer not found"
    
    # For credit transactions, check if amount is reasonable
    if data['type'] == 'credit':
        try:
            shopkeeper = Shopkeeper.objects.get(id=data['shopkeeper_id'])
            # Get average daily sales (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sales = Transaction.objects(
                shopkeeper_id=data['shopkeeper_id'],
                type='sale',
                timestamp__gte=thirty_days_ago
            )
            
            if recent_sales:
                total_sales = sum(t.amount for t in recent_sales)
                avg_daily_sales = total_sales / 30
                # Credit should not exceed 3x average daily sales
                if data['amount'] > avg_daily_sales * 3:
                    logger.warning(f"Credit amount {data['amount']} exceeds 3x average daily sales {avg_daily_sales}")
                    # Don't fail, just warn
        except Exception as e:
            logger.warning(f"Could not validate credit amount: {e}")
    
    return True, None


def create_transaction(data):
    """
    Create a new transaction
    
    Args:
        data: Transaction data dictionary
    
    Returns:
        Transaction: Created transaction object
    """
    # Validate transaction
    is_valid, error_message = validate_transaction(data)
    if not is_valid:
        raise ValidationError(error_message)
    
    # Get shopkeeper and customer objects for references
    try:
        from bson.errors import InvalidId
        shopkeeper = Shopkeeper.objects.get(id=data['shopkeeper_id'])
        customer = Customer.objects.get(id=data['customer_id'])
    except (Shopkeeper.DoesNotExist, InvalidId):
        raise ValidationError("Shopkeeper not found")
    except (Customer.DoesNotExist, InvalidId):
        raise ValidationError("Customer not found")
    
    # Get product if provided
    product = None
    if data.get('product_id'):
        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise ValidationError("Product not found")
    
    # Create transaction
    transaction = Transaction(
        type=data['type'],
        amount=data['amount'],
        shopkeeper_id=shopkeeper,
        customer_id=customer,
        product_id=product,
        timestamp=data.get('timestamp', datetime.now()),
        status=data.get('status', 'pending'),
        transcript_hash=data.get('transcript_hash'),
        notes=data.get('notes')
    )
    
    transaction.save()
    
    # Update customer statistics (customer object already retrieved above)
    if data['type'] == 'sale':
        customer.total_purchases += data['amount']
    elif data['type'] == 'credit':
        customer.total_credits += data['amount']
        customer.credit_balance += data['amount']
    elif data['type'] == 'repay':
        customer.credit_balance -= data['amount']
        if customer.credit_balance < 0:
            customer.credit_balance = 0
    customer.save()
    
    logger.info(f"Created transaction {transaction.id} of type {data['type']} for amount {data['amount']}")
    
    return transaction


def get_transactions(filters=None, page=1, page_size=20):
    """
    Get transactions with filtering and pagination
    
    Args:
        filters: Dictionary of filters (shopkeeper_id, customer_id, type, date_from, date_to, status)
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        tuple: (transactions list, total count, page, page_size)
    """
    if filters is None:
        filters = {}
    
    query = Transaction.objects()
    
    # Apply filters
    if 'shopkeeper_id' in filters:
        query = query.filter(shopkeeper_id=filters['shopkeeper_id'])
    
    if 'customer_id' in filters:
        query = query.filter(customer_id=filters['customer_id'])
    
    if 'type' in filters:
        query = query.filter(type=filters['type'])
    
    if 'status' in filters:
        query = query.filter(status=filters['status'])
    
    if 'date_from' in filters:
        query = query.filter(timestamp__gte=filters['date_from'])
    
    if 'date_to' in filters:
        query = query.filter(timestamp__lte=filters['date_to'])
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    skip = (page - 1) * page_size
    transactions = query.order_by('-timestamp').skip(skip).limit(page_size)
    
    return list(transactions), total_count, page, page_size


def get_transaction_by_id(transaction_id):
    """
    Get transaction by ID
    
    Args:
        transaction_id: Transaction ID
    
    Returns:
        Transaction: Transaction object
    """
    try:
        from bson.errors import InvalidId
        transaction = Transaction.objects.get(id=transaction_id)
    except (Transaction.DoesNotExist, InvalidId):
        raise NotFoundError(f"Transaction {transaction_id} not found")
    
    return transaction


def update_transaction_status(transaction_id, status, blockchain_tx_id=None, blockchain_block_number=None):
    """
    Update transaction status
    
    Args:
        transaction_id: Transaction ID
        status: New status ('pending', 'verified', 'disputed', 'completed')
        blockchain_tx_id: Optional blockchain transaction hash
        blockchain_block_number: Optional blockchain block number
    
    Returns:
        Transaction: Updated transaction object
    """
    try:
        from bson.errors import InvalidId
        transaction = Transaction.objects.get(id=transaction_id)
    except (Transaction.DoesNotExist, InvalidId):
        raise NotFoundError(f"Transaction {transaction_id} not found")
    
    # Validate status
    if status not in Transaction.STATUS_CHOICES:
        raise ValidationError(f"Invalid status: {status}. Must be one of {Transaction.STATUS_CHOICES}")
    
    transaction.status = status
    
    if blockchain_tx_id:
        transaction.blockchain_tx_id = blockchain_tx_id
    
    if blockchain_block_number:
        transaction.blockchain_block_number = blockchain_block_number
    
    transaction.save()
    
    logger.info(f"Updated transaction {transaction_id} status to {status}")
    
    return transaction


def update_transaction_with_customer_confirmation(transaction_id, customer_confirmed=True):
    """
    Update transaction when customer confirms via WhatsApp.
    Re-runs verification and writes to blockchain if now verified.
    
    Args:
        transaction_id: Transaction ID
        customer_confirmed: Whether customer confirmed the transaction
    
    Returns:
        Transaction: Updated transaction object
    """
    try:
        from bson.errors import InvalidId
        transaction = Transaction.objects.get(id=transaction_id)
    except (Transaction.DoesNotExist, InvalidId):
        raise NotFoundError(f"Transaction {transaction_id} not found")
    
    # Only re-verify if transaction was pending and has transcript
    if not transaction.transcript or transaction.status != 'pending':
        logger.info(f"Transaction {transaction_id} does not need re-verification "
                   f"(status={transaction.status}, has_transcript={bool(transaction.transcript)})")
        return transaction
    
    # Check if already written to blockchain
    if transaction.blockchain_tx_id:
        logger.info(f"Transaction {transaction_id} already written to blockchain")
        return transaction
    
    # Generate shopkeeper history
    shopkeeper_history = get_shopkeeper_history(str(transaction.shopkeeper_id.id))
    
    # Prepare verification data with customer confirmation
    amount_paise = int(rupees_to_paise(transaction.amount))
    
    verification_data = {
        'transcript': transaction.transcript,
        'type': transaction.type,
        'amount': amount_paise,
        'customer_id': str(transaction.customer_id.id),
        'shopkeeper_id': str(transaction.shopkeeper_id.id),
        'customer_confirmed': customer_confirmed,
        'shopkeeper_history': shopkeeper_history,
        'language': 'hi-IN'  # Default, could be stored in transaction metadata
    }
    
    # Initialize verification service
    blockchain_service = get_blockchain_service()
    verification_service = get_verification_service(blockchain_service)
    
    # Re-run verification
    if transaction.type == 'credit':
        verification_result = verification_service.verify_credit_transaction(verification_data)
    elif transaction.type == 'sale':
        verification_result = verification_service.verify_sales_transaction(verification_data)
    else:
        verification_result = verification_service.verify_credit_transaction(verification_data)
    
    # Update verification metadata
    fraud_check = verification_result.fraud_check or {}
    transaction.verification_status = verification_result.status.value
    transaction.fraud_score = fraud_check.get('score', 0.0) * 100
    transaction.fraud_risk_level = fraud_check.get('risk_level', 'low')
    
    if transaction.verification_metadata:
        transaction.verification_metadata.update({
            'storage_location': verification_result.storage_location.value,
            'fraud_check': fraud_check,
            'errors': verification_result.errors,
            'warnings': verification_result.warnings,
            'customer_confirmed': customer_confirmed,
            're_verified_at': datetime.utcnow().isoformat()
        })
    else:
        transaction.verification_metadata = {
            'storage_location': verification_result.storage_location.value,
            'fraud_check': fraud_check,
            'errors': verification_result.errors,
            'warnings': verification_result.warnings,
            'customer_confirmed': customer_confirmed,
            're_verified_at': datetime.utcnow().isoformat()
        }
    
    # Update status based on verification result
    if verification_result.status == VerificationStatus.VERIFIED:
        transaction.status = 'verified'
    elif verification_result.status == VerificationStatus.FLAGGED:
        transaction.status = 'pending'
    elif verification_result.status == VerificationStatus.REJECTED:
        transaction.status = 'disputed'
    
    # Write to blockchain if verified
    if verification_result.should_write_to_blockchain and blockchain_service:
        try:
            shopkeeper = Shopkeeper.objects.get(id=transaction.shopkeeper_id.id)
            shop_address = shopkeeper.wallet_address or shopkeeper.blockchain_address
            
            if shop_address:
                tx_type_map = {'sale': 0, 'credit': 1, 'repay': 2}
                tx_type = tx_type_map.get(transaction.type, 1)
                
                blockchain_result = blockchain_service.record_transaction(
                    voice_hash=verification_result.transcript_hash,
                    shop_address=shop_address,
                    amount=amount_paise,
                    tx_type=tx_type
                )
                
                if blockchain_result.get('success'):
                    transaction.blockchain_tx_id = blockchain_result['tx_hash']
                    transaction.blockchain_block_number = blockchain_result.get('block_number')
                    logger.info(f"Transaction {transaction_id} written to blockchain after confirmation: "
                              f"{blockchain_result['tx_hash']}")
        except Exception as e:
            logger.error(f"Error writing transaction {transaction_id} to blockchain after confirmation: {e}",
                        exc_info=True)
    
    transaction.save()
    
    logger.info(f"Updated transaction {transaction_id} with customer confirmation: "
               f"status={transaction.status}, blockchain={bool(transaction.blockchain_tx_id)}")
    
    return transaction


def aggregate_daily_sales(shopkeeper_id, start_date=None, end_date=None):
    """
    Aggregate daily sales for a shopkeeper
    
    Args:
        shopkeeper_id: Shopkeeper ID
        start_date: Start date (datetime)
        end_date: End date (datetime)
    
    Returns:
        list: List of daily sales dictionaries
    """
    query = Transaction.objects(
        shopkeeper_id=shopkeeper_id,
        type='sale',
        status='verified'
    )
    
    if start_date:
        query = query.filter(timestamp__gte=start_date)
    
    if end_date:
        query = query.filter(timestamp__lte=end_date)
    
    transactions = query.order_by('timestamp')
    
    # Group by date
    daily_sales = {}
    for transaction in transactions:
        date_key = transaction.timestamp.date().isoformat()
        if date_key not in daily_sales:
            daily_sales[date_key] = {
                'date': date_key,
                'count': 0,
                'total_amount': 0.0
            }
        
        daily_sales[date_key]['count'] += 1
        daily_sales[date_key]['total_amount'] += transaction.amount
    
    return list(daily_sales.values())


def create_pending_confirmation(transaction_id, phone, amount, shopkeeper_name, expires_at=None):
    """
    Create a pending confirmation record for WhatsApp credit confirmation
    
    Args:
        transaction_id: Transaction ID (string or ObjectId)
        phone: Customer phone number (normalized, e.g., +919876543210)
        amount: Transaction amount
        shopkeeper_name: Shopkeeper name
        expires_at: Expiration datetime (defaults to 24 hours from now)
    
    Returns:
        PendingConfirmation: Created pending confirmation object
    """
    try:
        from bson.errors import InvalidId
        transaction = Transaction.objects.get(id=transaction_id)
    except (Transaction.DoesNotExist, InvalidId):
        raise NotFoundError(f"Transaction {transaction_id} not found")
    
    if expires_at is None:
        expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Normalize phone number (ensure + prefix)
    if not phone.startswith('+'):
        phone = f'+{phone.lstrip("+")}'
    
    pending_confirmation = PendingConfirmation(
        transaction_id=transaction,
        phone=phone,
        amount=amount,
        shopkeeper=shopkeeper_name,
        status='pending',
        expires_at=expires_at
    )
    
    pending_confirmation.save()
    
    logger.info(f"Created pending confirmation for transaction {transaction_id}, phone {phone}")
    
    return pending_confirmation


def get_pending_confirmation_by_phone(phone):
    """
    Get the latest pending confirmation for a phone number
    
    Args:
        phone: Customer phone number (normalized)
    
    Returns:
        PendingConfirmation or None: Latest pending confirmation, or None if not found
    """
    # Normalize phone number
    if not phone.startswith('+'):
        phone = f'+{phone.lstrip("+")}'
    
    # Get latest pending confirmation that hasn't expired
    now = datetime.utcnow()
    pending = PendingConfirmation.objects(
        phone=phone,
        status='pending',
        expires_at__gt=now
    ).order_by('-created_at').first()
    
    if pending:
        logger.info(f"Found pending confirmation for phone {phone}: {pending.id}")
    else:
        logger.debug(f"No pending confirmation found for phone {phone}")
    
    return pending


def update_pending_confirmation_status(confirmation_id, status):
    """
    Update pending confirmation status
    
    Args:
        confirmation_id: PendingConfirmation ID (string or ObjectId)
        status: New status ('pending', 'confirmed', 'rejected', 'expired')
    
    Returns:
        PendingConfirmation: Updated pending confirmation object
    """
    try:
        from bson.errors import InvalidId
        confirmation = PendingConfirmation.objects.get(id=confirmation_id)
    except (PendingConfirmation.DoesNotExist, InvalidId):
        raise NotFoundError(f"Pending confirmation {confirmation_id} not found")
    
    if status not in PendingConfirmation.STATUS_CHOICES:
        raise ValidationError(f"Invalid status: {status}. Must be one of {PendingConfirmation.STATUS_CHOICES}")
    
    confirmation.status = status
    confirmation.save()
    
    logger.info(f"Updated pending confirmation {confirmation_id} status to {status}")
    
    return confirmation


def expire_old_confirmations():
    """
    Mark expired pending confirmations as expired
    
    Returns:
        int: Number of confirmations expired
    """
    now = datetime.utcnow()
    
    expired = PendingConfirmation.objects(
        status='pending',
        expires_at__lte=now
    ).update(set__status='expired')
    
    if expired > 0:
        logger.info(f"Expired {expired} old pending confirmations")
    
    return expired

