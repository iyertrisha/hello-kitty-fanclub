"""
Shopkeeper routes
"""
from flask import Blueprint, request, jsonify, session
from services.shopkeeper import (
    register_shopkeeper,
    get_shopkeeper,
    update_shopkeeper,
    calculate_credit_score,
    get_inventory,
    delete_shopkeeper,
    toggle_shopkeeper_status,
    get_or_create_shopkeeper
)
from services.shopkeeper.otp_service import create_otp_record, verify_otp
from database.models import Product, Shopkeeper, Transaction, Customer, Cooperative
from api.middleware.validation import validate_request
from api.middleware.error_handler import ValidationError, NotFoundError, UnauthorizedError
import logging
import qrcode
import io
import base64
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

shopkeeper_bp = Blueprint('shopkeeper', __name__)


@shopkeeper_bp.route('', methods=['GET'])
def list_shopkeepers_route():
    """
    Get list of shopkeepers (for WhatsApp bot)
    
    Returns: {
        "shopkeepers": [...]
    }
    """
    try:
        from database.models import Shopkeeper
        
        shopkeepers = Shopkeeper.objects()
        
        result = []
        for shopkeeper in shopkeepers:
            result.append({
                'id': str(shopkeeper.id),
                'name': shopkeeper.name,
                'phone': shopkeeper.phone,
                'address': shopkeeper.address
            })
        
        return jsonify({
            'shopkeepers': result
        }), 200
    except Exception as e:
        logger.error(f"Error listing shopkeepers: {e}", exc_info=True)
        raise ValidationError(f"Failed to list shopkeepers: {str(e)}")


@shopkeeper_bp.route('/register', methods=['POST'])
@validate_request(required_fields=['name', 'address', 'phone', 'wallet_address'])
def register_shopkeeper_route():
    """Register new shopkeeper"""
    try:
        data = request.validated_data
        shopkeeper = register_shopkeeper(data)
        
        return jsonify({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'wallet_address': shopkeeper.wallet_address,
            'registered_at': shopkeeper.registered_at.isoformat() if shopkeeper.registered_at else None
        }), 201
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error registering shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to register shopkeeper: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>', methods=['GET'])
def get_shopkeeper_route(shopkeeper_id):
    """Get shopkeeper profile"""
    try:
        # Validate ObjectId format
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        shopkeeper_data = get_shopkeeper(shopkeeper_id)
        return jsonify(shopkeeper_data), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to get shopkeeper: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>', methods=['PUT'])
