"""
Debt tracking service - Core business logic for debt management
"""
from datetime import datetime, timedelta
from database.models import Customer, Transaction, Shopkeeper
from api.middleware.error_handler import NotFoundError, ValidationError
from services.transaction import create_transaction, update_transaction_status
import logging
import hashlib

logger = logging.getLogger(__name__)

# Try to import blockchain service
BLOCKCHAIN_AVAILABLE = False
BlockchainService = None

try:
    import sys
    from pathlib import Path
    blockchain_path = Path(__file__).parent.parent.parent / 'blockchain'
    sys.path.insert(0, str(blockchain_path))
    
    from utils.contract_service import BlockchainService
    from config import BlockchainConfig
    
    if BlockchainConfig.CONTRACT_ADDRESS and BlockchainConfig.PRIVATE_KEY:
        BLOCKCHAIN_AVAILABLE = True
        logger.info("Blockchain service available for debt tracking")
    else:
        logger.warning("Blockchain service not configured (missing CONTRACT_ADDRESS or PRIVATE_KEY)")
except ImportError as e:
    logger.warning(f"Blockchain service not available: {e}")
except Exception as e:
    logger.warning(f"Error loading blockchain service: {e}")


def get_customer_by_phone(phone):
    """
    Get customer by phone number
    
    Args:
        phone: Phone number (normalized with + prefix)
    
    Returns:
        Customer: Customer object
    """
    # Normalize phone
    if not phone.startswith('+'):
        phone = f'+{phone.lstrip("+")}'
    
    try:
        customer = Customer.objects.get(phone=phone)
        return customer
    except Customer.DoesNotExist:
        raise NotFoundError(f"Customer with phone {phone} not found")


def get_customer_debt(customer_id=None, phone=None):
    """
    Get customer debt balance and summary
    
    Args:
        customer_id: Customer ID (optional)
        phone: Phone number (optional, used if customer_id not provided)
    
    Returns:
        dict: Debt summary with balance, recent transactions, etc.
    """
    # Get customer
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise NotFoundError(f"Customer {customer_id} not found")
    elif phone:
        customer = get_customer_by_phone(phone)
    else:
        raise ValidationError("Either customer_id or phone must be provided")
    
    # Get recent credit transactions (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_credits = Transaction.objects(
        customer_id=customer.id,
        type__in=['credit', 'repay'],
        timestamp__gte=thirty_days_ago
    ).order_by('-timestamp').limit(10)
    
    # Format recent transactions
    recent_transactions = []
    for tx in recent_credits:
        recent_transactions.append({
            'id': str(tx.id),
            'type': tx.type,
            'amount': float(tx.amount),
            'timestamp': tx.timestamp.isoformat() if tx.timestamp else None,
            'status': tx.status,
            'notes': tx.notes
        })
    
    # Calculate next reminder date (7 days from now)
    next_reminder_date = (datetime.utcnow() + timedelta(days=7)).strftime('%d %b %Y')
    
    return {
        'customer_id': str(customer.id),
        'customer_name': customer.name,
        'phone': customer.phone,
        'total_debt': float(customer.credit_balance),
        'total_credits': float(customer.total_credits),
        'recent_transactions': recent_transactions,
        'next_reminder_date': next_reminder_date
    }


