"""
Monthly Confirmation Service
Handles monthly purchase summaries and customer confirmations via WhatsApp
"""
from datetime import datetime, timedelta
from collections import defaultdict
from database.models import Transaction, Customer
from api.middleware.error_handler import NotFoundError, ValidationError
import logging
import os

logger = logging.getLogger(__name__)


def generate_monthly_summary(customer_id, month, year):
    """
    Generate monthly purchase summary for a customer
    
    Args:
        customer_id: Customer ID (string or ObjectId)
        month: Month number (1-12)
        year: Year (e.g., 2024)
    
    Returns:
        dict: {
            "total_purchases": float,
            "items_count": int,
            "transactions_count": int,
            "top_items": list of {"name": str, "price": float, "times": int},
            "month": int,
            "year": int
        }
    """
    try:
        from bson.errors import InvalidId
        customer = Customer.objects.get(id=customer_id)
    except (Customer.DoesNotExist, InvalidId):
        raise NotFoundError(f"Customer {customer_id} not found")
    
    # Calculate date range for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Query transactions for the month
    transactions = Transaction.objects(
        customer_id=customer_id,
        type='sale',
        status__in=['verified', 'completed'],
        timestamp__gte=start_date,
        timestamp__lt=end_date
    ).order_by('timestamp')
    
    # Aggregate data
    total_purchases = 0.0
    items_count = 0
    transactions_count = transactions.count()
    
    # Track items for top items calculation
    item_counts = defaultdict(lambda: {'count': 0, 'total_price': 0.0})
    
    for transaction in transactions:
        total_purchases += transaction.amount
        
        # If transaction has a product, track it
        if transaction.product_id:
            product = transaction.product_id
            product_name = product.name
            item_counts[product_name]['count'] += 1
            item_counts[product_name]['total_price'] += transaction.amount
            items_count += 1
    
    # Get top 3 items by frequency
    top_items = []
    sorted_items = sorted(
        item_counts.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:3]
    
    for item_name, data in sorted_items:
        # Calculate average price per occurrence
        avg_price = data['total_price'] / data['count'] if data['count'] > 0 else 0
        top_items.append({
            'name': item_name,
            'price': round(avg_price, 2),
            'times': data['count']
        })
    
    summary = {
        'total_purchases': round(total_purchases, 2),
        'items_count': items_count,
        'transactions_count': transactions_count,
        'top_items': top_items,
        'month': month,
        'year': year
    }
    
    logger.info(f"Generated monthly summary for customer {customer_id}, {month}/{year}: {transactions_count} transactions, ₹{total_purchases}")
    
    return summary


def format_monthly_message(summary):
    """
    Format monthly summary as WhatsApp message
    
    Args:
        summary: Summary dict from generate_monthly_summary
    
    Returns:
        str: Formatted message text
    """
    month_names = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    month_name = month_names[summary['month']]
    year = summary['year']
    
    message = f"Namaste! Your purchase summary for {month_name} {year}:\n\n"
    message += f"📦 Total Purchases: ₹{summary['total_purchases']}\n"
    message += f"🛒 Items: {summary['items_count']}\n"
    message += f"📅 Transactions: {summary['transactions_count']}\n\n"
    
    if summary['top_items']:
        message += "Top items:\n"
        for idx, item in enumerate(summary['top_items'], 1):
            message += f"{idx}. {item['name']} - ₹{item['price']} ({item['times']} times)\n"
        message += "\n"
    
    message += "Reply DISPUTE if you find any errors.\n"
    message += "Reply OK to confirm."
    
    return message


