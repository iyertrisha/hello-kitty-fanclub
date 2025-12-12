"""
Supplier routes
"""
from flask import Blueprint, request, jsonify, session
from services.supplier import (
    register_supplier,
    get_or_create_supplier,
    get_supplier,
    update_supplier_service_area,
    get_stores_in_service_area,
    create_bulk_order
)
from services.supplier.otp_service import create_otp_record, verify_otp
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError, UnauthorizedError
from api.middleware.auth import require_supplier_session
import logging

logger = logging.getLogger(__name__)

supplier_bp = Blueprint('supplier', __name__)


@supplier_bp.route('/register', methods=['POST'])
@validate_request(required_fields=['email'])
def register_supplier_route():
    """Register new supplier (optional - suppliers auto-created on first login)"""
    try:
        data = request.validated_data
        supplier = register_supplier(data)
        
        return jsonify({
            'id': str(supplier.id),
            'name': supplier.name,
            'email': supplier.email,
            'message': 'Supplier registered successfully'
        }), 201
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error registering supplier: {e}", exc_info=True)
        raise ValidationError(f"Failed to register supplier: {str(e)}")


@supplier_bp.route('/login/request-otp', methods=['POST'])
@validate_request(required_fields=['email'])
def request_otp_route():
    """Request OTP for login"""
    # #region agent log
    import json
    with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"supplier.py:47","message":"request_otp_route entry","data":{"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
    try:
        data = request.validated_data
        email = data['email'].strip().lower()
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"supplier.py:52","message":"email received","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        
        # Create OTP record and send email
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"supplier.py:55","message":"before create_otp_record","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        create_otp_record(email)
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"supplier.py:58","message":"after create_otp_record success","data":{"email":email,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        
        return jsonify({
            'success': True,
            'message': 'OTP sent to your email'
        }), 200
    except ValidationError as ve:
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"supplier.py:66","message":"ValidationError caught","data":{"error":str(ve),"email":email if 'email' in locals() else None,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        raise
    except Exception as e:
        # #region agent log
        with open(r'c:\hello-kitty-fanclub\.cursor\debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"supplier.py:70","message":"Exception caught in request_otp","data":{"error":str(e),"error_type":type(e).__name__,"email":email if 'email' in locals() else None,"timestamp":__import__('time').time()*1000},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        # #endregion
        logger.error(f"Error requesting OTP: {e}", exc_info=True)
        raise ValidationError(f"Failed to send OTP: {str(e)}")


@supplier_bp.route('/login/verify-otp', methods=['POST'])
@validate_request(required_fields=['email', 'otp_code'])
def verify_otp_route():
    """Verify OTP and create session"""
    try:
        data = request.validated_data
        email = data['email'].strip().lower()
        otp_code = data['otp_code'].strip()
        
        # Verify OTP
        if not verify_otp(email, otp_code):
            raise UnauthorizedError("Invalid or expired OTP code")
        
        # Get or create supplier
        supplier = get_or_create_supplier(email)
        
        # Create Flask session
        session['supplier_id'] = str(supplier.id)
        session['email'] = email
        session.permanent = True
        
        # Prepare supplier data
        supplier_data = {
            'id': str(supplier.id),
            'name': supplier.name,
            'email': supplier.email,
            'phone': supplier.phone,
            'company_name': supplier.company_name,
            'address': supplier.address,
            'service_area_center': supplier.service_area_center.to_dict() if supplier.service_area_center else None,
            'service_area_radius_km': supplier.service_area_radius_km,
            'registered_at': supplier.registered_at.isoformat() if supplier.registered_at else None
        }
        
        return jsonify({
            'success': True,
            'supplier': supplier_data,
            'message': 'Login successful'
        }), 200
    except UnauthorizedError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}", exc_info=True)
        raise ValidationError(f"Failed to verify OTP: {str(e)}")


@supplier_bp.route('/logout', methods=['POST'])
def logout_route():
    """Logout supplier and destroy session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error logging out: {e}", exc_info=True)
        raise ValidationError(f"Failed to logout: {str(e)}")


@supplier_bp.route('/session', methods=['GET'])
def check_session_route():
    """Check if session is valid"""
    try:
        supplier_id = session.get('supplier_id')
        if not supplier_id:
            return jsonify({
                'authenticated': False,
                'message': 'No active session'
            }), 200
        
        # Get supplier data
        supplier_data = get_supplier(supplier_id)
        
        return jsonify({
            'authenticated': True,
            'supplier': supplier_data
        }), 200
    except NotFoundError:
        session.clear()
        return jsonify({
            'authenticated': False,
            'message': 'Supplier not found'
        }), 200
    except Exception as e:
        logger.error(f"Error checking session: {e}", exc_info=True)
        return jsonify({
            'authenticated': False,
            'message': 'Session check failed'
        }), 200


@supplier_bp.route('/<supplier_id>', methods=['GET'])
def get_supplier_route(supplier_id):
    """Get supplier profile"""
    try:
        supplier_data = get_supplier(supplier_id)
        return jsonify(supplier_data), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier: {e}", exc_info=True)
        raise ValidationError(f"Failed to get supplier: {str(e)}")


@supplier_bp.route('/service-area', methods=['PUT'])
@require_supplier_session
@validate_request(required_fields=['center'])
def update_service_area_route():
    """Update supplier service area"""
    try:
        supplier_id = request.supplier_id
        data = request.validated_data
        
        # Validate center has lat/lng
        if 'latitude' not in data['center'] or 'longitude' not in data['center']:
            raise ValidationError("Service area center must have 'latitude' and 'longitude'")
        
        supplier = update_supplier_service_area(supplier_id, {
            'center': data['center'],
            'radius_km': data.get('radius_km', 10.0)
        })
        
        return jsonify({
            'id': str(supplier.id),
            'service_area_center': supplier.service_area_center.to_dict() if supplier.service_area_center else None,
            'service_area_radius_km': supplier.service_area_radius_km,
            'message': 'Service area updated successfully'
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating service area: {e}", exc_info=True)
        raise ValidationError(f"Failed to update service area: {str(e)}")


@supplier_bp.route('/stores', methods=['GET'])
@require_supplier_session
def get_stores_route():
    """Get stores in supplier's service area"""
    try:
        supplier_id = request.supplier_id
        stores = get_stores_in_service_area(supplier_id)
        return jsonify({
            'stores': stores,
            'count': len(stores)
        }), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting stores: {e}", exc_info=True)
        raise ValidationError(f"Failed to get stores: {str(e)}")


@supplier_bp.route('/orders', methods=['POST'])
@require_supplier_session
@validate_request(required_fields=['shopkeeper_id', 'products'])
def create_order_route():
    """Create bulk order to shopkeeper"""
    try:
        supplier_id = request.supplier_id
        data = request.validated_data
        
        # Validate products
        if not isinstance(data['products'], list) or len(data['products']) == 0:
            raise ValidationError("Products must be a non-empty list")
        
        for product in data['products']:
            if 'name' not in product or 'quantity' not in product or 'unit_price' not in product:
                raise ValidationError("Each product must have 'name', 'quantity', and 'unit_price'")
        
        order = create_bulk_order(
            supplier_id=supplier_id,
            shopkeeper_id=data['shopkeeper_id'],
            products_data=data['products']
        )
        
        return jsonify({
            'id': str(order.id),
            'supplier_id': str(order.supplier_id.id),
            'shopkeeper_id': str(order.shopkeeper_id.id),
            'products': order.products,
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'message': 'Order created successfully'
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise ValidationError(f"Failed to create order: {str(e)}")


@supplier_bp.route('/orders', methods=['GET'])
@require_supplier_session
def get_orders_route():
    """Get all orders for supplier"""
    try:
        supplier_id = request.supplier_id
        from database.models import SupplierOrder
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(supplier_id)
        except InvalidId:
            raise ValidationError(f"Invalid supplier ID format: {supplier_id}")
        
        orders = SupplierOrder.objects(supplier_id=supplier_id).order_by('-created_at')
        
        orders_list = []
        for order in orders:
            orders_list.append({
                'id': str(order.id),
                'shopkeeper_id': str(order.shopkeeper_id.id),
                'shopkeeper_name': order.shopkeeper_id.name,
                'products': order.products,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'notes': order.notes
            })
        
        return jsonify({
            'orders': orders_list,
            'count': len(orders_list)
        }), 200
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting orders: {e}", exc_info=True)
        raise ValidationError(f"Failed to get orders: {str(e)}")

