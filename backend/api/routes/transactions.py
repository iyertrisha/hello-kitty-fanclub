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
@validate_request(required_fields=['shopkeeper_id'])  # Only shopkeeper_id is always required
def create_transaction_route():
    """
    Create new transaction with optional transcript for STT verification.
    
    If 'transcript' field is provided, uses verification service and blockchain integration.
    Otherwise, creates transaction directly in MongoDB (backward compatible).
    """
    import json
    
    # #region agent log
    import os
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({'location':'transactions.py:27','message':'Route handler entry','data':{'method':request.method,'path':request.path,'hasJson':request.is_json},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'A'})+'\n')
    except:
        pass
    # #endregion
    
    try:
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'transactions.py:35','message':'Before validation check','data':{'hasValidatedData':hasattr(request,'validated_data')},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'B'})+'\n')
        except:
            pass
        # #endregion
        
        data = request.validated_data
        
        # Log transaction creation attempt
        logger.info("=" * 60)
        logger.info("🔄 Creating Transaction")
        logger.info(f"   Type: {data.get('type')}")
        logger.info(f"   Amount: {data.get('amount')}")
        logger.info(f"   Shopkeeper ID: {data.get('shopkeeper_id')}")
        logger.info(f"   Customer ID: {data.get('customer_id')}")
        if data.get('description'):
            logger.info(f"   Description: {data.get('description')}")
        if data.get('transcript'):
            logger.info(f"   Transcript: {data.get('transcript')[:100]}...")
        logger.info("=" * 60)
        
        # #region agent log
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'location':'transactions.py:36','message':'Validation passed','data':{'dataKeys':list(data.keys()) if data else []},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'C'})+'\n')
        except:
            pass
        # #endregion
        
        # Check if transcript is provided (STT flow)
        has_transcript = 'transcript' in data and data.get('transcript')
        
        # Auto-parse transcript if provided and fields are missing
        if has_transcript:
            # Check if we need to parse (missing type, amount, or other key fields)
            needs_parsing = (
                not data.get('type') or
                not data.get('amount') or
                (data.get('type') == 'sale' and not data.get('product_name'))
            )
            
            if needs_parsing:
                try:
                    from services.voice_parser import parse_transcript
                    
                    # Get language from request (default to en-IN)
                    language = data.get('language', 'en-IN')
                    shopkeeper_id = data.get('shopkeeper_id')
                    
                    logger.info(f"🔍 Auto-parsing transcript in {language}...")
                    parsed_data = parse_transcript(
                        transcript=data.get('transcript'),
                        language=language,
                        shopkeeper_id=shopkeeper_id
                    )
                    
                    # Merge parsed fields with provided fields (provided fields take precedence)
                    if not data.get('type') and parsed_data.get('type'):
                        data['type'] = parsed_data['type']
                        logger.info(f"   Parsed type: {parsed_data['type']}")
                    
                    if not data.get('amount') and parsed_data.get('amount'):
                        # Convert rupees to paise if needed
                        amount_rupees = parsed_data['amount']
                        data['amount'] = int(amount_rupees * 100)  # Convert to paise
                        logger.info(f"   Parsed amount: ₹{amount_rupees} ({data['amount']} paise)")
                    
                    if not data.get('customer_id') and parsed_data.get('customer_id'):
                        data['customer_id'] = parsed_data['customer_id']
                        logger.info(f"   Parsed customer_id: {parsed_data['customer_id']}")
                    
                    # Always copy customer_name if available (even if customer_id is None, for new customers)
                    if not data.get('customer_name') and parsed_data.get('customer_name'):
                        data['customer_name'] = parsed_data['customer_name']
                        logger.info(f"   Parsed customer_name: {parsed_data['customer_name']}")
                    
                    if data.get('type') == 'sale':
                        if not data.get('product_name') and parsed_data.get('product'):
                            data['product_name'] = parsed_data['product']
                            logger.info(f"   Parsed product: {parsed_data['product']}")
                        
                        if not data.get('quantity') and parsed_data.get('quantity'):
                            data['quantity'] = parsed_data['quantity']
                            logger.info(f"   Parsed quantity: {parsed_data['quantity']}")
                        
                        if not data.get('unit') and parsed_data.get('unit'):
                            data['unit'] = parsed_data['unit']
                            logger.info(f"   Parsed unit: {parsed_data['unit']}")
                        
                        if not data.get('product_price') and parsed_data.get('price_per_unit'):
                            data['product_price'] = parsed_data['price_per_unit']
                            logger.info(f"   Parsed price_per_unit: ₹{parsed_data['price_per_unit']}")
                    
                    logger.info("✅ Auto-parsing completed")
                except Exception as e:
                    logger.warning(f"⚠️  Auto-parsing failed: {e}. Continuing with provided fields only.")
        
        # Validate required fields after parsing (if not provided and not parsed)
        if not data.get('type'):
            raise ValidationError("'type' field is required (or provide 'transcript' for auto-parsing)")
        if not data.get('amount'):
            raise ValidationError("'amount' field is required (or provide 'transcript' for auto-parsing)")
        if not data.get('customer_id'):
            raise ValidationError("'customer_id' field is required (or provide 'transcript' for auto-parsing)")
        
        if has_transcript:
            # Use verification flow with blockchain integration
            logger.info("📝 Using verification flow with blockchain integration")
            transaction = create_transaction_with_verification(data)
            
            # Build response with verification details
            response_data = {
                'id': str(transaction.id),
                'type': transaction.type,
                'amount': transaction.amount,
                'description': getattr(transaction, 'notes', '') or '',  # Add description
                'date': transaction.timestamp.isoformat() if transaction.timestamp else datetime.now().isoformat(),  # Add date
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,  # Keep for compatibility
                'status': transaction.status,
                'transcription': getattr(transaction, 'transcript', None),  # Add transcription
                'synced': True,  # Add synced flag
                'audioPath': None,  # For Flutter compatibility
                'customer_id': str(transaction.customer_id.id) if transaction.customer_id else None,
                'customer_name': data.get('customer_name') or (transaction.customer_id.name if transaction.customer_id else None),  # Use parsed name or customer name from DB
                'shopkeeper_id': str(transaction.shopkeeper_id.id) if transaction.shopkeeper_id else None,
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
            
            logger.info("✅ Transaction created with verification")
            logger.info(f"   Transaction ID: {transaction.id}")
            logger.info(f"   Status: {transaction.status}")
            logger.info(f"   Verification Status: {transaction.verification_status}")
            if transaction.blockchain_tx_id:
                logger.info(f"   Blockchain TX ID: {transaction.blockchain_tx_id}")
        else:
            # Backward compatible: direct MongoDB creation without verification
            logger.info("📝 Creating transaction directly (no verification)")
            transaction = create_transaction(data)
            
            response_data = {
                'id': str(transaction.id),
                'type': transaction.type,
                'amount': transaction.amount,
                'description': getattr(transaction, 'notes', '') or '',  # Add description
                'date': transaction.timestamp.isoformat() if transaction.timestamp else datetime.now().isoformat(),  # Add date
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,  # Keep for compatibility
                'status': transaction.status,
                'transcription': getattr(transaction, 'transcript', None),  # Add transcription
                'synced': True,  # Add synced flag
                'audioPath': None,  # For Flutter compatibility
                'customer_id': str(transaction.customer_id.id) if transaction.customer_id else None,
                'customer_name': data.get('customer_name') or (transaction.customer_id.name if transaction.customer_id else None),  # Use parsed name or customer name from DB
                'shopkeeper_id': str(transaction.shopkeeper_id.id) if transaction.shopkeeper_id else None,
            }
            
            logger.info("✅ Transaction created successfully")
            logger.info(f"   Transaction ID: {transaction.id}")
            logger.info(f"   Status: {transaction.status}")
        
        logger.info("=" * 60)
        
        # Wrap in 'data' key for Flutter app compatibility
        return jsonify({'data': response_data}), 201
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
                'description': getattr(transaction, 'notes', '') or '',  # Map notes to description
                'date': transaction.timestamp.isoformat() if transaction.timestamp else datetime.now().isoformat(),  # Add date field
                'timestamp': transaction.timestamp.isoformat() if transaction.timestamp else None,  # Keep for compatibility
                'shopkeeper_id': str(transaction.shopkeeper_id.id),
                'customer_id': str(transaction.customer_id.id),
                'product_id': str(transaction.product_id.id) if transaction.product_id else None,
                'status': transaction.status,
                'transcription': getattr(transaction, 'transcript', None),  # Add transcription
                'synced': True,  # Backend data is always synced
                'audioPath': None,  # For Flutter compatibility
                'blockchain_tx_id': transaction.blockchain_tx_id,
                'transcript_hash': transaction.transcript_hash,
                'verification_status': transaction.verification_status,
                'fraud_score': transaction.fraud_score,
                'fraud_risk_level': transaction.fraud_risk_level
            })
        
        return jsonify({
            'data': result,  # Change from 'transactions' to 'data'
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
    """
    Upload audio for transcription using speech recognition.
    
    Accepts audio file upload and returns transcribed text.
    Supports Hindi (hi-IN) and English (en-IN) with automatic fallback.
    
    Request:
        - Form data with 'audio' or 'audio_file' field (multipart/form-data)
        - Optional 'language' or 'language_code' parameter (default: 'hi-IN')
    
    Response:
        {
            "transcription": "...",  // For Flutter compatibility
            "transcript": "...",     // For backward compatibility
            "confidence": 0.9,
            "language": "hi-IN"
        }
    """
    import tempfile
    import os
    
    temp_file_path = None
    
    try:
        # Accept both 'audio' (Flutter) and 'audio_file' (backward compatibility)
        audio_file = None
        if 'audio' in request.files:
            audio_file = request.files['audio']
        elif 'audio_file' in request.files:
            audio_file = request.files['audio_file']
        
        if not audio_file:
            raise ValidationError("No audio file provided. Use 'audio' or 'audio_file' field.")
        
        if audio_file.filename == '':
            raise ValidationError("No file selected")
        
        # Get language code (support both 'language' and 'language_code' params)
        language_code = request.form.get('language') or request.form.get('language_code', 'en-IN')
        
        # Validate language code (supported: hi-IN, en-IN, kn-IN)
        supported_languages = ['hi-IN', 'en-IN', 'kn-IN']
        if language_code not in supported_languages:
            logger.warning(f"Unsupported language code: {language_code}, defaulting to en-IN")
            language_code = 'en-IN'
        
        # Determine file extension from filename
        filename = audio_file.filename or 'audio.m4a'
        file_ext = Path(filename).suffix.lower() or '.m4a'
        
        # Save uploaded file to temporary location
        temp_file = tempfile.NamedTemporaryFile(suffix=file_ext, delete=False)
        temp_file_path = temp_file.name
        audio_file.save(temp_file_path)
        temp_file.close()
        
        logger.info(f"Saved uploaded audio to: {temp_file_path} (format: {file_ext})")
        
        # Import and use speech transcription module
        try:
            from integrations.speech_transcribe import transcribe_audio_file, is_available
            
            if not is_available():
                logger.warning("Speech recognition not available")
                return jsonify({
                    'transcription': '',
                    'transcript': '',
                    'confidence': 0.0,
                    'language': language_code,
                    'error': 'Speech recognition not available. Install: pip install SpeechRecognition pydub'
                }), 200
            
            # Transcribe audio file
            result = transcribe_audio_file(temp_file_path, language=language_code)
            
            # Check for errors
            if result.get('error'):
                logger.warning(f"Transcription error: {result['error']}")
                return jsonify({
                    'transcription': result.get('transcript', ''),
                    'transcript': result.get('transcript', ''),
                    'confidence': result.get('confidence', 0.0),
                    'language': result.get('language', language_code),
                    'error': result['error']
                }), 200
            
            # Success response with both 'transcription' (Flutter) and 'transcript' (backward compat)
            transcript_text = result.get('transcript', '')
            return jsonify({
                'transcription': transcript_text,  # Flutter expects this key
                'transcript': transcript_text,     # Backward compatibility
                'confidence': result.get('confidence', 0.9),
                'language': result.get('language', language_code)
            }), 200
            
        except ImportError as e:
            logger.error(f"Failed to import speech transcription module: {e}")
            return jsonify({
                'transcription': '',
                'transcript': '',
                'confidence': 0.0,
                'language': language_code,
                'error': f'Speech transcription module not available: {str(e)}'
            }), 200
            
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}", exc_info=True)
        raise ValidationError(f"Failed to transcribe audio: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temp file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")


@transactions_bp.route('/parse', methods=['POST'])
def parse_transcript_route():
    """
    Parse voice transcript to extract transaction fields.
    
    Accepts transcript and language, returns parsed transaction fields.
    
    Request:
        {
            "transcript": "string",
            "language": "hi-IN" | "en-IN" | "kn-IN",
            "shopkeeper_id": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "data": {
                "type": "credit" | "sale",
                "amount": float,
                "customer_id": "string" | null,
                "customer_name": "string" | null,
                "product": "string" | null,
                "quantity": float | null,
                "unit": "string" | null,
                "price_per_unit": float | null,
                "confirmation_text": "string"
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        transcript = data.get('transcript')
        if not transcript:
            raise ValidationError("'transcript' field is required")
        
        language = data.get('language', 'en-IN')
        shopkeeper_id = data.get('shopkeeper_id')
        
        # Validate language code
        supported_languages = ['hi-IN', 'en-IN', 'kn-IN']
        if language not in supported_languages:
            logger.warning(f"Unsupported language code: {language}, defaulting to en-IN")
            language = 'en-IN'
        
        # Import parser service
        try:
            from services.voice_parser import parse_transcript
        except ImportError as e:
            logger.error(f"Failed to import voice parser: {e}")
            raise ValidationError(f"Voice parser service not available: {str(e)}")
        
        # Parse transcript
        logger.info(f"Parsing transcript in {language}: {transcript[:100]}...")
        # #region agent log
        import json, os
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.cursor', 'debug.log')
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'location':'transactions.py:546','message':'Parse request received','data':{'transcript':transcript[:100],'language':language},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H4'})+'\n')
        except: pass
        # #endregion
        parsed_data = parse_transcript(
            transcript=transcript,
            language=language,
            shopkeeper_id=shopkeeper_id
        )
        
        logger.info(f"Parsed transaction: type={parsed_data.get('type')}, amount={parsed_data.get('amount')}")
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'location':'transactions.py:553','message':'Parse result before return','data':{'customer_name':parsed_data.get('customer_name'),'customer_id':parsed_data.get('customer_id'),'type':parsed_data.get('type')},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H4'})+'\n')
        except: pass
        # #endregion
        
        return jsonify({
            'success': True,
            'data': parsed_data
        }), 200
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error parsing transcript: {e}", exc_info=True)
        raise ValidationError(f"Failed to parse transcript: {str(e)}")

