"""
MongoDB Models using MongoEngine
"""
from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    FloatField,
    IntField,
    DateTimeField,
    ListField,
    ReferenceField,
    BooleanField,
    DictField,
    EmbeddedDocument,
    EmbeddedDocumentField
)


class Location(EmbeddedDocument):
    """Geographic location embedded document"""
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    address = StringField()
    
    def to_dict(self):
        """Convert location to dictionary"""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address
        }


class Shopkeeper(Document):
    """Shopkeeper model"""
    name = StringField(required=True, max_length=200)
    address = StringField(required=True)
    phone = StringField(required=True, max_length=20)
    email = StringField(max_length=200)
    wallet_address = StringField(required=True, unique=True, max_length=42)
    blockchain_address = StringField(max_length=42)  # Same as wallet_address after registration
    credit_score = IntField(default=0, min_value=0, max_value=900)  # Vishwas Score
    registered_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    location = EmbeddedDocumentField(Location)
    flagged = BooleanField(default=False)  # Flagged by platform admin for review
    flag_reason = StringField(max_length=500)  # Reason for flagging
    flagged_at = DateTimeField()  # When it was flagged
    
    meta = {
        'collection': 'shopkeepers',
        'indexes': [
            'wallet_address',
            'phone',
            'email',
            'registered_at'
        ]
    }


class Customer(Document):
    """Customer model"""
    name = StringField(required=True, max_length=200)
    phone = StringField(required=True, unique=True, max_length=20)
    address = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    total_purchases = FloatField(default=0.0)
    total_credits = FloatField(default=0.0)
    credit_balance = FloatField(default=0.0)
    
    meta = {
        'collection': 'customers',
        'indexes': [
            'phone',
            'created_at'
        ]
    }


class Product(Document):
    """Product/Inventory model"""
    name = StringField(required=True, max_length=200)
    category = StringField(max_length=100)
    price = FloatField(required=True, min_value=0)
    stock_quantity = IntField(default=0, min_value=0)
    shopkeeper_id = ReferenceField('Shopkeeper', required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    description = StringField(max_length=500)
    
    meta = {
        'collection': 'products',
        'indexes': [
            'shopkeeper_id',
            'category',
            'name',
            ('shopkeeper_id', 'name')  # Compound index
        ]
    }


class Transaction(Document):
    """Transaction model"""
    TRANSACTION_TYPES = ('sale', 'credit', 'repay')
    STATUS_CHOICES = ('pending', 'verified', 'disputed', 'completed')
    
    type = StringField(required=True, choices=TRANSACTION_TYPES)
    amount = FloatField(required=True, min_value=0)
    shopkeeper_id = ReferenceField('Shopkeeper', required=True)
    customer_id = ReferenceField('Customer', required=True)
    product_id = ReferenceField('Product')  # Optional, for sales transactions
    timestamp = DateTimeField(default=datetime.utcnow, required=True)
    status = StringField(default='pending', choices=STATUS_CHOICES)
    transcript = StringField()  # Original transcript text from STT
    transcript_hash = StringField(max_length=66)  # SHA256 hash (0x + 64 hex chars)
    blockchain_tx_id = StringField(max_length=66)  # Blockchain transaction hash
    blockchain_block_number = IntField()
    verification_status = StringField(max_length=50)  # Additional verification info (verified, pending, flagged, rejected)
    fraud_score = FloatField()  # Fraud detection score (0-100)
    fraud_risk_level = StringField(max_length=20)  # low, medium, high, critical
    verification_metadata = DictField()  # Full verification metadata from verification service
    notes = StringField(max_length=500)
    
    meta = {
        'collection': 'transactions',
        'indexes': [
            'shopkeeper_id',
            'customer_id',
            'timestamp',
            'status',
            'type',
            ('shopkeeper_id', 'timestamp'),
            ('customer_id', 'timestamp'),
            'blockchain_tx_id'
        ]
    }


class Cooperative(Document):
    """Cooperative model"""
    name = StringField(required=True, max_length=200)
    description = StringField(max_length=1000)
    revenue_split_percent = FloatField(default=0.0, min_value=0, max_value=100)
    created_at = DateTimeField(default=datetime.utcnow)
    members = ListField(ReferenceField('Shopkeeper'))
    blockchain_coop_id = StringField(max_length=100)  # Cooperative ID on blockchain
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'cooperatives',
        'indexes': [
            'name',
            'created_at',
            'blockchain_coop_id',
            'members'
        ]
    }


