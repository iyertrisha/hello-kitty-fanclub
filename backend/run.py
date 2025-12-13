"""
Flask application entry point
"""
import os
import sys
import logging
import socket
from api import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_port_available(host, port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        sock.close()
        return True
    except OSError:
        return False

if __name__ == '__main__':
    try:
        # Get config name from environment or use default
        config_name = os.getenv('FLASK_ENV', 'default')
        logger.info(f"Starting Flask app with config: {config_name}")
        
        # Create Flask app
        app = create_app(config_name)
        
        # Get port from config
        port = app.config.get('FLASK_PORT', 5000)
        debug = app.config.get('FLASK_DEBUG', True)
        host = '0.0.0.0'
        
        # Check if port is available
        if not check_port_available(host, port):
            logger.error(f"❌ Port {port} is already in use! Please stop the other service or change FLASK_PORT.")
            sys.exit(1)
        
        # Get actual network IP addresses
        import socket as sock_module
        hostname = sock_module.gethostname()
        local_ip = sock_module.gethostbyname(hostname)
        try:
            # Try to get external IP (may fail, that's ok)
            s = sock_module.socket(sock_module.AF_INET, sock_module.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
            s.close()
        except:
            network_ip = local_ip
        
        logger.info("=" * 60)
        logger.info(f"🚀 Starting Flask server")
        logger.info(f"   Host: {host}")
        logger.info(f"   Port: {port}")
        logger.info(f"   Debug: {debug}")
        logger.info(f"   Threaded: True")
        logger.info("")
        logger.info(f"📱 Android emulator URL: http://10.0.2.2:{port}/api")
        logger.info(f"💻 Local access URL: http://localhost:{port}/api")
        logger.info(f"🌐 Network IP detected: {network_ip}")
        logger.info(f"🌐 Network access URL: http://{network_ip}:{port}/api")
        logger.info("")
        logger.info("⚠️  IMPORTANT: If Android emulator can't connect, check Windows Firewall!")
        logger.info(f"   Allow Python through firewall for port {port}")
        logger.info("")
        logger.info("✅ Server is ready to accept connections!")
        logger.info("=" * 60)
        
        # #region agent log - Verify socket binding
        import json
        import os
        log_path = os.path.join(os.path.dirname(__file__), '..', '.cursor', 'debug.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        try:
            # Test actual socket binding
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_sock.bind((host, port))
            test_sock.listen(1)
            bound_addr = test_sock.getsockname()
            test_sock.close()
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'run.py:61','message':'Socket binding verified','data':{'host':host,'port':port,'boundAddress':bound_addr[0],'boundPort':bound_addr[1]},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'B'})+'\n')
            logger.info(f"🔍 Socket binding verified: {bound_addr[0]}:{bound_addr[1]}")
        except Exception as e:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'run.py:61','message':'Socket binding failed','data':{'error':str(e)},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'B'})+'\n')
            logger.error(f"❌ Socket binding test failed: {e}")
        # #endregion
        
        # #region agent log - Test network connectivity
        try:
            # Test if we can actually accept connections from network
            test_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_listener.bind((host, port))
            test_listener.listen(5)
            test_listener.settimeout(0.1)  # Non-blocking
            logger.info(f"🔍 Network listener test: Socket is listening on {host}:{port}")
            test_listener.close()
        except Exception as e:
            logger.warning(f"⚠️  Network listener test failed: {e}")
        # #endregion
        
        # Run the app with explicit settings
        app.run(
            host=host,  # Listen on all interfaces (required for Android emulator)
            port=port,
            debug=debug,
            threaded=True,  # Enable threading for concurrent requests
            use_reloader=False  # Disable reloader to avoid issues
        )
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down Flask server...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Failed to start Flask server: {e}", exc_info=True)
        sys.exit(1)

