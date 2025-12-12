"""
Order routing service module
"""
from .order_routing import (
    find_nearest_store,
    route_order,
    check_inventory,
    calculate_distance
)

__all__ = [
    'find_nearest_store',
    'route_order',
    'check_inventory',
    'calculate_distance'
]