@validate_request()
def update_shopkeeper_route(shopkeeper_id):
    """Update shopkeeper profile"""
    try:
        data = request.validated_data
        shopkeeper = update_shopkeeper(shopkeeper_id, data)
        
        return jsonify({
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'address': shopkeeper.address,
            'phone': shopkeeper.phone,
            'email': shopkeeper.email
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to update shopkeeper: {str(e)}")




@shopkeeper_bp.route('/<shopkeeper_id>/inventory', methods=['GET'])
def get_inventory_route(shopkeeper_id):
    """Get shopkeeper inventory"""
    try:
        inventory = get_inventory(shopkeeper_id)
        return jsonify({'inventory': inventory}), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to get inventory: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/inventory/<product_id>', methods=['PUT'])
@validate_request()
def update_inventory_route(shopkeeper_id, product_id):
    """Update inventory item"""
    try:
        data = request.validated_data
        
        # Get product
        try:
            product = Product.objects.get(id=product_id, shopkeeper_id=shopkeeper_id)
        except Product.DoesNotExist:
            raise NotFoundError(f"Product {product_id} not found for shopkeeper {shopkeeper_id}")
        
        # Update allowed fields
        if 'price' in data:
            product.price = data['price']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stock_quantity']
        if 'name' in data:
            product.name = data['name']
        if 'category' in data:
            product.category = data['category']
        if 'description' in data:
            product.description = data['description']
        
        product.save()
        
        return jsonify({
            'id': str(product.id),
            'name': product.name,
            'price': product.price,
            'stock_quantity': product.stock_quantity
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to update inventory: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>', methods=['DELETE'])
def delete_shopkeeper_route(shopkeeper_id):
    """Delete shopkeeper"""
    try:
        # Validate ObjectId format
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        delete_shopkeeper(shopkeeper_id)
        return jsonify({'success': True, 'message': 'Shopkeeper deleted successfully'}), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error deleting shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to delete shopkeeper: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/toggle-status', methods=['POST'])
def toggle_shopkeeper_status_route(shopkeeper_id):
    """Toggle shopkeeper active/inactive status"""
    try:
        # Validate ObjectId format
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        shopkeeper = toggle_shopkeeper_status(shopkeeper_id)
        return jsonify({
            'success': True,
            'id': str(shopkeeper.id),
            'is_active': shopkeeper.is_active,
            'message': f"Shopkeeper is now {'active' if shopkeeper.is_active else 'inactive'}"
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error toggling shopkeeper status: {e}", exc_info=True)
        raise ValidationError(f"Failed to toggle shopkeeper status: {str(e)}")


# ========== Login & Authentication Routes ==========

@shopkeeper_bp.route('/login/request-otp', methods=['POST'])
@validate_request(required_fields=['phone'])
def request_otp_route():
    """Request OTP for shopkeeper login"""
    try:
        data = request.validated_data
        phone = data['phone'].strip()
        
        # Normalize phone number
        if not phone.startswith('+'):
            phone = f'+{phone.lstrip("+")}'
        
        # Create OTP record and send via WhatsApp or log
        create_otp_record(phone)
        
        return jsonify({
            'success': True,
            'message': 'OTP sent to your phone'
        }), 200
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to send OTP: {e}", exc_info=True)
        raise ValidationError(f"Failed to send OTP: {str(e)}")


@shopkeeper_bp.route('/login/verify-otp', methods=['POST'])
@validate_request(required_fields=['phone', 'otp_code'])
def verify_otp_route():
    """Verify OTP and create session"""
    try:
        data = request.validated_data
        phone = data['phone'].strip()
        otp_code = data['otp_code'].strip()
        
        # Normalize phone number
        if not phone.startswith('+'):
            phone = f'+{phone.lstrip("+")}'
        
        # Verify OTP
        if not verify_otp(phone, otp_code):
            raise UnauthorizedError("Invalid or expired OTP code")
        
        # Get shopkeeper (must exist - no auto-creation, need registration first)
        shopkeeper = get_or_create_shopkeeper(phone)
        
        # Create Flask session
        session['shopkeeper_id'] = str(shopkeeper.id)
        session['phone'] = phone
        session.permanent = True
        
        # Prepare shopkeeper data
        shopkeeper_data = {
            'id': str(shopkeeper.id),
            'name': shopkeeper.name,
            'phone': shopkeeper.phone,
            'email': shopkeeper.email,
            'address': shopkeeper.address,
            'wallet_address': shopkeeper.wallet_address,
            'blockchain_address': shopkeeper.blockchain_address,
            'credit_score': shopkeeper.credit_score,
            'location': shopkeeper.location.to_dict() if shopkeeper.location else None,
            'is_active': shopkeeper.is_active,
            'registered_at': shopkeeper.registered_at.isoformat() if shopkeeper.registered_at else None
        }
        
        return jsonify({
            'success': True,
            'shopkeeper': shopkeeper_data,
            'message': 'Login successful'
        }), 200
    except UnauthorizedError:
        raise
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}", exc_info=True)
        raise ValidationError(f"Failed to verify OTP: {str(e)}")


@shopkeeper_bp.route('/me', methods=['GET'])
def get_current_shopkeeper_route():
    """Get current shopkeeper profile from session"""
    try:
        shopkeeper_id = session.get('shopkeeper_id')
        if not shopkeeper_id:
            raise UnauthorizedError("Authentication required. Please login.")
        
        shopkeeper_data = get_shopkeeper(shopkeeper_id)
        return jsonify(shopkeeper_data), 200
    except UnauthorizedError:
        raise
    except NotFoundError:
        # Clear invalid session
        session.clear()
        raise UnauthorizedError("Session invalid. Please login again.")
    except Exception as e:
        logger.error(f"Error getting current shopkeeper: {e}", exc_info=True)
        raise ValidationError(f"Failed to get shopkeeper profile: {str(e)}")


@shopkeeper_bp.route('/logout', methods=['POST'])
def logout_route():
    """Logout shopkeeper and destroy session"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    except Exception as e:
        logger.error(f"Error logging out: {e}", exc_info=True)
        raise ValidationError(f"Failed to logout: {str(e)}")


# ========== Profile Management Routes ==========

@shopkeeper_bp.route('/<shopkeeper_id>/profile', methods=['GET'])
def get_profile_route(shopkeeper_id):
    """Get shopkeeper store profile"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        shopkeeper_data = get_shopkeeper(shopkeeper_id)
        return jsonify(shopkeeper_data), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}", exc_info=True)
        raise ValidationError(f"Failed to get profile: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/profile', methods=['POST'])
@validate_request()
def update_profile_route(shopkeeper_id):
    """Create or update shopkeeper store profile"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        data = request.validated_data
        
        # Update allowed fields
        allowed_fields = ['name', 'address', 'email', 'location']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        shopkeeper = update_shopkeeper(shopkeeper_id, update_data)
        shopkeeper_data = get_shopkeeper(shopkeeper_id)
        
        return jsonify({
            'success': True,
            'shopkeeper': shopkeeper_data,
            'message': 'Profile updated successfully'
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        raise ValidationError(f"Failed to update profile: {str(e)}")


# ========== QR Code Generation ==========

@shopkeeper_bp.route('/<shopkeeper_id>/qr-code', methods=['GET'])
def get_qr_code_route(shopkeeper_id):
    """Generate QR code for WhatsApp linking"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        
        # Create WhatsApp deep link
        phone = shopkeeper.phone
        if not phone.startswith('+'):
            phone = f'+{phone.lstrip("+")}'
        
        # WhatsApp link format: whatsapp://send?phone=<phone>&text=<message>
        encoded_message = "Link+to+shop"
        whatsapp_url = f"https://wa.me/{phone.replace('+', '')}?text={encoded_message}"
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(whatsapp_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 data URL
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        data_url = f"data:image/png;base64,{img_base64}"
        
        return jsonify({
            'qr_code': data_url,
            'whatsapp_url': whatsapp_url,
            'phone': phone
        }), 200
    except Shopkeeper.DoesNotExist:
        raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
    except Exception as e:
        logger.error(f"Error generating QR code: {e}", exc_info=True)
        raise ValidationError(f"Failed to generate QR code: {str(e)}")


# ========== Inventory Management ==========

@shopkeeper_bp.route('/<shopkeeper_id>/inventory', methods=['POST'])
@validate_request(required_fields=['name', 'price'])
def add_inventory_route(shopkeeper_id):
    """Add new product to inventory"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        # Verify shopkeeper exists
        try:
            Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        data = request.validated_data
        
        # Create product
        product = Product(
            name=data['name'],
            category=data.get('category', 'General'),
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            description=data.get('description', ''),
            shopkeeper_id=shopkeeper_id
        )
        product.save()
        
        return jsonify({
            'id': str(product.id),
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'stock_quantity': product.stock_quantity,
            'description': product.description
        }), 201
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error adding inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to add inventory: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/inventory/<product_id>', methods=['DELETE'])
def delete_inventory_route(shopkeeper_id, product_id):
    """Delete product from inventory"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
            ObjectId(product_id)
        except InvalidId:
            raise ValidationError(f"Invalid ID format")
        
        try:
            product = Product.objects.get(id=product_id, shopkeeper_id=shopkeeper_id)
        except Product.DoesNotExist:
            raise NotFoundError(f"Product {product_id} not found for shopkeeper {shopkeeper_id}")
        
        product.delete()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error deleting inventory: {e}", exc_info=True)
        raise ValidationError(f"Failed to delete inventory: {str(e)}")


# ========== Cooperative Routes ==========

@shopkeeper_bp.route('/<shopkeeper_id>/cooperatives', methods=['GET'])
def get_shopkeeper_cooperatives_route(shopkeeper_id):
    """Get list of cooperatives the shopkeeper is a member of"""
    try:
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
        
        # Find cooperatives where shopkeeper is a member
        cooperatives = Cooperative.objects(members=shopkeeper)
        
        result = []
        for coop in cooperatives:
            result.append({
                'id': str(coop.id),
                'name': coop.name,
                'description': coop.description,
                'revenue_split_percent': coop.revenue_split_percent,
                'member_count': len(coop.members),
                'is_active': coop.is_active,
                'created_at': coop.created_at.isoformat() if coop.created_at else None
            })
        
        return jsonify({'cooperatives': result}), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting cooperatives: {e}", exc_info=True)
        raise ValidationError(f"Failed to get cooperatives: {str(e)}")


# ========== Transaction Routes ==========

@shopkeeper_bp.route('/<shopkeeper_id>/transactions/recent', methods=['GET'])
def get_recent_transactions_route(shopkeeper_id):
    """Get recent transactions for shopkeeper"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        # Verify shopkeeper exists
        try:
            Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        # Get query parameters
        limit = min(request.args.get('limit', 30, type=int), 100)
        offset = request.args.get('offset', 0, type=int)
        tx_type = request.args.get('type')  # sale, credit, repay
        status = request.args.get('status')  # pending, verified, completed, disputed
        days = request.args.get('days', 30, type=int)
        
        # Build query
        query = {'shopkeeper_id': shopkeeper_id}
        if tx_type:
            query['type'] = tx_type
        if status:
            query['status'] = status
        
        # Date filter
        date_from = datetime.utcnow() - timedelta(days=days)
        query['timestamp__gte'] = date_from
        
        # Get transactions
        transactions = Transaction.objects(**query).order_by('-timestamp').skip(offset).limit(limit)
        
        result = []
        for tx in transactions:
            result.append({
                'id': str(tx.id),
                'type': tx.type,
                'amount': tx.amount,
                'status': tx.status,
                'timestamp': tx.timestamp.isoformat() if tx.timestamp else None,
                'customer_id': str(tx.customer_id.id) if tx.customer_id else None,
                'customer_name': tx.customer_id.name if tx.customer_id else None,
                'product_id': str(tx.product_id.id) if tx.product_id else None,
                'product_name': tx.product_id.name if tx.product_id else None,
                'blockchain_tx_id': tx.blockchain_tx_id,
                'notes': tx.notes
            })
        
        return jsonify({'transactions': result}), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting recent transactions: {e}", exc_info=True)
        raise ValidationError(f"Failed to get recent transactions: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/transactions/stats', methods=['GET'])
def get_transaction_stats_route(shopkeeper_id):
    """Get transaction statistics for shopkeeper"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        # Verify shopkeeper exists
        try:
            Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        # Get all transactions for this shopkeeper
        all_transactions = Transaction.objects(shopkeeper_id=shopkeeper_id)
        
        # Calculate statistics
        total_sales = sum(t.amount for t in all_transactions if t.type == 'sale')
        total_credits = sum(t.amount for t in all_transactions if t.type == 'credit')
        total_repayments = sum(t.amount for t in all_transactions if t.type == 'repay')
        
        sales_count = Transaction.objects(shopkeeper_id=shopkeeper_id, type='sale').count()
        credit_count = Transaction.objects(shopkeeper_id=shopkeeper_id, type='credit').count()
        repay_count = Transaction.objects(shopkeeper_id=shopkeeper_id, type='repay').count()
        
        verified_count = Transaction.objects(shopkeeper_id=shopkeeper_id, status='verified').count()
        completed_count = Transaction.objects(shopkeeper_id=shopkeeper_id, status='completed').count()
        pending_count = Transaction.objects(shopkeeper_id=shopkeeper_id, status='pending').count()
        
        return jsonify({
            'total_sales': total_sales,
            'total_credits': total_credits,
            'total_repayments': total_repayments,
            'counts': {
                'sales': sales_count,
                'credits': credit_count,
                'repayments': repay_count,
                'total': len(all_transactions)
            },
            'status_counts': {
                'verified': verified_count,
                'completed': completed_count,
                'pending': pending_count
            },
            'outstanding_credits': total_credits - total_repayments
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction stats: {e}", exc_info=True)
        raise ValidationError(f"Failed to get transaction stats: {str(e)}")


# ========== Credit/Debit Summary Routes ==========

@shopkeeper_bp.route('/<shopkeeper_id>/credit-summary', methods=['GET'])
def get_credit_summary_route(shopkeeper_id):
    """Get credit summary for shopkeeper"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        # Verify shopkeeper exists
        try:
            Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        # Get all credit transactions
        credit_transactions = Transaction.objects(shopkeeper_id=shopkeeper_id, type='credit')
        repay_transactions = Transaction.objects(shopkeeper_id=shopkeeper_id, type='repay')
        
        total_credits_given = sum(t.amount for t in credit_transactions)
        total_repayments = sum(t.amount for t in repay_transactions)
        outstanding_credits = total_credits_given - total_repayments
        
        # Get unique customers who have credits
        customer_ids = set(str(t.customer_id.id) for t in credit_transactions if t.customer_id)
        
        return jsonify({
            'total_credits_given': total_credits_given,
            'total_repayments': total_repayments,
            'outstanding_credits': outstanding_credits,
            'customer_count': len(customer_ids),
            'credit_transaction_count': len(credit_transactions),
            'repay_transaction_count': len(repay_transactions)
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting credit summary: {e}", exc_info=True)
        raise ValidationError(f"Failed to get credit summary: {str(e)}")


@shopkeeper_bp.route('/<shopkeeper_id>/debt-summary', methods=['GET'])
def get_debt_summary_route(shopkeeper_id):
    """Get debt summary per customer"""
    try:
        from bson.errors import InvalidId
        from bson import ObjectId
        try:
            ObjectId(shopkeeper_id)
        except InvalidId:
            raise ValidationError(f"Invalid shopkeeper ID format: {shopkeeper_id}")
        
        # Verify shopkeeper exists
        try:
            Shopkeeper.objects.get(id=shopkeeper_id)
        except Shopkeeper.DoesNotExist:
            raise NotFoundError(f"Shopkeeper {shopkeeper_id} not found")
        
        # Get all transactions
        credit_transactions = Transaction.objects(shopkeeper_id=shopkeeper_id, type='credit')
        repay_transactions = Transaction.objects(shopkeeper_id=shopkeeper_id, type='repay')
        
        # Calculate debt per customer
        customer_debts = {}
        for tx in credit_transactions:
            if tx.customer_id:
                customer_id = str(tx.customer_id.id)
                if customer_id not in customer_debts:
                    customer_debts[customer_id] = {
                        'customer_id': customer_id,
                        'customer_name': tx.customer_id.name,
                        'total_credits': 0,
                        'total_repayments': 0,
                        'outstanding': 0
                    }
                customer_debts[customer_id]['total_credits'] += tx.amount
        
        for tx in repay_transactions:
            if tx.customer_id:
                customer_id = str(tx.customer_id.id)
                if customer_id not in customer_debts:
                    customer_debts[customer_id] = {
                        'customer_id': customer_id,
                        'customer_name': tx.customer_id.name,
                        'total_credits': 0,
                        'total_repayments': 0,
                        'outstanding': 0
                    }
                customer_debts[customer_id]['total_repayments'] += tx.amount
        
        # Calculate outstanding for each customer
        for customer_id in customer_debts:
            customer_debts[customer_id]['outstanding'] = (
                customer_debts[customer_id]['total_credits'] - 
                customer_debts[customer_id]['total_repayments']
            )
        
        # Filter to only customers with outstanding debt
        outstanding_debts = [debt for debt in customer_debts.values() if debt['outstanding'] > 0]
        
        return jsonify({
            'customers_with_debt': outstanding_debts,
            'total_outstanding': sum(d['outstanding'] for d in outstanding_debts),
            'customer_count': len(outstanding_debts)
        }), 200
    except NotFoundError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error getting debt summary: {e}", exc_info=True)
        raise ValidationError(f"Failed to get debt summary: {str(e)}")


# ========== Credit Score with Limit ==========

@shopkeeper_bp.route('/<shopkeeper_id>/credit-score', methods=['GET'])
def get_credit_score_route(shopkeeper_id):
    """Get credit score with credit limit calculation"""
    try:
        credit_data = calculate_credit_score(shopkeeper_id)
        
        # Add credit limit calculation (score * 100 = max credit in ₹)
        credit_limit = credit_data.get('score', 0) * 100
        
        credit_data['credit_limit'] = credit_limit
        credit_data['credit_limit_currency'] = 'INR'
        
        return jsonify(credit_data), 200
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error getting credit score: {e}", exc_info=True)
        raise ValidationError(f"Failed to get credit score: {str(e)}")