def record_debt_entry(customer_id=None, phone=None, shopkeeper_id=None, amount=None, description=None):
    """
    Record a new debt entry (credit transaction)
    
    Args:
        customer_id: Customer ID (optional)
        phone: Phone number (optional, used if customer_id not provided)
        shopkeeper_id: Shopkeeper ID (required)
        amount: Debt amount
        description: Description/notes for the debt
    
    Returns:
        dict: Transaction details including new balance and blockchain info
    """
    # Validate required fields
    if not amount or amount <= 0:
        raise ValidationError("Amount must be greater than 0")
    
    if not shopkeeper_id:
        raise ValidationError("shopkeeper_id is required")
    
    # Get customer
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise NotFoundError(f"Customer {customer_id} not found")
    elif phone:
        customer = get_customer_by_phone(phone)
    else:
        raise ValidationError("Either customer_id or phone must be provided")
    
    # Get shopkeeper
    try:
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    
    # Create transaction
    transaction_data = {
        'type': 'credit',
        'amount': float(amount),
        'shopkeeper_id': str(shopkeeper.id),
        'customer_id': str(customer.id),
        'status': 'verified',  # Auto-verify debt entries from WhatsApp
        'notes': description or 'Debt entry via WhatsApp'
    }
    
    transaction = create_transaction(transaction_data)
    
    # Record on blockchain if available
    blockchain_tx_id = None
    blockchain_block_number = None
    
    if BLOCKCHAIN_AVAILABLE:
        try:
            # Initialize blockchain service
            from config import BlockchainConfig
            blockchain_service = BlockchainService(
                rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL or BlockchainConfig.RPC_URL,
                private_key=BlockchainConfig.PRIVATE_KEY,
                contract_address=BlockchainConfig.CONTRACT_ADDRESS
            )
            
            # Create hash for transaction (using transaction ID and timestamp)
            tx_hash_data = f"{transaction.id}_{transaction.timestamp.isoformat()}_{amount}"
            tx_hash = hashlib.sha256(tx_hash_data.encode()).hexdigest()
            
            # Convert amount to wei (assuming amount is in rupees, 1 rupee = 10^18 wei for demo)
            # In production, you might want a different conversion
            amount_wei = int(float(amount) * 1e18)
            
            # Record transaction on blockchain (type 1 = CREDIT)
            result = blockchain_service.record_transaction(
                voice_hash=tx_hash,
                shop_address=shopkeeper.wallet_address,
                amount=amount_wei,
                tx_type=1  # CREDIT
            )
            
            if result.get('success'):
                blockchain_tx_id = result.get('tx_hash')
                blockchain_block_number = result.get('block_number')
                
                # Update transaction with blockchain info
                update_transaction_status(
                    str(transaction.id),
                    'verified',
                    blockchain_tx_id=blockchain_tx_id,
                    blockchain_block_number=blockchain_block_number
                )
                
                logger.info(f"✅ Debt entry recorded on blockchain: {blockchain_tx_id}")
            else:
                logger.warning(f"⚠️ Blockchain recording failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Error recording debt on blockchain: {e}", exc_info=True)
            # Continue without blockchain - don't fail the transaction
    
    # Get updated customer balance
    customer.reload()
    
    return {
        'transaction_id': str(transaction.id),
        'amount': float(amount),
        'new_balance': float(customer.credit_balance),
        'blockchain_tx_id': blockchain_tx_id,
        'blockchain_block_number': blockchain_block_number
    }


def record_payment(customer_id=None, phone=None, amount=None):
    """
    Record a payment (repay transaction)
    
    Args:
        customer_id: Customer ID (optional)
        phone: Phone number (optional, used if customer_id not provided)
        amount: Payment amount
    
    Returns:
        dict: Payment details including new balance and blockchain info
    """
    # Validate required fields
    if not amount or amount <= 0:
        raise ValidationError("Amount must be greater than 0")
    
    # Get customer
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise NotFoundError(f"Customer {customer_id} not found")
    elif phone:
        customer = get_customer_by_phone(phone)
    else:
        raise ValidationError("Either customer_id or phone must be provided")
    
    # Check if payment exceeds balance
    if amount > customer.credit_balance:
        raise ValidationError(
            f"Payment amount (₹{amount}) exceeds outstanding balance (₹{customer.credit_balance})"
        )
    
    # Get shopkeeper (use first shopkeeper for now, or make it configurable)
    # In production, you might want to track which shopkeeper the payment is for
    shopkeeper = Shopkeeper.objects.first()
    if not shopkeeper:
        raise ValidationError("No shopkeeper found. Please register a shopkeeper first.")
    
    previous_balance = float(customer.credit_balance)
    
    # Create repayment transaction
    transaction_data = {
        'type': 'repay',
        'amount': float(amount),
        'shopkeeper_id': str(shopkeeper.id),
        'customer_id': str(customer.id),
        'status': 'verified',
        'notes': 'Payment via WhatsApp'
    }
    
    transaction = create_transaction(transaction_data)
    
    # Record on blockchain if available
    blockchain_tx_id = None
    blockchain_block_number = None
    
    if BLOCKCHAIN_AVAILABLE:
        try:
            # Initialize blockchain service
            from config import BlockchainConfig
            blockchain_service = BlockchainService(
                rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL or BlockchainConfig.RPC_URL,
                private_key=BlockchainConfig.PRIVATE_KEY,
                contract_address=BlockchainConfig.CONTRACT_ADDRESS
            )
            
            # Create hash for transaction
            tx_hash_data = f"{transaction.id}_{transaction.timestamp.isoformat()}_{amount}"
            tx_hash = hashlib.sha256(tx_hash_data.encode()).hexdigest()
            
            # Convert amount to wei
            amount_wei = int(float(amount) * 1e18)
            
            # Record transaction on blockchain (type 2 = REPAY)
            result = blockchain_service.record_transaction(
                voice_hash=tx_hash,
                shop_address=shopkeeper.wallet_address,
                amount=amount_wei,
                tx_type=2  # REPAY
            )
            
            if result.get('success'):
                blockchain_tx_id = result.get('tx_hash')
                blockchain_block_number = result.get('block_number')
                
                # Update transaction with blockchain info
                update_transaction_status(
                    str(transaction.id),
                    'verified',
                    blockchain_tx_id=blockchain_tx_id,
                    blockchain_block_number=blockchain_block_number
                )
                
                logger.info(f"✅ Payment recorded on blockchain: {blockchain_tx_id}")
            else:
                logger.warning(f"⚠️ Blockchain recording failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Error recording payment on blockchain: {e}", exc_info=True)
            # Continue without blockchain
    
    # Get updated customer balance
    customer.reload()
    
    return {
        'transaction_id': str(transaction.id),
        'amount': float(amount),
        'previous_balance': previous_balance,
        'new_balance': float(customer.credit_balance),
        'blockchain_tx_id': blockchain_tx_id,
        'blockchain_block_number': blockchain_block_number
    }


