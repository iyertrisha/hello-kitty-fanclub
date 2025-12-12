"""
Test Flask API for Kirana Store Management System

Simulates Vineet's Flask API endpoints for independent testing.
Use this to test the verification flow before the real API is ready.

Run: python test_api.py
Test: curl -X POST http://localhost:5001/test/transactions -H "Content-Type: application/json" -d '{"transcript": "test"}'
"""

import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.fraud_detection import get_fraud_detection_service
from services.transaction_verification import (
    TransactionVerificationService,
    VerificationStatus,
    StorageLocation
)
from blockchain.mock_data import (
    generate_shopkeeper_history,
    generate_transaction_data,
    get_sample_credit_data,
    get_sample_sale_data,
    SAMPLE_TRANSCRIPTS
)

# Try to import blockchain service (optional)
try:
    from blockchain.utils.contract_service import BlockchainService
    from blockchain.config import config
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    print("⚠️  Blockchain service not available - running in mock mode")

app = Flask(__name__)
CORS(app)

# Initialize services
fraud_service = get_fraud_detection_service()
verification_service = None
blockchain_service = None


def init_blockchain():
    """Initialize blockchain service if available"""
    global blockchain_service, verification_service
    
    if BLOCKCHAIN_AVAILABLE:
        try:
            config.validate(require_contract=True)
            blockchain_service = BlockchainService(
                rpc_url=config.RPC_URL,
                private_key=config.PRIVATE_KEY,
                contract_address=config.CONTRACT_ADDRESS
            )
            verification_service = TransactionVerificationService(blockchain_service)
            print("✅ Blockchain service initialized")
        except Exception as e:
            print(f"⚠️  Blockchain init failed: {e}")
            verification_service = TransactionVerificationService(None)
    else:
        verification_service = TransactionVerificationService(None)


# ============================================================
# TEST ENDPOINTS (Simulate Vineet's API)
# ============================================================

