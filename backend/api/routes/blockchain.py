"""
Blockchain routes - Integration with Trisha's contract_service.py
"""
from flask import Blueprint, request, jsonify
import sys
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

blockchain_bp = Blueprint('blockchain', __name__)

# Import blockchain service
BLOCKCHAIN_AVAILABLE = False
BlockchainService = None
BlockchainConfig = None

try:
    # Ensure .env is loaded from backend directory before importing blockchain config
    from dotenv import load_dotenv
    backend_dir = Path(__file__).parent.parent.parent
    env_path = backend_dir / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logger.info(f"Loaded .env from {env_path}")
    
    # Add blockchain directory to path
    blockchain_path = backend_dir / 'blockchain'
    sys.path.insert(0, str(blockchain_path))
    
    # Import from blockchain module
    from utils.contract_service import BlockchainService
    from config import BlockchainConfig
    
    # Reload .env to ensure blockchain config gets the values
    load_dotenv(dotenv_path=env_path)
    
    # Check if blockchain is properly configured
    if BlockchainConfig.CONTRACT_ADDRESS and BlockchainConfig.PRIVATE_KEY:
        BLOCKCHAIN_AVAILABLE = True
        logger.info(f"Blockchain service loaded successfully (Contract: {BlockchainConfig.CONTRACT_ADDRESS[:10]}..., RPC: {BlockchainConfig.RPC_URL})")
    else:
        logger.warning(f"Blockchain service loaded but not configured (CONTRACT_ADDRESS: {bool(BlockchainConfig.CONTRACT_ADDRESS)}, PRIVATE_KEY: {bool(BlockchainConfig.PRIVATE_KEY)})")
        BLOCKCHAIN_AVAILABLE = False
except ImportError as e:
    logger.warning(f"Blockchain service not available: {e}")
except Exception as e:
    logger.warning(f"Error loading blockchain service: {e}")


def get_blockchain_service():
    """Get initialized blockchain service"""
    if not BLOCKCHAIN_AVAILABLE:
        raise Exception("Blockchain service not available - check if blockchain module is installed")
    
    if BlockchainConfig is None:
        raise Exception("BlockchainConfig not loaded")
    
    if not BlockchainConfig.CONTRACT_ADDRESS:
        raise Exception("Contract address not configured in .env file")
    
    if not BlockchainConfig.PRIVATE_KEY:
        raise Exception("Private key not configured in .env file")
    
    return BlockchainService(
        rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL,
        private_key=BlockchainConfig.PRIVATE_KEY,
        contract_address=BlockchainConfig.CONTRACT_ADDRESS
    )


@blockchain_bp.route('/status', methods=['GET'])
def get_blockchain_status():
    """Get blockchain service status"""
    status = {
        'available': BLOCKCHAIN_AVAILABLE,
        'configured': False,
        'contract_address': None,
        'network': None
    }
    
    if BLOCKCHAIN_AVAILABLE and BlockchainConfig:
        status['configured'] = bool(BlockchainConfig.CONTRACT_ADDRESS and BlockchainConfig.PRIVATE_KEY)
        status['contract_address'] = BlockchainConfig.CONTRACT_ADDRESS[:10] + '...' if BlockchainConfig.CONTRACT_ADDRESS else None
        status['network'] = 'Polygon Amoy' if 'amoy' in BlockchainConfig.POLYGON_AMOY_RPC_URL.lower() else 'Local'
    
    return jsonify(status), 200


@blockchain_bp.route('/record-transaction', methods=['POST'])
def record_transaction_route():
    """Record transaction on blockchain"""
    try:
        if not BLOCKCHAIN_AVAILABLE:
            return jsonify({'error': 'Blockchain service not available'}), 503
        
        data = request.get_json()
        required_fields = ['voice_hash', 'shop_address', 'amount', 'tx_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        blockchain_service = get_blockchain_service()
        
        tx_hash = blockchain_service.record_transaction(
            voice_hash=data['voice_hash'],
            shop_address=data['shop_address'],
            amount=int(data['amount'] * 100),  # Convert to smallest unit
            tx_type=data['tx_type']
        )
        
        return jsonify({
            'tx_hash': tx_hash,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error recording transaction on blockchain: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@blockchain_bp.route('/transaction/<tx_id>', methods=['GET'])
def get_blockchain_transaction_route(tx_id):
    """Get blockchain transaction"""
    try:
        if not BLOCKCHAIN_AVAILABLE:
            return jsonify({'error': 'Blockchain service not available'}), 503
        
        blockchain_service = get_blockchain_service()
        transaction = blockchain_service.get_transaction(tx_id)
        
        return jsonify({
            'transaction': transaction,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error getting blockchain transaction: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@blockchain_bp.route('/register-shopkeeper', methods=['POST'])
def register_shopkeeper_blockchain_route():
    """Register shopkeeper on blockchain"""
    try:
        if not BLOCKCHAIN_AVAILABLE:
            return jsonify({'error': 'Blockchain service not available'}), 503
        
        data = request.get_json()
        if 'address' not in data:
            return jsonify({'error': 'Missing required field: address'}), 400
        
        blockchain_service = get_blockchain_service()
        tx_hash = blockchain_service.register_shopkeeper(data['address'])
        
        return jsonify({
            'tx_hash': tx_hash,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error registering shopkeeper on blockchain: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@blockchain_bp.route('/credit-score/<shopkeeper_id>', methods=['GET'])
def get_blockchain_credit_score_route(shopkeeper_id):
    """Get credit score from blockchain"""
    try:
        if not BLOCKCHAIN_AVAILABLE:
            return jsonify({'error': 'Blockchain service not available'}), 503
        
        # Get shopkeeper wallet address
        from database.models import Shopkeeper
        try:
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            return jsonify({'error': 'Shopkeeper not found'}), 404
        
        blockchain_service = get_blockchain_service()
        credit_score_data = blockchain_service.get_credit_score(shopkeeper.wallet_address)
        
        return jsonify({
            'credit_score': credit_score_data,
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error getting blockchain credit score: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

