"""
Authentication middleware
"""
from functools import wraps
from flask import request, jsonify
from api.middleware.error_handler import UnauthorizedError, ForbiddenError
import logging

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Require authentication (basic implementation)
    For now, this is a placeholder for future JWT implementation
    
    Usage:
        @require_auth
        def my_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement JWT token validation
        # For now, allow all requests (development mode)
        # In production, validate JWT token from Authorization header
        
        # Example future implementation:
        # auth_header = request.headers.get('Authorization')
        # if not auth_header or not auth_header.startswith('Bearer '):
        #     raise UnauthorizedError("Missing or invalid authorization header")
        # token = auth_header.split(' ')[1]
        # # Validate token...
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_shopkeeper(f):
    """
    Require shopkeeper authentication
    
    Usage:
        @require_shopkeeper
        def my_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement shopkeeper-specific authentication
        # For now, allow all requests (development mode)
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """
    Require admin authentication
    
    Usage:
        @require_admin
        def my_route():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement admin authentication
        # For now, allow all requests (development mode)
        return f(*args, **kwargs)
    
    return decorated_function


def require_supplier_session(f):
    """
    Require supplier session authentication
    
    Checks Flask session for supplier_id and attaches supplier to request context
    
    Usage:
        @require_supplier_session
        def my_route():
            supplier_id = request.supplier_id
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, request
        
        supplier_id = session.get('supplier_id')
        if not supplier_id:
            raise UnauthorizedError("Authentication required. Please login.")
        
        # Attach supplier_id to request for easy access
        request.supplier_id = supplier_id
        request.supplier_email = session.get('email')
        
        return f(*args, **kwargs)
    
    return decorated_function
