"""
Transaction routes
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from services.transaction import (
    create_transaction,
    create_transaction_with_verification,
    get_transactions,
    get_transaction_by_id,
    update_transaction_status,
    update_transaction_with_customer_confirmation
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
    """
    Create new transaction with optional transcript for STT verification.
    
    If 'transcript' field is provided, uses verification service and blockchain integration.
    Otherwise, creates transaction directly in MongoDB (backward compatible).
    """
    try:
        data = request.validated_data
        
        # Check if transcript is provided (STT flow)
        has_transcript = 'transcript' in data and data.get('transcript')
        
        if has_transcript:
            # Use verification flow with blockchain integration
            transaction = create_transaction_with_verification(data)
            
            # Build response with verification details
            response_data = {
                'id': str(transaction.id),
                'type': transaction.type,
                'amount': transaction.amount,
                'status': transaction.status,
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,
                'verification': {
                    'status': transaction.verification_status,
                    'fraud_score': transaction.fraud_score,
                    'fraud_risk_level': transaction.fraud_risk_level,
                    'blockchain_tx_id': transaction.blockchain_tx_id,
                    'blockchain_block_number': transaction.blockchain_block_number
                }
            }
            
            # Include verification metadata if available
            if transaction.verification_metadata:
                verification_meta = transaction.verification_metadata
                response_data['verification']['storage_location'] = verification_meta.get('storage_location')
                response_data['verification']['warnings'] = verification_meta.get('warnings', [])
                response_data['verification']['errors'] = verification_meta.get('errors', [])
        else:
            # Backward compatible: direct MongoDB creation without verification
            transaction = create_transaction(data)
            
            response_data = {
                'id': str(transaction.id),
                'type': transaction.type,
                'amount': transaction.amount,
                'status': transaction.status,
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None
            }
        
        return jsonify(response_data), 201
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
                'transcript_hash': transaction.transcript_hash,
                'verification_status': transaction.verification_status,
                'fraud_score': transaction.fraud_score,
                'fraud_risk_level': transaction.fraud_risk_level
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
            'transcript': transaction.transcript,
            'transcript_hash': transaction.transcript_hash,
            'verification_status': transaction.verification_status,
            'fraud_score': transaction.fraud_score,
            'fraud_risk_level': transaction.fraud_risk_level,
            'verification_metadata': transaction.verification_metadata,
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
    """
    Update transaction status.
    
    If 'customer_confirmed' is True and transaction is pending, re-runs verification
    and writes to blockchain if verified.
    """
    try:
        data = request.validated_data
        status = data['status']
        
        # Check if this is a customer confirmation
        customer_confirmed = data.get('customer_confirmed', False)
        
        # If customer confirmed and status is being set to verified, re-verify
        if customer_confirmed and status == 'verified':
            transaction = update_transaction_with_customer_confirmation(
                transaction_id,
                customer_confirmed=True
            )
        else:
            # Standard status update
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
            'verification_status': transaction.verification_status,
            'blockchain_tx_id': transaction.blockchain_tx_id,
            'blockchain_block_number': transaction.blockchain_block_number
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
        # Accept both 'audio' (from Flutter) and 'audio_file' (backward compatibility)
        audio_file = None
        if 'audio' in request.files:
            audio_file = request.files['audio']
        elif 'audio_file' in request.files:
            audio_file = request.files['audio_file']
        else:
            raise ValidationError("No audio file provided. Expected 'audio' or 'audio_file' field.")
        
        # Import Google Speech API integration (Trisha's work)
        # This will be available when Trisha completes her integration
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'integrations' / 'google-speech'))
            from google_speech import transcribe_audio_bytes
            
            # Read audio file bytes
            audio_bytes = audio_file.read()
            
            # Get language from form data or query params (Flutter sends as 'language' in form)
            language_code = request.form.get('language') or request.form.get('language_code') or 'hi-IN'
            result = transcribe_audio_bytes(audio_bytes, language_code)
            
            # Return both 'transcript' and 'transcription' for compatibility
            transcript_text = result.get('transcript', '')
            return jsonify({
                'transcript': transcript_text,
                'transcription': transcript_text,  # Flutter expects 'transcription'
                'confidence': result.get('confidence', 0.0),
                'language': result.get('language', language_code)
            }), 200
        except ImportError:
            # Fallback if Google Speech API not available
            logger.warning("Google Speech API integration not available")
            return jsonify({
                'transcript': '',
                'transcription': '',  # Flutter expects 'transcription'
                'confidence': 0.0,
                'language': 'hi-IN',
                'error': 'Google Speech API integration not available'
            }), 200
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}", exc_info=True)
        raise ValidationError(f"Failed to transcribe audio: {str(e)}")


@transactions_bp.route('/parse', methods=['POST'])
def parse_transcript_route():
    """
    Parse voice transcript to extract transaction details.
    Uses voice_parser.py for Hindi, English, and Kannada support.
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        transcript = data.get('transcript')
        if not transcript:
            raise ValidationError("'transcript' field is required")
        
        language = data.get('language', 'hi-IN')
        shopkeeper_id = data.get('shopkeeper_id')
        
        # Import voice parser
        try:
            blockchain_dir = Path(__file__).parent.parent.parent / 'blockchain'
            sys.path.insert(0, str(blockchain_dir))
            from voice_parser import parse_transcript
            
            # Parse the transcript
            parsed_result = parse_transcript(
                transcript=transcript,
                language=language,
                shopkeeper_id=shopkeeper_id,
                customer_list=None,  # Will be fetched from database
                product_map=None  # Will use default mapping
            )
            
            # Convert amount from rupees to paise if needed (parser returns rupees)
            # But Flutter expects rupees, so we keep it as is
            amount = parsed_result.get('amount')
            if amount is not None:
                # Ensure amount is a number
                if isinstance(amount, (int, float)):
                    parsed_result['amount'] = float(amount)
            
            # Return in format Flutter expects
            return jsonify({
                'success': True,
                'data': {
                    'type': parsed_result.get('type', 'credit'),
                    'amount': parsed_result.get('amount'),
                    'customer_id': parsed_result.get('customer_id'),
                    'customer_name': parsed_result.get('customer_name'),
                    'product': parsed_result.get('product'),
                    'quantity': parsed_result.get('quantity'),
                    'unit': parsed_result.get('unit'),
                    'price_per_unit': parsed_result.get('price_per_unit'),
                    'is_buying': parsed_result.get('is_buying', False),
                    'transaction_subtype': parsed_result.get('transaction_subtype'),
                    'confirmation_text': parsed_result.get('confirmation_text'),
                    'confirmation_text_hindi': parsed_result.get('confirmation_text_hindi'),
                }
            }), 200
            
        except ImportError as e:
            logger.error(f"Failed to import voice parser: {e}", exc_info=True)
            raise ValidationError(f"Voice parser not available: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing transcript: {e}", exc_info=True)
            raise ValidationError(f"Failed to parse transcript: {str(e)}")
            
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error in parse endpoint: {e}", exc_info=True)
        raise ValidationError(f"Failed to parse transcript: {str(e)}")

