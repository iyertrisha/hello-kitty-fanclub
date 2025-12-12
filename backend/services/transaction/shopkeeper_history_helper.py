"""
Shopkeeper History Helper

Generates shopkeeper_history dict from MongoDB queries for fraud detection.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from database.models import Transaction, Product
from services.transaction.amount_utils import rupees_to_paise
import logging

logger = logging.getLogger(__name__)


def get_shopkeeper_history(shopkeeper_id: str) -> Dict[str, Any]:
    """
    Generate shopkeeper_history dict from MongoDB queries for fraud detection.
    
    Args:
        shopkeeper_id: MongoDB ObjectId string of the shopkeeper
    
    Returns:
        Dict with shopkeeper history data:
        {
            'average_daily_sales': int,  # in paise
            'customer_credits_today': Dict[str, int],  # customer_id -> count
            'customer_purchase_history': Dict[str, List],  # customer_id -> list of purchase amounts
            'product_catalog': Dict[str, int],  # product_name -> price in paise
            'sales_today': int,  # in paise
            'total_transactions': int
        }
    """
    try:
        # Calculate average daily sales (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_sales = Transaction.objects(
            shopkeeper_id=shopkeeper_id,
            type='sale',
            timestamp__gte=thirty_days_ago
        )
        
        total_sales = sum(t.amount for t in recent_sales)
        avg_daily_sales = int(rupees_to_paise(total_sales / 30)) if recent_sales else 0
        
        # Get customer credits today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        credits_today = Transaction.objects(
            shopkeeper_id=shopkeeper_id,
            type='credit',
            timestamp__gte=today_start
        )
        
        customer_credits_today = {}
        for tx in credits_today:
            customer_id = str(tx.customer_id.id)
            customer_credits_today[customer_id] = customer_credits_today.get(customer_id, 0) + 1
        
        # Get customer purchase history (last 90 days)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        customer_purchases = Transaction.objects(
            shopkeeper_id=shopkeeper_id,
            type='sale',
            timestamp__gte=ninety_days_ago
        )
        
        customer_purchase_history = {}
        for tx in customer_purchases:
            customer_id = str(tx.customer_id.id)
            if customer_id not in customer_purchase_history:
                customer_purchase_history[customer_id] = []
            customer_purchase_history[customer_id].append(int(rupees_to_paise(tx.amount)))
        
        # Get product catalog
        products = Product.objects(shopkeeper_id=shopkeeper_id)
        product_catalog = {}
        for p in products:
            product_catalog[p.name] = int(rupees_to_paise(p.price))
        
        # Calculate sales today
        sales_today = Transaction.objects(
            shopkeeper_id=shopkeeper_id,
            type='sale',
            timestamp__gte=today_start
        )
        sales_today_amount = sum(t.amount for t in sales_today)
        sales_today_paise = int(rupees_to_paise(sales_today_amount))
        
        # Get total transactions count
        total_transactions = Transaction.objects(shopkeeper_id=shopkeeper_id).count()
        
        history = {
            'average_daily_sales': avg_daily_sales,
            'customer_credits_today': customer_credits_today,
            'customer_purchase_history': customer_purchase_history,
            'product_catalog': product_catalog,
            'sales_today': sales_today_paise,
            'total_transactions': total_transactions
        }
        
        logger.info(f"Generated shopkeeper history for {shopkeeper_id}: "
                   f"avg_daily_sales={avg_daily_sales} paise, "
                   f"total_transactions={total_transactions}")
        
        return history
        
    except Exception as e:
        logger.error(f"Error generating shopkeeper history for {shopkeeper_id}: {e}", exc_info=True)
        # Return empty history on error
        return {
            'average_daily_sales': 0,
            'customer_credits_today': {},
            'customer_purchase_history': {},
            'product_catalog': {},
            'sales_today': 0,
            'total_transactions': 0
        }

