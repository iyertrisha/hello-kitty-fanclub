"""
Request validation middleware
"""
from functools import wraps
from flask import request, jsonify
from api.middleware.error_handler import ValidationError, BadRequestError
import re


def validate_request(schema=None, required_fields=None):
    """
    Validate request body
    
    Args:
        schema: JSON schema for validation (optional)
        required_fields: List of required field names
    
    Usage:
        @validate_request(required_fields=['name', 'email'])
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # #region agent log
            import json
            import os
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.cursor', 'debug.log')
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({'location':'validation.py:25','message':'Validation middleware entry','data':{'isJson':request.is_json,'contentType':request.content_type,'requiredFields':required_fields},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
            except Exception as e:
                pass
            # #endregion
            
            if not request.is_json:
                # #region agent log
                try:
                    with open(log_path, 'a') as f:
                        f.write(json.dumps({'location':'validation.py:27','message':'Not JSON request','data':{'contentType':request.content_type},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
                except:
                    pass
                # #endregion
                raise BadRequestError("Request must be JSON")
            
            data = request.get_json()
            if data is None:
                data = {}
            
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({'location':'validation.py:33','message':'Parsed request data','data':{'dataKeys':list(data.keys()) if data else [],'hasData':bool(data)},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'E'})+'\n')
            except:
                pass
            # #endregion
            
            # Validate required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data or data[field] is None]
                if missing_fields:
                    # #region agent log
                    try:
                        with open(log_path, 'a') as f:
                            f.write(json.dumps({'location':'validation.py:37','message':'Validation failed - missing fields','data':{'missingFields':missing_fields,'receivedFields':list(data.keys())},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'B'})+'\n')
                    except:
                        pass
                    # #endregion
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Store validated data in request context
            request.validated_data = data
            
            # #region agent log
            try:
                with open(log_path, 'a') as f:
                    f.write(json.dumps({'location':'validation.py:40','message':'Validation passed','data':{},'timestamp':int(__import__('time').time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'C'})+'\n')
            except:
                pass
            # #endregion
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_query_params(required_params=None, param_types=None):
    """
    Validate query parameters
    
    Args:
        required_params: List of required parameter names
        param_types: Dict mapping param names to types (int, float, str, bool)
    
    Usage:
        @validate_query_params(required_params=['page'], param_types={'page': int})
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate required params
            if required_params:
                missing_params = [param for param in required_params if param not in request.args]
                if missing_params:
                    raise ValidationError(f"Missing required query parameters: {', '.join(missing_params)}")
            
            # Validate and convert types
            if param_types:
                converted_params = {}
                for param_name, param_type in param_types.items():
                    if param_name in request.args:
                        try:
                            if param_type == bool:
                                value = request.args.get(param_name).lower() in ('true', '1', 'yes')
                            else:
                                value = param_type(request.args.get(param_name))
                            converted_params[param_name] = value
                        except (ValueError, TypeError):
                            raise ValidationError(f"Invalid type for parameter '{param_name}'. Expected {param_type.__name__}")
                
                # Store converted params in request context
                request.validated_params = converted_params
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_file_upload(allowed_extensions=None, max_size=None):
    """
    Validate file upload
    
    Args:
        allowed_extensions: List of allowed file extensions (e.g., ['jpg', 'png'])
        max_size: Maximum file size in bytes
    
    Usage:
        @validate_file_upload(allowed_extensions=['wav', 'mp3'], max_size=16777216)
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                raise BadRequestError("No file provided")
            
            file = request.files['file']
            if file.filename == '':
                raise BadRequestError("No file selected")
            
            # Validate extension
            if allowed_extensions:
                file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                if file_ext not in allowed_extensions:
                    raise ValidationError(f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}")
            
            # Validate size
            if max_size:
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                if file_size > max_size:
                    raise ValidationError(f"File too large. Maximum size: {max_size} bytes")
            
            # Store validated file in request context
            request.validated_file = file
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def sanitize_input(text):
    """
    Sanitize input text
    
    Args:
        text: Input text to sanitize
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format (basic validation)"""
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's digits and reasonable length (7-15 digits)
    return phone.isdigit() and 7 <= len(phone) <= 15


def validate_wallet_address(address):
    """Validate Ethereum wallet address format"""
    if not address.startswith('0x'):
        return False
    if len(address) != 42:
        return False
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False

