"""
Flask API application package
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_session import Session
from mongoengine import connect, disconnect
import logging
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """
    Flask application factory
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing', 'default')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize Flask-Session for supplier authentication
    Session(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Connect to MongoDB
    try:
        # Parse MongoDB URI to extract database name if present
        mongodb_uri = app.config['MONGODB_URI']
        db_name = app.config['MONGODB_DB_NAME']
        
        # If URI contains database name, use it and don't pass db parameter
        # Otherwise use separate db parameter
        if '/' in mongodb_uri.split('?')[0].split('@')[-1]:
            # URI contains database name
            connect(
                host=mongodb_uri,
                alias='default'
            )
        else:
            # URI doesn't contain database name, use separate parameter
            connect(
                db=db_name,
                host=mongodb_uri,
                alias='default'
            )
        
        # FIXED: Validate connection by actually testing it
        from mongoengine import get_db
        db = get_db(alias='default')
        server_info = db.client.server_info()
        logger.info(f"✅ Connected to MongoDB: {db_name} (server version: {server_info.get('version', 'unknown')})")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise
    
    # Register blueprints
    from api.routes import register_blueprints
    register_blueprints(app)
    
    # Register error handlers
    from api.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return jsonify({
            'message': 'KiranaChain API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api': '/api'
            }
        })
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'KiranaChain API',
            'version': '1.0.0',
            'database': 'connected'
        })
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests"""
        logger.info(f"{request.method} {request.path}")
    
    @app.teardown_appcontext
    def close_db(error):
        """Close database connection on app teardown"""
        pass  # MongoEngine handles connection pooling
    
    # FIXED: Add shutdown handler to properly disconnect MongoDB
    import atexit
    def cleanup_mongodb():
        """Cleanup MongoDB connection on app shutdown"""
        try:
            disconnect(alias='default')
            logger.info("✅ Disconnected from MongoDB on shutdown")
        except Exception as e:
            logger.warning(f"⚠️ Error disconnecting from MongoDB: {e}")
    
    atexit.register(cleanup_mongodb)
    
    logger.info("✅ Flask application initialized successfully")
    
    return app

