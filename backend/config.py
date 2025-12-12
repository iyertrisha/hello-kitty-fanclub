import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_very_secret_key')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kirana_db')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'kirana_db')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # Twilio WhatsApp configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    # Dialogflow configuration
    DIALOGFLOW_PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID', '')
    DIALOGFLOW_CREDENTIALS_PATH = os.getenv('DIALOGFLOW_CREDENTIALS_PATH', '')
    
    # Vineet API configuration
    VINEET_API_BASE_URL = os.getenv('VINEET_API_BASE_URL', 'http://localhost:5000/api')
    
    # WhatsApp internal API key
    WHATSAPP_INTERNAL_API_KEY = os.getenv('WHATSAPP_INTERNAL_API_KEY', '')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    MONGODB_DB_NAME = os.getenv('MONGODB_TEST_DB_NAME', 'kirana_test_db')

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    CORS_ORIGINS = os.getenv('CORS_ORIGINS_PROD', 'https://your-prod-frontend.com').split(',')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

class BlockchainConfig:
    RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
    POLYGON_AMOY_RPC_URL = os.getenv("POLYGON_AMOY_RPC_URL", "https://rpc-amoy.polygon.technology")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
    ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS", "")
    CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))
    GAS_LIMIT = int(os.getenv("GAS_LIMIT", "3000000"))

    @classmethod
    def validate(cls, require_contract: bool = True):
        errors = []
        if not cls.PRIVATE_KEY:
            errors.append("PRIVATE_KEY is not set in environment variables")
        elif len(cls.PRIVATE_KEY) < 64:
            errors.append("PRIVATE_KEY appears to be invalid (too short, expected 64 hex characters)")
        if require_contract and not cls.CONTRACT_ADDRESS:
            errors.append("CONTRACT_ADDRESS is not set in environment variables (deploy contract first)")
        if not cls.ADMIN_ADDRESS and not cls.PRIVATE_KEY:
            errors.append("Either ADMIN_ADDRESS or PRIVATE_KEY must be set")
        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        return True

blockchain_config = BlockchainConfig()