def send_monthly_confirmation(customer_id, month=None, year=None):
    """
    Generate and send monthly confirmation message via WhatsApp
    
    Args:
        customer_id: Customer ID
        month: Month number (defaults to previous month)
        year: Year (defaults to current year or previous year if month is December)
    
    Returns:
        dict: {
            "success": bool,
            "message_sid": str or None,
            "summary": dict
        }
    """
    try:
        from integrations.whatsapp import TwilioClient
        
        # Get customer
        try:
            from bson.errors import InvalidId
            customer = Customer.objects.get(id=customer_id)
        except (Customer.DoesNotExist, InvalidId):
            raise NotFoundError(f"Customer {customer_id} not found")
        
        # Default to previous month
        if month is None or year is None:
            today = datetime.utcnow()
            if today.month == 1:
                month = 12
                year = today.year - 1
            else:
                month = today.month - 1
                year = today.year
        
        # Generate summary
        summary = generate_monthly_summary(customer_id, month, year)
        
        # Format message
        message_text = format_monthly_message(summary)
        
        # Send via Twilio
        twilio_client = TwilioClient()
        phone = customer.phone
        if not phone.startswith('whatsapp:'):
            phone = f'whatsapp:{phone}'
        
        result = twilio_client.send_message(phone, message_text)
        
        logger.info(f"Sent monthly confirmation to customer {customer_id}, message SID: {result['sid']}")
        
        return {
            'success': True,
            'message_sid': result['sid'],
            'summary': summary
        }
    except Exception as e:
        logger.error(f"Failed to send monthly confirmation to customer {customer_id}: {e}", exc_info=True)
        raise


def process_confirmation_response(customer_id, response):
    """
    Process customer response to monthly confirmation (OK/DISPUTE)
    
    Args:
        customer_id: Customer ID
        response: Response text (should be "OK" or "DISPUTE")
    
    Returns:
        dict: {
            "success": bool,
            "action": str ("confirmed" or "disputed"),
            "disputed_transactions": list or None
        }
    """
    try:
        from bson.errors import InvalidId
        customer = Customer.objects.get(id=customer_id)
    except (Customer.DoesNotExist, InvalidId):
        raise NotFoundError(f"Customer {customer_id} not found")
    
    response_upper = response.strip().upper()
    
    if response_upper == 'OK':
        # Mark monthly confirmation as confirmed
        # For now, we just log it. In future, could add a MonthlyConfirmation model
        logger.info(f"Customer {customer_id} confirmed monthly summary")
        
        return {
            'success': True,
            'action': 'confirmed',
            'disputed_transactions': None
        }
    
    elif response_upper == 'DISPUTE':
        # Flag disputed transactions for review
        # Get transactions from previous month
        today = datetime.utcnow()
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        # Get transactions and flag them
        transactions = Transaction.objects(
            customer_id=customer_id,
            timestamp__gte=start_date,
            timestamp__lt=end_date
        )
        
        disputed_ids = []
        for transaction in transactions:
            # Update status to disputed
            transaction.status = 'disputed'
            transaction.notes = f"Disputed by customer on {datetime.utcnow().isoformat()}"
            transaction.save()
            disputed_ids.append(str(transaction.id))
        
        logger.warning(f"Customer {customer_id} disputed monthly summary. Flagged {len(disputed_ids)} transactions")
        
        return {
            'success': True,
            'action': 'disputed',
            'disputed_transactions': disputed_ids
        }
    
    else:
        raise ValidationError(f"Invalid response: {response}. Expected 'OK' or 'DISPUTE'")


def flag_disputed_transactions(customer_id, month, year):
    """
    Flag all transactions for a customer in a specific month as disputed
    
    Args:
        customer_id: Customer ID
        month: Month number (1-12)
        year: Year
    
    Returns:
        int: Number of transactions flagged
    """
    try:
        from bson.errors import InvalidId
        customer = Customer.objects.get(id=customer_id)
    except (Customer.DoesNotExist, InvalidId):
        raise NotFoundError(f"Customer {customer_id} not found")
    
    # Calculate date range
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Get and flag transactions
    transactions = Transaction.objects(
        customer_id=customer_id,
        timestamp__gte=start_date,
        timestamp__lt=end_date
    )
    
    count = 0
    for transaction in transactions:
        transaction.status = 'disputed'
        transaction.notes = f"Disputed by customer on {datetime.utcnow().isoformat()}"
        transaction.save()
        count += 1
    
    logger.info(f"Flagged {count} transactions as disputed for customer {customer_id}, {month}/{year}")
    
    return count

