"""
Weekly reminder service - Enhanced reminders with debt duration and history
"""
from datetime import datetime, timedelta
from database.models import Customer, Transaction
from api.middleware.error_handler import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


def get_customers_for_weekly_reminder(days_threshold=7):
    """
    Get customers with debt >= days_threshold days old
    
    Args:
        days_threshold: Minimum days since first debt (default: 7)
        
    Returns:
        list: Customer dictionaries with debt info
    """
    customers = Customer.objects(credit_balance__gt=0)
    
    result = []
    cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
    
    for customer in customers:
        # Get first debt date
        first_debt_date = get_first_debt_date(customer.id)
        
        if first_debt_date and first_debt_date <= cutoff_date:
            # Calculate days since first debt
            days_since_first = (datetime.utcnow() - first_debt_date).days
            
            # Get debt statistics
            stats = get_debt_statistics(customer.id)
            
            result.append({
                'phone': customer.phone,
                'name': customer.name,
                'total_debt': float(customer.credit_balance),
                'days_since_first': days_since_first,
                'history': stats
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


def format_weekly_reminder(customer, debt_info):
    """
    Format weekly reminder message
    
    Args:
        customer: Customer dict with phone, name, total_debt
        debt_info: Debt info dict with days_since_first, history
        
    Returns:
        str: Formatted reminder message
    """
    days = debt_info.get('days_since_first', 0)
    history = debt_info.get('history', {})
    
    # Format days
    if days == 1:
        days_text = "1 day ago"
    else:
        days_text = f"{days} days ago"
    
    # Format last payment
    last_payment_date = history.get('last_payment_date')
    if last_payment_date:
        if isinstance(last_payment_date, str):
            last_payment_date = datetime.fromisoformat(last_payment_date.replace('Z', '+00:00'))
        days_since_payment = (datetime.utcnow() - last_payment_date).days
        if days_since_payment == 0:
            last_payment_text = "Today"
        elif days_since_payment == 1:
            last_payment_text = "1 day ago"
        else:
            last_payment_text = f"{days_since_payment} days ago"
    else:
        last_payment_text = "Never"
    
    message = f"📢 *Weekly Debt Reminder*\n\n"
    message += f"Dear {customer.get('name', 'Customer')},\n\n"
    message += f"You have an outstanding balance of *₹{customer.get('total_debt', 0):.2f}*\n\n"
    message += f"*Debt Details:*\n"
    message += f"• First debt: {days_text}\n"
    message += f"• Total transactions: {history.get('total_transactions', 0)}\n"
    message += f"• Last payment: {last_payment_text}\n\n"
    message += f"Please clear your dues at your earliest convenience.\n\n"
    message += f"Thank you!"
    
    return message

