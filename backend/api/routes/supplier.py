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
from services.supplier.analytics_service import (
    get_analytics_overview,
    get_analytics_orders,
    get_analytics_stores,
    get_analytics_revenue
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
    try:
        data = request.validated_data
        email = data['email'].strip().lower()
        
        # Create OTP record and send email
        create_otp_record(email)
        
        return jsonify({
            'success': True,
            'message': 'OTP sent to your email'
        }), 200
    except ValidationError as ve:
        raise
    except Exception as e:
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
    """Get stores in supplier's service area (with optional geographic filtering)"""
    try:
        supplier_id = request.supplier_id
        
        # Check for geographic filter parameters
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=float)  # in km
        
        if lat is not None and lng is not None:
            # Use geographic filtering
            from database.models import Shopkeeper
            # Import order routing service (handles hyphenated directory)
            import importlib.util
            from pathlib import Path
            _order_routing_file = Path(__file__).parent.parent.parent / 'services' / 'order-routing' / 'order_routing.py'
            _spec = importlib.util.spec_from_file_location('order_routing', _order_routing_file)
            _order_routing_module = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_order_routing_module)
            calculate_distance = _order_routing_module.calculate_distance
            import math
            
            center_location = {'latitude': lat, 'longitude': lng}
            if radius is None:
                radius = 10.0  # Default 10km
            
            # Get all active shopkeepers with locations
            all_stores = Shopkeeper.objects(is_active=True, location__exists=True)
            
            stores_in_area = []
            for shopkeeper in all_stores:
                if not shopkeeper.location:
                    continue
                
                store_location = {
                    'latitude': shopkeeper.location.latitude,
                    'longitude': shopkeeper.location.longitude
                }
                
                distance = calculate_distance(center_location, store_location)
                
                if distance <= radius:
                    stores_in_area.append({
                        'id': str(shopkeeper.id),
                        'name': shopkeeper.name,
                        'address': shopkeeper.address,
                        'phone': shopkeeper.phone,
                        'email': shopkeeper.email,
                        'location': shopkeeper.location.to_dict() if shopkeeper.location else None,
                        'credit_score': shopkeeper.credit_score,
                        'distance_km': round(distance, 2)
                    })
            
            # Sort by distance
            stores_in_area.sort(key=lambda x: x.get('distance_km', float('inf')))
            
            logger.info(f"Found {len(stores_in_area)} stores within {radius}km of ({lat}, {lng})")
            return jsonify({
                'stores': stores_in_area,
                'count': len(stores_in_area),
                'center': {'latitude': lat, 'longitude': lng},
                'radius_km': radius
            }), 200
        else:
            # Use supplier's service area
            logger.info(f"Getting stores for supplier {supplier_id}")
            stores = get_stores_in_service_area(supplier_id)
            logger.info(f"Found {len(stores)} stores for supplier {supplier_id}")
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
                'shopkeeper_address': order.shopkeeper_id.address,
                'shopkeeper_phone': order.shopkeeper_id.phone,
                'shopkeeper_email': order.shopkeeper_id.email,
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


