"""
Flask API application package
Exports create_app from database module

FIXED: Removed duplicate create_app() - now properly delegates to database module
"""
from database import create_app

__all__ = ['create_app']