@app.route('/test/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Kirana Test API',
        'blockchain_available': blockchain_service is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/test/transactions', methods=['POST'])
def create_transaction():
    """
    Create a new transaction (simulates Vineet's POST /api/transactions)
    
    Request Body:
    {
        "transcript": "मुझे 500 रुपये का क्रेडिट चाहिए",
        "type": "credit" | "sale" | "repay",
        "amount": 50000,  // in paise
        "customer_id": "customer_123",
        "shopkeeper_id": "shopkeeper_456",
        "customer_confirmed": true,
        "language": "hi-IN"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        # Generate mock shopkeeper history if not provided
        shopkeeper_history = data.get('shopkeeper_history') or generate_shopkeeper_history()
        
        # Add shopkeeper history to transaction data
        transaction_data = {
            **data,
            'shopkeeper_history': shopkeeper_history
        }
        
        # Determine transaction type
        tx_type = data.get('type', 'credit')
        
        # Verify transaction
        if tx_type == 'credit':
            result = verification_service.verify_credit_transaction(transaction_data)
        elif tx_type == 'sale':
            result = verification_service.verify_sales_transaction(transaction_data)
        else:
            # Treat repay like credit for now
            result = verification_service.verify_credit_transaction(transaction_data)
        
        # Prepare response
        response = {
            'success': True,
            'transaction_id': f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'verification': {
                'status': result.status.value,
                'storage_location': result.storage_location.value,
                'transcript_hash': result.transcript_hash,
                'should_write_to_blockchain': result.should_write_to_blockchain,
                'errors': result.errors,
                'warnings': result.warnings
            },
            'fraud_check': result.fraud_check,
            'metadata': result.metadata
        }
        
        # Write to blockchain if verified
        if result.should_write_to_blockchain and blockchain_service:
            tx_type_int = {'sale': 0, 'credit': 1, 'repay': 2}.get(tx_type, 1)
            blockchain_result = verification_service.write_to_blockchain(result, tx_type_int)
            response['blockchain'] = blockchain_result
        
        return jsonify(response), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test/verify-transaction', methods=['POST'])
def verify_transaction():
    """
    Direct verification endpoint for testing
    
    Request Body: Same as /test/transactions
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        # Generate mock data if transcript provided
        transcript = data.get('transcript', '')
        tx_type = data.get('type', 'credit')
        
        shopkeeper_history = data.get('shopkeeper_history') or generate_shopkeeper_history()
        
        transaction_data = {
            'transcript': transcript,
            'type': tx_type,
            'amount': data.get('amount', 50000),
            'customer_id': data.get('customer_id', 'test_customer'),
            'shopkeeper_id': data.get('shopkeeper_id', 'test_shopkeeper'),
            'customer_confirmed': data.get('customer_confirmed', False),
            'language': data.get('language', 'hi-IN'),
            'shopkeeper_history': shopkeeper_history
        }
        
        # Add product info for sales
        if tx_type == 'sale':
            transaction_data['product'] = data.get('product', 'Test Product')
            transaction_data['price'] = data.get('price', data.get('amount', 1000))
            transaction_data['quantity'] = data.get('quantity', 1)
        
        # Verify
        if tx_type == 'credit' or tx_type == 'repay':
            result = verification_service.verify_credit_transaction(transaction_data)
        else:
            result = verification_service.verify_sales_transaction(transaction_data)
        
        return jsonify({
            'status': result.status.value,
            'storage_location': result.storage_location.value,
            'transcript_hash': result.transcript_hash,
            'should_write_to_blockchain': result.should_write_to_blockchain,
            'fraud_check': result.fraud_check,
            'errors': result.errors,
            'warnings': result.warnings,
            'metadata': result.metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    Get transaction by ID (simulates Vineet's GET /api/transactions/:id)
    
    Note: Returns mock data since we don't have a database yet
    """
    # Return mock transaction data
    return jsonify({
        'id': transaction_id,
        'type': 'credit',
        'amount': 50000,
        'customer_id': 'customer_123',
        'shopkeeper_id': 'shopkeeper_456',
        'status': 'verified',
        'transcript_hash': 'a1b2c3d4e5f6...',
        'blockchain_tx_id': None,
        'created_at': datetime.now().isoformat()
    })


@app.route('/test/blockchain/record', methods=['POST'])
def record_to_blockchain():
    """
    Direct blockchain write endpoint for testing
    
    Request Body:
    {
        "voice_hash": "abc123...",
        "shop_address": "0x...",
        "amount": 50000,
        "tx_type": 1  // 0=SALE, 1=CREDIT, 2=REPAY
    }
    """
    if not blockchain_service:
        return jsonify({'error': 'Blockchain service not available'}), 503
    
    try:
        data = request.get_json()
        
        voice_hash = data.get('voice_hash')
        shop_address = data.get('shop_address') or blockchain_service.address
        amount = data.get('amount', 10000)
        tx_type = data.get('tx_type', 1)
        
        if not voice_hash:
            return jsonify({'error': 'voice_hash required'}), 400
        
        result = blockchain_service.record_transaction(
            voice_hash=voice_hash,
            shop_address=shop_address,
            amount=amount,
            tx_type=tx_type
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/test/blockchain/status', methods=['GET'])
def blockchain_status():
    """Get blockchain connection status"""
    if not blockchain_service:
        return jsonify({
            'connected': False,
            'error': 'Blockchain service not initialized'
        })
    
    try:
        balance = blockchain_service.get_account_balance_eth()
        next_tx_id = blockchain_service.get_next_transaction_id()
        
        return jsonify({
            'connected': True,
            'address': blockchain_service.address,
            'contract_address': blockchain_service.contract_address,
            'balance_eth': balance,
            'next_transaction_id': next_tx_id
        })
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e)
        })


# ============================================================
# MOCK DATA ENDPOINTS (For frontend testing)
# ============================================================

@app.route('/test/mock/credit', methods=['GET'])
def get_mock_credit():
    """Get mock credit transaction data"""
    language = request.args.get('language', 'hi-IN')
    return jsonify(get_sample_credit_data(language))


@app.route('/test/mock/sale', methods=['GET'])
def get_mock_sale():
    """Get mock sale transaction data"""
    language = request.args.get('language', 'hi-IN')
    return jsonify(get_sample_sale_data(language))


@app.route('/test/mock/history', methods=['GET'])
def get_mock_history():
    """Get mock shopkeeper history"""
    return jsonify(generate_shopkeeper_history())


@app.route('/test/mock/transcripts', methods=['GET'])
def get_mock_transcripts():
    """Get sample transcripts for testing"""
    return jsonify(SAMPLE_TRANSCRIPTS)


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🧪 KIRANA TEST API")
    print("=" * 60)
    
    # Initialize blockchain
    init_blockchain()
    
    print("\n📡 Available Endpoints:")
    print("  GET  /test/health              - Health check")
    print("  POST /test/transactions        - Create transaction")
    print("  POST /test/verify-transaction  - Verify transaction")
    print("  GET  /test/transactions/:id    - Get transaction")
    print("  POST /test/blockchain/record   - Direct blockchain write")
    print("  GET  /test/blockchain/status   - Blockchain status")
    print("  GET  /test/mock/credit         - Mock credit data")
    print("  GET  /test/mock/sale           - Mock sale data")
    print("  GET  /test/mock/history        - Mock shopkeeper history")
    print("  GET  /test/mock/transcripts    - Sample transcripts")
    
    print("\n🚀 Starting server on http://localhost:5001")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

