"""
Amount conversion utilities for rupees and paise
"""
from typing import Union


def rupees_to_paise(rupees: Union[int, float]) -> int:
    """
    Convert rupees to paise
    
    Args:
        rupees: Amount in rupees (can be int or float)
    
    Returns:
        Amount in paise (int)
    
    Examples:
        >>> rupees_to_paise(100)
        10000
        >>> rupees_to_paise(50.50)
        5050
    """
    return int(rupees * 100)


def paise_to_rupees(paise: int) -> float:
    """
    Convert paise to rupees
    
    Args:
        paise: Amount in paise (int)
    
    Returns:
        Amount in rupees (float)
    
    Examples:
        >>> paise_to_rupees(10000)
        100.0
        >>> paise_to_rupees(5050)
        50.5
    """
    return paise / 100.0


def format_rupees(amount: Union[int, float]) -> str:
    """
    Format amount as rupees string
    
    Args:
        amount: Amount in rupees
    
    Returns:
        Formatted string (e.g., "₹100.50")
    
    Examples:
        >>> format_rupees(100.50)
        '₹100.50'
        >>> format_rupees(1000)
        '₹1000.00'
    """
    return f"₹{amount:.2f}"