def get_customers_for_reminder(days_overdue=0):
    """
    Get list of customers who need reminders
    
    Args:
        days_overdue: Minimum days since last transaction to send reminder (default: 0 = all with debt)
    
    Returns:
        list: List of customer dictionaries with debt info
    """
    # Get all customers with outstanding debt
    customers_with_debt = Customer.objects(credit_balance__gt=0)
    
    result = []
    cutoff_date = datetime.utcnow() - timedelta(days=days_overdue)
    
    for customer in customers_with_debt:
        # Get last transaction date
        last_transaction = Transaction.objects(
            customer_id=customer.id
        ).order_by('-timestamp').first()
        
        # Include if no last transaction or it's older than cutoff
        include = True
        if last_transaction and last_transaction.timestamp:
            if last_transaction.timestamp > cutoff_date:
                include = False
        
        if include:
            result.append({
                'customer_id': str(customer.id),
                'name': customer.name,
                'phone': customer.phone,
                'total_debt': float(customer.credit_balance),
                'last_transaction_date': last_transaction.timestamp.isoformat() if last_transaction and last_transaction.timestamp else None
            })
    
    return result


def get_first_debt_date(customer_id):
    """
    Get date of first debt transaction
    
    Args:
        customer_id: Customer ID
        
    Returns:
        datetime: First debt date or None
    """
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return None
    
    # Get first credit transaction
    first_credit = Transaction.objects(
        customer_id=customer,
        type='credit'
    ).order_by('timestamp').first()
    
    if first_credit:
        return first_credit.timestamp
    
    return None


def get_debt_statistics(customer_id):
    """
    Get debt statistics for a customer
    
    Args:
        customer_id: Customer ID
        
    Returns:
        dict: {
            'total_transactions': int,
            'credit_count': int,
            'payment_count': int,
            'last_payment_date': datetime or None,
            'last_credit_date': datetime or None
        }
    """
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return {
            'total_transactions': 0,
            'credit_count': 0,
            'payment_count': 0,
            'last_payment_date': None,
            'last_credit_date': None
        }
    
    transactions = Transaction.objects(customer_id=customer)
    
    credit_txs = transactions.filter(type='credit').order_by('-timestamp')
    payment_txs = transactions.filter(type='repay').order_by('-timestamp')
    
    last_payment = payment_txs.first()
    last_credit = credit_txs.first()
    
    return {
        'total_transactions': transactions.count(),
        'credit_count': credit_txs.count(),
        'payment_count': payment_txs.count(),
        'last_payment_date': last_payment.timestamp if last_payment else None,
        'last_credit_date': last_credit.timestamp if last_credit else None
    }


def format_debt_summary(customer_id):
    """
    Format debt summary as a readable message
    
    Args:
        customer_id: Customer ID
    
    Returns:
        str: Formatted debt summary message
    """
    summary = get_customer_debt(customer_id=customer_id)
    
    message = f"💰 Debt Summary for {summary['customer_name']}\n\n"
    message += f"Total Outstanding: ₹{summary['total_debt']:.2f}\n"
    
    if summary['recent_transactions']:
        message += "\nRecent Transactions:\n"
        for tx in summary['recent_transactions'][:5]:
            symbol = "➕" if tx['type'] == 'credit' else "➖"
            date = datetime.fromisoformat(tx['timestamp']).strftime('%d %b') if tx['timestamp'] else 'N/A'
            message += f"{symbol} ₹{tx['amount']:.2f} - {date}\n"
    
    return message

