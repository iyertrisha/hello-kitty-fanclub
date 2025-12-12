"""
Flask API application package
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
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
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Connect to MongoDB
    try:
        connect(
            db=app.config['MONGODB_DB_NAME'],
            host=app.config['MONGODB_URI'],
            alias='default'
        )
        logger.info(f"✅ Connected to MongoDB: {app.config['MONGODB_DB_NAME']}")
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
    
    logger.info("✅ Flask application initialized successfully")
    
    return app