class BulkOrder(Document):
    """Bulk order model for cooperatives"""
    cooperative_id = ReferenceField('Cooperative', required=True)
    product_name = StringField(required=True, max_length=200)
    quantity = IntField(required=True, min_value=1)
    unit_price = FloatField(required=True, min_value=0)
    total_amount = FloatField(required=True, min_value=0)
    created_at = DateTimeField(default=datetime.utcnow)
    status = StringField(default='pending', choices=('pending', 'ordered', 'delivered', 'cancelled'))
    order_details = DictField()  # Additional order information
    
    meta = {
        'collection': 'bulk_orders',
        'indexes': [
            'cooperative_id',
            'created_at',
            'status'
        ]
    }


class PendingConfirmation(Document):
    """Pending confirmation model for WhatsApp credit confirmations"""
    STATUS_CHOICES = ('pending', 'confirmed', 'rejected', 'expired')
    
    transaction_id = ReferenceField('Transaction', required=True)
    phone = StringField(required=True, max_length=20)  # Normalized phone (e.g., +919876543210)
    amount = FloatField(required=True, min_value=0)
    shopkeeper = StringField(required=True, max_length=200)  # Shopkeeper name
    status = StringField(default='pending', choices=STATUS_CHOICES)
    created_at = DateTimeField(default=datetime.utcnow, required=True)
    expires_at = DateTimeField(required=True)
    
    meta = {
        'collection': 'pending_confirmations',
        'indexes': [
            'phone',
            'status',
            'expires_at',
            'transaction_id',
            ('phone', 'status'),
            ('phone', 'expires_at')
        ]
    }


class Notice(Document):
    """Noticeboard announcements"""
    title = StringField(required=True, max_length=200)
    message = StringField(required=True, max_length=1000)
    shopkeeper_id = ReferenceField('Shopkeeper', required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    priority = StringField(default='normal', choices=('low', 'normal', 'high', 'urgent'))
    is_active = BooleanField(default=True)
    expires_at = DateTimeField()  # Optional expiration
    
    meta = {
        'collection': 'notices',
        'indexes': [
            'shopkeeper_id',
            'created_at',
            'is_active',
            'priority',
            ('shopkeeper_id', 'is_active'),
            ('shopkeeper_id', 'priority')
class Supplier(Document):
    """Supplier/Vendor model"""
    name = StringField(required=True, max_length=200)
    email = StringField(required=True, unique=True, max_length=200)
    phone = StringField(max_length=20)  # Optional, can be set later
    password_hash = StringField(default='')  # Not required for OTP auth
    company_name = StringField(max_length=200)
    address = StringField()
    service_area_center = EmbeddedDocumentField(Location)  # Center of service area
    service_area_radius_km = FloatField(default=10.0, min_value=1.0)  # Radius in km
    registered_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'suppliers',
        'indexes': [
            'email',
            'phone',
            'registered_at'
        ]
    }


class SupplierOrder(Document):
    """Bulk order from supplier to shopkeeper"""
    supplier_id = ReferenceField('Supplier', required=True)
    shopkeeper_id = ReferenceField('Shopkeeper', required=True)
    products = ListField(DictField())  # [{product_name, quantity, unit_price}, ...]
    total_amount = FloatField(required=True, min_value=0)
    status = StringField(default='pending', choices=('pending', 'confirmed', 'dispatched', 'delivered', 'cancelled'))
    created_at = DateTimeField(default=datetime.utcnow)
    notes = StringField(max_length=500)
    
    meta = {
        'collection': 'supplier_orders',
        'indexes': [
            'supplier_id',
            'shopkeeper_id',
            'created_at',
            'status'
        ]
    }


class OTPVerification(Document):
    """OTP verification model for email-based authentication"""
    email = StringField(required=True, max_length=200)
    otp_code = StringField(required=True, max_length=6)
    expires_at = DateTimeField(required=True)
    used = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'otp_verifications',
        'indexes': [
            'email',
            'expires_at',
            ('email', 'expires_at')
        ]
    }