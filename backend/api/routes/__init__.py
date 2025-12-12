"""
API Routes module
Register all blueprints here
"""
from flask import Blueprint

def register_blueprints(app):
    """Register all route blueprints with Flask app"""
    
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

