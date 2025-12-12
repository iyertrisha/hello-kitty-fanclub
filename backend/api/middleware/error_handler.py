"""
Error handling middleware
"""
from flask import jsonify, request
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    status_code = 500
    message = "An error occurred"

    def __init__(self, message=None, status_code=None, payload=None):
        Exception.__init__(self)
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIError):
    """Validation error (400)"""
    status_code = 400
    message = "Validation error"


class NotFoundError(APIError):
    """Not found error (404)"""
    status_code = 404
    message = "Resource not found"


class BadRequestError(APIError):
    """Bad request error (400)"""
    status_code = 400
    message = "Bad request"


class UnauthorizedError(APIError):
    """Unauthorized error (401)"""
    status_code = 401
    message = "Unauthorized"


class ForbiddenError(APIError):
    """Forbidden error (403)"""
    status_code = 403
    message = "Forbidden"


class ServiceUnavailableError(APIError):
    """Service unavailable error (503)"""
    status_code = 503
    message = "Service unavailable"


def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Handle validation errors"""
        logger.warning(f"Validation error: {e.message}")
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        """Handle not found errors"""
        logger.warning(f"Not found: {e.message}")
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response
    
    @app.errorhandler(BadRequestError)
    def handle_bad_request_error(e):
        """Handle bad request errors"""
        logger.warning(f"Bad request: {e.message}")
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response
    
    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized_error(e):
        """Handle unauthorized errors"""
        logger.warning(f"Unauthorized: {e.message}")
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(e):
        """Handle forbidden errors"""
        logger.warning(f"Forbidden: {e.message}")
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response
    
    @app.errorhandler(404)
    def handle_404(e):
        """Handle 404 errors"""
        logger.warning(f"404 Not Found: {request.path}")
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404,
            'path': request.path
        }), 404
    
    @app.errorhandler(500)
    def handle_500(e):
        """Handle 500 errors"""
        logger.error(f"500 Internal Server Error: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_error(e):
        """Handle all other exceptions"""
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'status_code': 500
        }), 500

