"""
Flask API application package
"""
from flask import Flask, request
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
    
    # Configure Flask sessions
    Session(app)
    
    # Initialize CORS - Allow all origins for mobile apps (CORS doesn't apply to mobile, but this ensures compatibility)
    CORS(app, origins='*', supports_credentials=True)
    
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
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log incoming requests with detailed information"""
        import json
        import os
        
        # #region agent log - Verify request reached Flask
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.cursor', 'debug.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'__init__.py:63','message':'Request reached Flask before_request','data':{'method':request.method,'path':request.path,'remoteAddr':request.remote_addr,'url':request.url,'headers':dict(request.headers)},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'D'})+'\n')
        except:
            pass
        # #endregion
        
        # Log basic request info
        logger.info(f"{request.method} {request.path} from {request.remote_addr}")
        
        # For POST/PUT requests, log the request body
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.is_json:
                    # Log JSON data
                    data = request.get_json(silent=True) or {}
                    # Truncate long data for readability
                    data_str = json.dumps(data, indent=2, default=str)
                    if len(data_str) > 1000:
                        data_str = data_str[:1000] + "... (truncated)"
                    logger.info(f"📥 Request Body:\n{data_str}")
                elif request.form:
                    # Log form data
                    form_data = dict(request.form)
                    logger.info(f"📥 Form Data: {json.dumps(form_data, indent=2)}")
                elif request.files:
                    # Log file upload info
                    files_info = {key: f.filename for key, f in request.files.items()}
                    logger.info(f"📥 File Upload: {json.dumps(files_info, indent=2)}")
            except Exception as e:
                logger.warning(f"Could not log request body: {e}")
        
        # #region agent log (debug file)
        try:
            import os
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.cursor', 'debug.log')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'__init__.py:62','message':'Request received','data':{'method':request.method,'path':request.path,'remoteAddr':request.remote_addr,'contentType':request.content_type},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'})+'\n')
        except Exception as e:
            pass  # Silently fail debug log
        # #endregion
    
    @app.teardown_appcontext
    def close_db(error):
        """Close database connection on app teardown"""
        pass  # MongoEngine handles connection pooling
    
    logger.info("✅ Flask application initialized successfully")
    
    return app

