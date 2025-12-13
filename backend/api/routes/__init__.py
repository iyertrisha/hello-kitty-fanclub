"""
API Routes module
Register all blueprints here
"""
from flask import Blueprint, jsonify
import logging

logger = logging.getLogger(__name__)

def register_blueprints(app):
    """Register all route blueprints with Flask app"""
    
    # Test endpoint to verify connectivity
    @app.route('/api/test', methods=['GET', 'POST'])
    def test_endpoint():
        """Test endpoint to verify backend is reachable"""
        # #region agent log
        import json
        import os
        from flask import request
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.cursor', 'debug.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'routes/__init__.py:12','message':'Test endpoint reached','data':{'method':request.method,'remoteAddr':request.remote_addr},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'})+'\n')
        except:
            pass
        # #endregion
        return jsonify({'status': 'ok', 'message': 'Backend is reachable'}), 200
    
    # Import blueprints
    from api.routes.transactions import transactions_bp
    from api.routes.shopkeeper import shopkeeper_bp
    from api.routes.customer import customer_bp
    from api.routes.blockchain import blockchain_bp
    from api.routes.cooperative import cooperative_bp
    from api.routes.admin import admin_bp
    from api.routes.whatsapp import whatsapp_bp
    from api.routes.debt import debt_bp
    from api.routes.grocery import grocery_bp
    from api.routes.noticeboard import noticeboard_bp
    from api.routes.supplier import supplier_bp
    
    # Register blueprints
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(shopkeeper_bp, url_prefix='/api/shopkeeper')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    app.register_blueprint(cooperative_bp, url_prefix='/api/cooperative')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(whatsapp_bp, url_prefix='/api/whatsapp')
    app.register_blueprint(debt_bp, url_prefix='/api/debt')
    app.register_blueprint(grocery_bp, url_prefix='/api/grocery')
    app.register_blueprint(noticeboard_bp, url_prefix='/api/noticeboard')
    app.register_blueprint(supplier_bp, url_prefix='/api/supplier')
    
    # Add alias route for /api/customers (plural) for Flutter compatibility
    @app.route('/api/customers', methods=['GET'])
    def get_customers_alias():
        """Alias for /api/customer to support Flutter app"""
        from services.customer import get_all_customers
        try:
            customers = get_all_customers()
            return jsonify({
                'data': customers,
                'customers': customers,  # For backward compatibility
            }), 200
        except Exception as e:
            logger.error(f"Error getting customers: {e}", exc_info=True)
            from api.middleware.error_handler import ValidationError
            raise ValidationError(f"Failed to get customers: {str(e)}")

