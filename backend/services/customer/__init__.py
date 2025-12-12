"""
Customer service module
"""
from .customer_service import (
    get_customer,
    create_customer,
    get_customer_orders,
    get_customer_credits
)

__all__ = [
    'get_customer',
    'create_customer',
    'get_customer_orders',
    'get_customer_credits'
]

