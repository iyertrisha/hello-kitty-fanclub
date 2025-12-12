"""
Transaction routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from services.transaction import (
    create_transaction,
    get_transactions,
    get_transaction_by_id,
    update_transaction_status
)
from api.middleware.validation import validate_request, validate_query_params
from api.middleware.error_handler import ValidationError, NotFoundError
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('', methods=['POST'])
@validate_request(required_fields=['type', 'amount', 'shopkeeper_id', 'customer_id'])
def create_transaction_route():
    """Create new transaction"""
    try:
        data = request.validated_data
        transaction = create_transaction(data)
        
        return jsonify({
            'id': str(transaction.id),
            'type': transaction.type,
            'amount': transaction.amount,
            'status': transaction.status,
            'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None
        }), 201
    except ValidationError as e:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {e}", exc_info=True)
        raise ValidationError(f"Failed to create transaction: {str(e)}")


@transactions_bp.route('', methods=['GET'])
@validate_query_params(param_types={'page': int, 'page_size': int})
def get_transactions_route():
    """Get transactions with filtering"""
    try:
        # Parse filters
        filters = {}
        if 'shopkeeper_id' in request.args:
            filters['shopkeeper_id'] = request.args.get('shopkeeper_id')
        if 'customer_id' in request.args:
            filters['customer_id'] = request.args.get('customer_id')
        if 'type' in request.args:
            filters['type'] = request.args.get('type')
        if 'status' in request.args:
            filters['status'] = request.args.get('status')
        if 'date_from' in request.args:
            filters['date_from'] = datetime.fromisoformat(request.args.get('date_from'))
        if 'date_to' in request.args:
            filters['date_to'] = datetime.fromisoformat(request.args.get('date_to'))
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        page_size = min(request.args.get('page_size', 20, type=int), 100)
        
        transactions, total_count, page, page_size = get_transactions(filters, page, page_size)
        
        result = []
        for transaction in transactions:
            result.append({
                'id': str(transaction.id),
                'type': transaction.type,
                'amount': transaction.amount,
                'shopkeeper_id': str(transaction.shopkeeper_id.id),
                'customer_id': str(transaction.customer_id.id),
                'product_id': str(transaction.product_id.id) if transaction.product_id else None,
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,
                'status': transaction.status,
                'blockchain_tx_id': transaction.blockchain_tx_id,
                'transcript_hash': transaction.transcript_hash
            })
        
        return jsonify({
            'transactions': result,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting transactions: {e}", exc_info=True)
        raise ValidationError(f"Failed to get transactions: {str(e)}")


@transactions_bp.route('/<transaction_id>', methods=['GET'])
def get_transaction_route(transaction_id):
    """Get transaction by ID"""
    try:
        transaction = get_transaction_by_id(transaction_id)
        
        return jsonify({
            'id': str(transaction.id),
            'type': transaction.type,
            'amount': transaction.amount,
            'shopkeeper_id': str(transaction.shopkeeper_id.id),
            'customer_id': str(transaction.customer_id.id),
            'product_id': str(transaction.product_id.id) if transaction.product_id else None,
            'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,
            'status': transaction.status,
            'blockchain_tx_id': transaction.blockchain_tx_id,
            'blockchain_block_number': transaction.blockchain_block_number,
            'transcript_hash': transaction.transcript_hash,
            'notes': transaction.notes
        }), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction: {e}", exc_info=True)
        raise ValidationError(f"Failed to get transaction: {str(e)}")


@transactions_bp.route('/<transaction_id>/status', methods=['PUT'])
@validate_request(required_fields=['status'])
def update_transaction_status_route(transaction_id):
    """Update transaction status"""
    try:
        data = request.validated_data
        status = data['status']
        
        blockchain_tx_id = data.get('blockchain_tx_id')
        blockchain_block_number = data.get('blockchain_block_number')
        
        transaction = update_transaction_status(
            transaction_id,
            status,
            blockchain_tx_id,
            blockchain_block_number
        )
        
        return jsonify({
            'id': str(transaction.id),
            'status': transaction.status,
            'blockchain_tx_id': transaction.blockchain_tx_id
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction status: {e}", exc_info=True)
        raise ValidationError(f"Failed to update transaction status: {str(e)}")


@transactions_bp.route('/transcribe', methods=['POST'])
def transcribe_audio_route():
    """Upload audio for transcription (calls Trisha's Google Speech API)"""
    try:
        if 'audio_file' not in request.files:
            raise ValidationError("No audio file provided")
        
        audio_file = request.files['audio_file']
        
        # Import Google Speech API integration (Trisha's work)
        # This will be available when Trisha completes her integration
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'integrations' / 'google-speech'))
            from google_speech import transcribe_audio_bytes
            
            # Read audio file bytes
            audio_bytes = audio_file.read()
            
            # Transcribe
            language_code = request.form.get('language_code', 'hi-IN')
            result = transcribe_audio_bytes(audio_bytes, language_code)
            
            return jsonify({
                'transcript': result.get('transcript', ''),
                'confidence': result.get('confidence', 0.0),
                'language': result.get('language', language_code)
            }), 200
        except ImportError:
            # Fallback if Google Speech API not available
            logger.warning("Google Speech API integration not available")
            return jsonify({
                'transcript': '',
                'confidence': 0.0,
                'language': 'hi-IN',
                'error': 'Google Speech API integration not available'
            }), 200
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}", exc_info=True)
        raise ValidationError(f"Failed to transcribe audio: {str(e)}")

