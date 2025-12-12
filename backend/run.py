"""
Flask application entry point
"""
import os
from api import create_app

if __name__ == '__main__':
    # Get config name from environment or use default
    config_name = os.getenv('FLASK_ENV', 'default')
    
    # Create Flask app
    app = create_app(config_name)
    
    # Get port from config
    port = app.config.get('FLASK_PORT', 5000)
    debug = app.config.get('FLASK_DEBUG', True)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

