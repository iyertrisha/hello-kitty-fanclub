"""
Flask API application package
Exports create_app from database module
"""
from database import create_app

__all__ = ['create_app']

