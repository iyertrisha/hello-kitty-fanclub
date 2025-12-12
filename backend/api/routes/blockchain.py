"""
Blockchain routes - Integration with Trisha's contract_service.py
"""
from flask import Blueprint, request, jsonify
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

blockchain_bp = Blueprint('blockchain', __name__)

# Import blockchain service
try:
    blockchain_path = Path(__file__).parent.parent.parent / 'blockchain'
    sys.path.insert(0, str(blockchain_path))
    from utils.contract_service import BlockchainService
    from config import BlockchainConfig
    BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Blockchain service not available: {e}")
    BlockchainService = None
    BLOCKCHAIN_AVAILABLE = False


def get_blockchain_service():
    """Get initialized blockchain service"""
    if not BLOCKCHAIN_AVAILABLE:
        raise Exception("Blockchain service not available")
    
    if not BlockchainConfig.CONTRACT_ADDRESS:
        raise Exception("Contract address not configured")
    
    return BlockchainService(
        rpc_url=BlockchainConfig.POLYGON_AMOY_RPC_URL,
        private_key=BlockchainConfig.PRIVATE_KEY,
        contract_address=BlockchainConfig.CONTRACT_ADDRESS
    )


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