@supplier_bp.route('/orders/<order_id>', methods=['GET'])
@require_supplier_session
def get_order_route(order_id):
    """Get order details by ID"""
    try:
        supplier_id = request.supplier_id
        from database.models import SupplierOrder
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(order_id)
            ObjectId(supplier_id)
        except InvalidId:
            raise ValidationError(f"Invalid ID format")
        
        try:
            order = SupplierOrder.objects.get(id=order_id, supplier_id=supplier_id)
        except SupplierOrder.DoesNotExist:
            raise NotFoundError(f"Order {order_id} not found")
        
        order_data = {
            'id': str(order.id),
            'shopkeeper_id': str(order.shopkeeper_id.id),
            'shopkeeper_name': order.shopkeeper_id.name,
            'shopkeeper_address': order.shopkeeper_id.address,
            'shopkeeper_phone': order.shopkeeper_id.phone,
            'shopkeeper_email': order.shopkeeper_id.email,
            'products': order.products,
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'notes': order.notes
        }
        
        return jsonify({
            'order': order_data
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting order: {e}", exc_info=True)
        raise ValidationError(f"Failed to get order: {str(e)}")


@supplier_bp.route('/orders/<order_id>/status', methods=['PUT'])
@require_supplier_session
@validate_request(required_fields=['status'])
def update_order_status_route(order_id):
    """Update order status"""
    try:
        supplier_id = request.supplier_id
        data = request.validated_data
        new_status = data['status']
        
        from database.models import SupplierOrder
        from bson.errors import InvalidId
        from bson import ObjectId
        
        valid_statuses = ['pending', 'confirmed', 'dispatched', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        try:
            ObjectId(order_id)
            ObjectId(supplier_id)
        except InvalidId:
            raise ValidationError(f"Invalid ID format")
        
        try:
            order = SupplierOrder.objects.get(id=order_id, supplier_id=supplier_id)
        except SupplierOrder.DoesNotExist:
            raise NotFoundError(f"Order {order_id} not found")
        
        order.status = new_status
        order.save()
        
        logger.info(f"Updated order {order_id} status to {new_status}")
        
        return jsonify({
            'id': str(order.id),
            'status': order.status,
            'message': 'Order status updated successfully'
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}", exc_info=True)
        raise ValidationError(f"Failed to update order status: {str(e)}")


@supplier_bp.route('/orders/<order_id>', methods=['DELETE'])
@require_supplier_session
def cancel_order_route(order_id):
    """Cancel order"""
    try:
        supplier_id = request.supplier_id
        from database.models import SupplierOrder
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(order_id)
            ObjectId(supplier_id)
        except InvalidId:
            raise ValidationError(f"Invalid ID format")
        
        try:
            order = SupplierOrder.objects.get(id=order_id, supplier_id=supplier_id)
        except SupplierOrder.DoesNotExist:
            raise NotFoundError(f"Order {order_id} not found")
        
        # Only allow cancelling if not delivered
        if order.status == 'delivered':
            raise ValidationError("Cannot cancel a delivered order")
        
        order.status = 'cancelled'
        order.save()
        
        logger.info(f"Cancelled order {order_id}")
        
        return jsonify({
            'id': str(order.id),
            'status': order.status,
            'message': 'Order cancelled successfully'
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}", exc_info=True)
        raise ValidationError(f"Failed to cancel order: {str(e)}")


@supplier_bp.route('/analytics/overview', methods=['GET'])
@require_supplier_session
def get_analytics_overview_route():
    """Get analytics overview statistics"""
    try:
        supplier_id = request.supplier_id
        overview = get_analytics_overview(supplier_id)
        return jsonify(overview), 200
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}", exc_info=True)
        raise ValidationError(f"Failed to get analytics overview: {str(e)}")


@supplier_bp.route('/analytics/orders', methods=['GET'])
@require_supplier_session
def get_analytics_orders_route():
    """Get order analytics data"""
    try:
        supplier_id = request.supplier_id
        days = request.args.get('days', 30, type=int)
        analytics = get_analytics_orders(supplier_id, days)
        return jsonify(analytics), 200
    except Exception as e:
        logger.error(f"Error getting order analytics: {e}", exc_info=True)
        raise ValidationError(f"Failed to get order analytics: {str(e)}")


@supplier_bp.route('/analytics/stores', methods=['GET'])
@require_supplier_session
def get_analytics_stores_route():
    """Get store analytics data"""
    try:
        supplier_id = request.supplier_id
        analytics = get_analytics_stores(supplier_id)
        return jsonify(analytics), 200
    except Exception as e:
        logger.error(f"Error getting store analytics: {e}", exc_info=True)
        raise ValidationError(f"Failed to get store analytics: {str(e)}")


@supplier_bp.route('/analytics/revenue', methods=['GET'])
@require_supplier_session
def get_analytics_revenue_route():
    """Get revenue analytics data"""
    try:
        supplier_id = request.supplier_id
        days = request.args.get('days', 30, type=int)
        analytics = get_analytics_revenue(supplier_id, days)
        return jsonify(analytics), 200
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}", exc_info=True)
        raise ValidationError(f"Failed to get revenue analytics: {str(e)}")


# ========== Blockchain Read Access Routes ==========

@supplier_bp.route('/blockchain/transactions', methods=['GET'])
@require_supplier_session
def get_blockchain_transactions_route():
    """Get blockchain transactions for shopkeeper (read-only access)"""
    try:
        shopkeeper_id = request.args.get('shopkeeper_id')
        if not shopkeeper_id:
            raise ValidationError("Missing required parameter: shopkeeper_id")
        
        from database.models import Transaction, Shopkeeper
        from bson.errors import InvalidId
        from bson import ObjectId
        
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        # Verify shopkeeper exists
        try:
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        # Get verified transactions with blockchain TX IDs
        transactions = Transaction.objects(
            shopkeeper_id=shopkeeper_id,
            blockchain_tx_id__exists=True
        ).order_by('-timestamp')
        
        result = []
        for tx in transactions:
            result.append({
                'id': str(tx.id),
                'type': tx.type,
                'amount': tx.amount,
                'blockchain_tx_id': tx.blockchain_tx_id,
                'blockchain_block_number': tx.blockchain_block_number,
                'timestamp': tx.timestamp.isoformat() if tx.timestamp else None,
                'transcript_hash': tx.transcript_hash,
                'status': tx.status
            })
        
        return jsonify({
            'shopkeeper_id': shopkeeper_id,
            'shopkeeper_name': shopkeeper.name,
            'transactions': result,
            'count': len(result)
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting blockchain transactions: {e}", exc_info=True)
        raise ValidationError(f"Failed to get blockchain transactions: {str(e)}")


@supplier_bp.route('/blockchain/verify', methods=['GET'])
@require_supplier_session
def verify_blockchain_transaction_route():
    """Verify transaction on blockchain (read-only)"""
    try:
        tx_hash = request.args.get('tx_hash')
        if not tx_hash:
            raise ValidationError("Missing required parameter: tx_hash")
        
        # Try to get transaction from blockchain service
        try:
            from api.routes.blockchain import get_blockchain_service
            blockchain_service = get_blockchain_service()
            
            # Get transaction from blockchain (assuming contract has getTransaction method)
            # This is a placeholder - actual implementation depends on contract methods
            try:
                # Try to get transaction receipt
                from web3 import Web3
                import os
                
                rpc_url = os.getenv('POLYGON_AMOY_RPC_URL') or os.getenv('RPC_URL')
                if not rpc_url:
                    raise Exception("RPC URL not configured")
                
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # Get transaction receipt
                tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
                
                return jsonify({
                    'tx_hash': tx_hash,
                    'verified': True,
                    'block_number': tx_receipt['blockNumber'],
                    'status': 'success' if tx_receipt['status'] == 1 else 'failed',
                    'confirmations': w3.eth.block_number - tx_receipt['blockNumber'] if tx_receipt['blockNumber'] else 0
                }), 200
            except Exception as e:
                logger.warning(f"Error verifying transaction on blockchain: {e}")
                return jsonify({
                    'tx_hash': tx_hash,
                    'verified': False,
                    'error': str(e)
                }), 200
        except Exception as e:
            logger.error(f"Blockchain service error: {e}")
            return jsonify({
                'tx_hash': tx_hash,
                'verified': False,
                'error': 'Blockchain service not available'
            }), 503
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error verifying transaction: {e}", exc_info=True)
        raise ValidationError(f"Failed to verify transaction: {str(e)}")

