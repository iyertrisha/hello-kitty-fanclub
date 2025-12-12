"""
Voice Demo Script for Hackathon Judges

Captures voice input, transcribes it, and stores transactions on blockchain.
Works without React Native app - uses Python microphone input.

Requirements:
  pip install speechrecognition pyaudio

Usage:
  python voice_demo.py
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Add parent directories to path (parent first to get backend/config.py, not blockchain/config.py)
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(1, str(Path(__file__).parent))

# Import database models
try:
    from mongoengine import connect
    from database.models import Product, Shopkeeper, Customer
    # Import from parent directory's config (backend/config.py, not blockchain/config.py)
    # Remove blockchain directory from path temporarily to avoid import conflict
    blockchain_dir = str(Path(__file__).parent)
    if blockchain_dir in sys.path:
        sys.path.remove(blockchain_dir)
    from config import DevelopmentConfig
    # Re-add blockchain dir if needed
    if blockchain_dir not in sys.path:
        sys.path.append(blockchain_dir)
    DATABASE_AVAILABLE = True
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️  Database models not available: {e}")
    print("   Product lookup will be disabled.")

# Import new Hindi parser
# Import new Hindi parser
try:
    from hindi_parser import parse_hindi_transaction, PRODUCT_MAPPING as HINDI_PRODUCT_MAPPING
    HINDI_PARSER_AVAILABLE = True
except ImportError as e:
    HINDI_PARSER_AVAILABLE = False
    HINDI_PRODUCT_MAPPING = {}
    print(f"⚠️  Hindi parser not available: {e}")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  speech_recognition not installed. Install with: pip install speechrecognition pyaudio")

# API Configuration
# Use actual backend API (port 5000) instead of test API (port 5001)
# This ensures transactions are stored in the real database and visible in admin dashboard
API_URL = "http://localhost:5000/api/transactions"
API_STATUS_URL = "http://localhost:5000/api/blockchain/status"


def get_demo_ids():
    """
    Get demo shopkeeper and customer IDs from database
    Returns tuple: (shopkeeper_id, customer_id) or (None, None) if not available
    """
    if not DATABASE_AVAILABLE:
        return None, None
    
    try:
        # Use DevelopmentConfig directly
        cfg = DevelopmentConfig
        
        # Connect to database using same method as Flask app
        # Disconnect first if already connected to avoid errors
        from mongoengine import disconnect
        try:
            disconnect()
        except:
            pass
        
        # Connect to database
        connect(
            db=cfg.MONGODB_DB_NAME,
            host=cfg.MONGODB_URI,
            alias='default'
        )
        
        # Get first active shopkeeper
        shopkeeper = Shopkeeper.objects(is_active=True).first()
        if not shopkeeper:
            shopkeeper = Shopkeeper.objects().first()
        
        # Get a random customer (for testing)
        import random
        all_customers = list(Customer.objects())
        if all_customers:
            customer = random.choice(all_customers)
        else:
            customer = None
        
        if shopkeeper and customer:
            return str(shopkeeper.id), str(customer.id)
        else:
            print("⚠️  No shopkeepers or customers found in database")
            return None, None
    except Exception as e:
        print(f"⚠️  Error getting demo IDs: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def get_customer_list() -> List[Dict[str, Any]]:
    """
    Get list of all customers for fuzzy matching.
    
    Returns:
        List of customer dicts with 'id' and 'name' keys
    """
    if not DATABASE_AVAILABLE:
        return []
    
    try:
        customers = Customer.objects().only('id', 'name')
        return [{'id': str(c.id), 'name': c.name} for c in customers]
    except Exception as e:
        print(f"⚠️  Error getting customer list: {e}")
        return []


def create_product_price_lookup(shopkeeper_id: str):
    """
    Create a product price lookup function for the Hindi parser.
    
    Args:
        shopkeeper_id: Shopkeeper ID
    
    Returns:
        Function that takes product_name and returns price (float) or None
    """
    def lookup_price(product_name: str) -> Optional[float]:
        """Lookup product price from database or demo prices"""
        if not DATABASE_AVAILABLE:
            # Use demo prices
            from hindi_parser import PRODUCT_MAPPING
            demo_prices = {
                'Tomatoes': 50.00,
                'Potatoes': 35.00,
                'Onions': 40.00,
                'Rice': 50.00,
                'Wheat Flour': 40.00,
                'Sugar': 45.00,
                'Salt': 20.00,
                'Cooking Oil': 120.00,
                'Tea': 200.00,
                'Coffee': 300.00,
                'Milk': 60.00,
                'Bread': 30.00,
                'Eggs': 80.00,
                'Soap': 25.00,
                'Shampoo': 150.00,
            }
            return demo_prices.get(product_name)
        
        try:
            # Try database lookup
            product = Product.objects(
                shopkeeper_id=shopkeeper_id,
                name__iexact=product_name
            ).first()
            
            if product:
                return product.price
            
            # Try partial match
            product = Product.objects(
                shopkeeper_id=shopkeeper_id,
                name__icontains=product_name
            ).first()
            
            if product:
                return product.price
            
            # Fallback to demo prices
            demo_prices = {
                'Tomatoes': 50.00,
                'Potatoes': 35.00,
                'Onions': 40.00,
                'Rice': 50.00,
                'Wheat Flour': 40.00,
                'Sugar': 45.00,
                'Salt': 20.00,
                'Cooking Oil': 120.00,
                'Tea': 200.00,
                'Coffee': 300.00,
                'Milk': 60.00,
                'Bread': 30.00,
                'Eggs': 80.00,
                'Soap': 25.00,
                'Shampoo': 150.00,
            }
            return demo_prices.get(product_name)
        except Exception:
            return None
    
    return lookup_price


def check_api_connection():
    """Check if backend API is running"""
    try:
        # Check main backend API - try a simple endpoint
        response = requests.get("http://localhost:5000/api/admin/overview", timeout=2)
        if response.status_code in [200, 401, 403]:  # Any response means server is running
            return True
    except:
        # Try alternative - just check if server responds
        try:
            response = requests.get("http://localhost:5000/", timeout=2)
            return True
        except:
            pass
    return False


def get_voice_input():
    """Capture voice input from microphone"""
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("\n❌ Speech recognition not available.")
        print("   Install: pip install speechrecognition pyaudio")
        return None
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("\n" + "=" * 70)
    print("🎤 VOICE INPUT MODE")
    print("=" * 70)
    print("\n📢 Speak your transaction:")
    print("   Examples:")
    print("   - 'राहुल को 500 रुपये का उधार दे दो' (Hindi credit)")
    print("   - 'Give 500 rupees credit to Rahul' (English credit)")
    print("   - '2 किलो चावल 120 रुपये' (Hindi sale)")
    print("   - '2 kg rice 120 rupees' (English sale)")
    print("\n⏸️  Listening... (speak now, or press Ctrl+C to cancel)")
    
    try:
        with microphone as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=20)
        
        print("🔄 Processing audio...")
        
        # Try Hindi first, then English
        transcript = None
        language = None
        
        try:
            # Try Hindi (India)
            transcript = recognizer.recognize_google(audio, language='hi-IN')
            language = 'hi-IN'
            print(f"✅ Detected: Hindi")
        except sr.UnknownValueError:
            try:
                # Try English (India)
                transcript = recognizer.recognize_google(audio, language='en-IN')
                language = 'en-IN'
                print(f"✅ Detected: English")
            except sr.UnknownValueError:
                print("❌ Could not understand audio. Please try again.")
                return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            print("   Note: Requires internet connection for Google Speech API")
            return None
        
        print(f"\n📝 Transcript: {transcript}")
        return {'transcript': transcript, 'language': language}
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        return None
    except sr.WaitTimeoutError:
        print("\n⏱️  Timeout - no speech detected")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None


# Product name mapping (Hindi to English)
PRODUCT_MAPPING = {
    # Vegetables
    'टमाटर': 'Tomatoes',
    'tomato': 'Tomatoes',
    'tomatoes': 'Tomatoes',
    'आलू': 'Potatoes',
    'potato': 'Potatoes',
    'potatoes': 'Potatoes',
    'प्याज': 'Onions',
    'onion': 'Onions',
    'onions': 'Onions',
    'चावल': 'Rice',
    'rice': 'Rice',
    'गेहूं': 'Wheat Flour',
    'wheat': 'Wheat Flour',
    'चीनी': 'Sugar',
    'sugar': 'Sugar',
    'नमक': 'Salt',
    'salt': 'Salt',
    'तेल': 'Cooking Oil',
    'oil': 'Cooking Oil',
    'चाय': 'Tea',
    'tea': 'Tea',
    'कॉफी': 'Coffee',
    'coffee': 'Coffee',
    'दूध': 'Milk',
    'milk': 'Milk',
    'ब्रेड': 'Bread',
    'bread': 'Bread',
    'अंडे': 'Eggs',
    'egg': 'Eggs',
    'eggs': 'Eggs',
    'साबुन': 'Soap',
    'soap': 'Soap',
    'शैंपू': 'Shampoo',
    'shampoo': 'Shampoo',
}

# Demo product prices (in rupees per unit) - used when product not found in database
DEMO_PRODUCT_PRICES = {
    'Tomatoes': 50.00,      # ₹50/kg
    'Potatoes': 35.00,       # ₹35/kg
    'Onions': 40.00,         # ₹40/kg
    'Rice': 50.00,           # ₹50/kg
    'Wheat Flour': 40.00,    # ₹40/kg
    'Sugar': 45.00,          # ₹45/kg
    'Salt': 20.00,           # ₹20/kg
    'Cooking Oil': 120.00,   # ₹120/liter
    'Tea': 200.00,          # ₹200/kg
    'Coffee': 300.00,       # ₹300/kg
    'Milk': 60.00,          # ₹60/liter
    'Bread': 30.00,         # ₹30/pack
    'Eggs': 80.00,          # ₹80/dozen (or per piece)
    'Soap': 25.00,          # ₹25/piece
    'Shampoo': 150.00,      # ₹150/bottle
}

# Quantity units mapping
QUANTITY_UNITS = {
    'किलो': 'kg',
    'kg': 'kg',
    'kilo': 'kg',
    'kilogram': 'kg',
    'ग्राम': 'gram',
    'gram': 'gram',
    'grams': 'gram',
    'पीस': 'piece',
    'piece': 'piece',
    'pieces': 'piece',
    'पैक': 'pack',
    'pack': 'pack',
    'packet': 'pack',
    'लिटर': 'liter',
    'liter': 'liter',
    'litre': 'liter',
    'l': 'liter',
}


def lookup_product_price(product_name, shopkeeper_id='shop_demo'):
    """
    Look up product price from database
    
    Args:
        product_name: Product name (English)
        shopkeeper_id: Shopkeeper ID (default: 'shop_demo')
    
    Returns:
        float: Product price per unit in rupees, or None if not found
    """
    if not DATABASE_AVAILABLE:
        return None
    
    try:
        # Try to find shopkeeper first
        if shopkeeper_id == 'shop_demo':
            # Get first shopkeeper as demo
            shopkeeper = Shopkeeper.objects().first()
            if not shopkeeper:
                return None
            shopkeeper_id = str(shopkeeper.id)
        else:
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        
        # Search for product (case-insensitive)
        product = Product.objects(
            shopkeeper_id=shopkeeper_id,
            name__iexact=product_name
        ).first()
        
        if product:
            return product.price
        else:
            # Try partial match
            product = Product.objects(
                shopkeeper_id=shopkeeper_id,
                name__icontains=product_name
            ).first()
            if product:
                return product.price
        
        return None
    except Exception as e:
        print(f"⚠️  Error looking up product: {e}")
        return None


def extract_product_and_quantity(transcript):
    """
    Extract product name and quantity from transcript
    
    Returns:
        tuple: (product_name_english, quantity, unit) or (None, None, None)
    """
    import re
    transcript_lower = transcript.lower()
    
    # Extract quantity
    quantity = None
    unit = None
    
    # Pattern: "1 किलो", "2 kg", "500 ग्राम", etc.
    quantity_patterns = [
        (r'(\d+(?:\.\d+)?)\s*(किलो|kg|kilo|kilogram)', 'kg'),
        (r'(\d+(?:\.\d+)?)\s*(ग्राम|gram|grams)', 'gram'),
        (r'(\d+)\s*(पीस|piece|pieces)', 'piece'),
        (r'(\d+)\s*(पैक|pack|packet)', 'pack'),
        (r'(\d+(?:\.\d+)?)\s*(लिटर|liter|litre|l)', 'liter'),
    ]
    
    for pattern, unit_type in quantity_patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            quantity = float(match.group(1))
            unit = unit_type
            break
    
    # If no unit found, look for standalone numbers (assume kg for common items)
    if quantity is None:
        numbers = re.findall(r'\d+(?:\.\d+)?', transcript)
        if numbers:
            # Take first number as quantity (likely quantity, not price)
            quantity = float(numbers[0])
            unit = 'kg'  # Default unit
    
    # Extract product name
    product_name = None
    
    # Try to find product name from mapping
    for hindi_name, english_name in PRODUCT_MAPPING.items():
        if hindi_name.lower() in transcript_lower or hindi_name in transcript:
            product_name = english_name
            break
    
    return product_name, quantity, unit


def parse_transaction(transcript, language, shopkeeper_id='shop_demo'):
    """
    Parse transcript to extract transaction details.
    Enhanced parser that extracts product names, quantities, and calculates prices.
    """
    import re
    transcript_lower = transcript.lower()
    
    # Detect transaction type (only sale and credit, no repay)
    tx_type = 'credit'
    if any(word in transcript_lower for word in ['sale', 'buy', 'purchase', 'खरीद', 'बिक्री']):
        tx_type = 'sale'
    
    # Extract product name and quantity
    product_name, quantity, unit = extract_product_and_quantity(transcript)
    
    # Try to get product price from database
    product_price = None
    if product_name:
        product_price = lookup_product_price(product_name, shopkeeper_id)
        if product_price:
            print(f"✅ Found product in database: {product_name} @ ₹{product_price:.2f}/{unit or 'unit'}")
        elif product_name in DEMO_PRODUCT_PRICES:
            # Use demo price if product not found in database
            product_price = DEMO_PRODUCT_PRICES[product_name]
            print(f"📦 Using demo price for {product_name}: ₹{product_price:.2f}/{unit or 'unit'}")
        else:
            print(f"⚠️  Product {product_name} not found in database or demo prices")
    
    # Calculate amount from product price × quantity
    amount = None
    if product_price and quantity:
        # Convert quantity to base unit for calculation
        if unit == 'gram':
            quantity_kg = quantity / 1000  # Convert grams to kg
            amount = int(product_price * quantity_kg * 100)  # Convert to paise
        elif unit == 'liter':
            amount = int(product_price * quantity * 100)  # Convert to paise
        else:  # kg, piece, pack (assume price is per unit)
            amount = int(product_price * quantity * 100)  # Convert to paise
        print(f"💰 Calculated amount: {quantity} {unit or ''} × ₹{product_price:.2f} = ₹{amount/100:.2f}")
    
    # Extract amount - look for amount keywords first (if not calculated from product)
    if amount is None:
        # Hindi amount patterns: "500 रुपये", "500 रु", "₹500", "500 rupees"
        amount_patterns = [
            r'(\d+)\s*रुपये',  # "500 रुपये"
            r'(\d+)\s*रु',     # "500 रु"
            r'₹\s*(\d+)',      # "₹500"
            r'(\d+)\s*rupees',  # "500 rupees"
            r'(\d+)\s*rs',      # "500 rs"
            r'(\d+)\s*rupee',  # "500 rupee"
        ]
        
        # Try to find amount with keywords first
        for pattern in amount_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                amount_value = int(match.group(1))
                amount = amount_value * 100  # Convert rupees to paise
                break
    
    # If no amount keyword found, look for numbers near amount-related words
    if amount is None:
        # Look for numbers followed by amount-related words
        amount_context_patterns = [
            r'(\d+)\s*(?:का|की|को)\s*(?:उधार|क्रेडिट|credit)',  # "500 का उधार"
            r'(?:उधार|क्रेडिट|credit)\s*(?:दे|का|की)\s*(\d+)',  # "उधार दे 500"
            r'(\d+)\s*(?:का|की)\s*(?:मूल्य|price|cost)',        # "500 का मूल्य"
        ]
        
        for pattern in amount_context_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                amount_value = int(match.group(1))
                amount = amount_value * 100  # Convert rupees to paise
                break
    
    # If still no amount found, look for all numbers and use heuristics
    if amount is None:
        all_numbers = re.findall(r'\d+', transcript)
        if all_numbers:
            numbers = [int(n) for n in all_numbers]
            
            # For credit transactions, if there's a number > 10, it's likely the amount
            # For sale transactions, the larger number is usually the price
            if tx_type == 'credit':
                # Filter out small numbers (likely quantities like 1, 2 kg)
                large_numbers = [n for n in numbers if n >= 10]
                if large_numbers:
                    amount_value = max(large_numbers)
                    amount = amount_value * 100  # Convert rupees to paise
                elif numbers:
                    # If only small numbers, use the largest but warn
                    amount_value = max(numbers)
                    amount = amount_value * 100
                    print(f"⚠️  Warning: Could not find explicit amount. Using {amount_value} as amount.")
            else:  # sale
                # For sales, use the largest number as price
                amount_value = max(numbers)
                amount = amount_value * 100  # Convert rupees to paise
    
    # Default amount if nothing found
    if amount is None:
        amount = 50000  # Default ₹500
        print(f"⚠️  Warning: No amount found in transcript. Using default ₹500.")
    
    # Customer ID will be set from database in main() function
    # Don't set it here - it will be overridden
    
    return {
        'type': tx_type,
        'amount': amount,
        'customer_id': None,  # Will be set from database
        'customer_confirmed': True,  # Auto-confirm for demo
        'product_name': product_name,
        'quantity': quantity,
        'unit': unit,
        'product_price': product_price
    }


def send_to_backend(transcript_data, parsed_data, shopkeeper_id='shop_demo'):
    """Send transaction to backend API"""
    print("\n" + "=" * 70)
    print("📡 SENDING TO BACKEND")
    print("=" * 70)
    
    # Prepare transaction data
    transaction_data = {
        'transcript': transcript_data['transcript'],
        'type': parsed_data['type'],
        'amount': parsed_data['amount'],
        'customer_id': parsed_data['customer_id'],
        'shopkeeper_id': shopkeeper_id,
        'customer_confirmed': parsed_data['customer_confirmed'],
        'language': transcript_data['language']
    }
    
    # Add product information if available
    if parsed_data.get('product_name'):
        transaction_data['product'] = parsed_data['product_name']
        if parsed_data.get('quantity'):
            transaction_data['quantity'] = parsed_data['quantity']
        if parsed_data.get('unit'):
            transaction_data['unit'] = parsed_data['unit']
        if parsed_data.get('product_price'):
            transaction_data['price'] = parsed_data['product_price']
    
    print(f"\n📤 Sending transaction:")
    print(f"   Type: {transaction_data['type']}")
    if transaction_data.get('product'):
        print(f"   Product: {transaction_data['product']}")
        if transaction_data.get('quantity'):
            print(f"   Quantity: {transaction_data['quantity']} {transaction_data.get('unit', '')}")
        if transaction_data.get('price'):
            print(f"   Price per unit: ₹{transaction_data['price']:.2f}")
    print(f"   Amount: ₹{transaction_data['amount']:.2f}")
    print(f"   Customer: {transaction_data['customer_id']}")
    print(f"   Language: {transaction_data['language']}")
    
    try:
        response = requests.post(API_URL, json=transaction_data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            
            print("\n✅ TRANSACTION CREATED!")
            print(f"   Transaction ID: {result.get('id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            
            # Check if verification data exists (from actual API)
            if 'verification' in result:
                verification = result['verification']
                print(f"\n✅ VERIFICATION COMPLETE!")
                print(f"   Verification Status: {verification.get('status', 'N/A')}")
                
                # Check blockchain write
                blockchain_tx_id = verification.get('blockchain_tx_id')
                blockchain_block = verification.get('blockchain_block_number')
                
                if blockchain_tx_id:
                    print(f"\n⛓️  BLOCKCHAIN WRITE SUCCESS!")
                    print(f"   TX Hash: {blockchain_tx_id}")
                    if blockchain_block:
                        print(f"   Block Number: {blockchain_block}")
                    print(f"\n✅ This transaction is now visible in Admin Dashboard → Blockchain Logs!")
                else:
                    print(f"\n💾 Stored in database (pending blockchain write)")
                    print(f"   Verification Status: {verification.get('status', 'N/A')}")
                
                # Show fraud check if available
                fraud_score = verification.get('fraud_score')
                fraud_risk = verification.get('fraud_risk_level')
                if fraud_score is not None:
                    print(f"\n⚠️  FRAUD CHECK:")
                    print(f"   Risk Level: {fraud_risk or 'N/A'}")
                    print(f"   Score: {fraud_score:.2f}")
            else:
                # Fallback for test API format
                if 'verification' in result:
                    verification = result['verification']
                    print(f"\n✅ TRANSACTION VERIFIED!")
                    print(f"   Status: {verification.get('status', 'N/A')}")
                    if verification.get('should_write_to_blockchain'):
                        if result.get('blockchain'):
                            blockchain = result['blockchain']
                            print(f"\n⛓️  BLOCKCHAIN WRITE SUCCESS!")
                            print(f"   TX Hash: {blockchain.get('tx_hash', 'N/A')}")
                            print(f"   Block: {blockchain.get('block_number', 'N/A')}")
                            print(f"\n✅ This transaction is now visible in Admin Dashboard → Blockchain Logs!")
            
            return True
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to backend API. Is the Flask server running?")
        print("   Start it with: cd helloKittyFanclub\\backend && python run.py")
        print("   Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def manual_input_mode():
    """Fallback: Manual text input if microphone not available"""
    print("\n" + "=" * 70)
    print("⌨️  MANUAL INPUT MODE")
    print("=" * 70)
    print("\nEnter transaction transcript:")
    print("   Examples:")
    print("   - राहुल को 500 रुपये का उधार दे दो")
    print("   - Give 500 rupees credit to Rahul")
    print("   - 2 किलो चावल 120 रुपये")
    print()
    
    transcript = input("📝 Transcript: ").strip()
    
    if not transcript:
        print("❌ Empty transcript")
        return None
    
    # Detect language
    language = 'hi-IN'
    if all(ord(c) < 128 for c in transcript):  # ASCII only = English
        language = 'en-IN'
    
    return {'transcript': transcript, 'language': language}


def show_blockchain_status():
    """Show current blockchain status"""
    try:
        response = requests.get(API_STATUS_URL, timeout=2)
        if response.status_code == 200:
            status = response.json()
            print("\n" + "=" * 70)
            print("⛓️  BLOCKCHAIN STATUS")
            print("=" * 70)
            print(f"   Connected: {status.get('connected', False)}")
            if status.get('connected'):
                print(f"   Address: {status.get('address', 'N/A')}")
                print(f"   Contract: {status.get('contract_address', 'N/A')[:20]}...")
                print(f"   Balance: {status.get('balance_eth', 0):.4f} ETH")
                print(f"   Next TX ID: {status.get('next_transaction_id', 0)}")
            return True
    except:
        pass
    return False


def main():
    """Main demo loop"""
    print("\n" + "=" * 70)
    print("🎤 KIRANA VOICE TRANSACTION DEMO")
    print("=" * 70)
    print("\nThis demo captures voice input and stores transactions on blockchain.")
    print("Perfect for hackathon judges to test!")
    
    # Check API connection
    print("\n🔍 Checking API connection...")
    if not check_api_connection():
        print("\n❌ Backend API is not running!")
        print("\n📋 To start the backend API:")
        print("   1. Open a new terminal")
        print("   2. cd helloKittyFanclub\\backend")
        print("   3. python run.py")
        print("\n   Make sure it's running on http://localhost:5000")
        print("   Then run this script again.")
        return
    
    print("✅ API is running!")
    
    # Get demo shopkeeper and customer IDs from database
    print("\n🔍 Getting demo shopkeeper and customer IDs...")
    shopkeeper_id, customer_id = get_demo_ids()
    
    if not shopkeeper_id or not customer_id:
        print("\n⚠️  Could not get shopkeeper/customer IDs from database")
        print("   Make sure you have seeded the database with:")
        print("   python database/seeders/seed_data.py")
        print("\n   Exiting...")
        return
    
    print(f"✅ Using Shopkeeper ID: {shopkeeper_id}")
    print(f"✅ Using Customer ID: {customer_id}")
    
    # Show blockchain status
    show_blockchain_status()
    
    # Main loop
    while True:
        print("\n" + "=" * 70)
        print("🎯 READY FOR VOICE INPUT")
        print("=" * 70)
        print("\nOptions:")
        print("  1. Voice input (microphone)")
        print("  2. Manual text input")
        print("  3. Show blockchain status")
        print("  4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            if not SPEECH_RECOGNITION_AVAILABLE:
                print("\n⚠️  Voice input not available. Use option 2 for manual input.")
                continue
            
            # Get voice input
            transcript_data = get_voice_input()
            if not transcript_data:
                continue
            
            # Parse transaction using new Hindi parser
            print("\n🔍 Parsing Hindi transaction...")
            
            if HINDI_PARSER_AVAILABLE and transcript_data['language'] == 'hi-IN':
                # Get customer list for fuzzy matching
                customer_list = get_customer_list()
                
                # Create product price lookup function
                lookup_price_fn = create_product_price_lookup(shopkeeper_id)
                
                # Parse using new Hindi parser
                hindi_result = parse_hindi_transaction(
                    transcript=transcript_data['transcript'],
                    customer_list=customer_list,
                    product_map=HINDI_PRODUCT_MAPPING if HINDI_PARSER_AVAILABLE else None,
                    lookup_product_price=lookup_price_fn
                )
                
                # Convert to format expected by send_to_backend
                # Amount is in rupees (backend will convert to paise)
                parsed_data = {
                    'type': hindi_result['type'],
                    'amount': hindi_result['amount'] or 500.0,  # Default ₹500 if not found (in rupees)
                    'customer_id': hindi_result['customer_id'] or customer_id,  # Fallback to random customer
                    'customer_confirmed': True,
                    'product_name': hindi_result['product'],
                    'quantity': hindi_result['quantity'],
                    'unit': hindi_result['unit'],
                    'product_price': hindi_result['price_per_unit'],
                    'confirmation_text_hindi': hindi_result.get('confirmation_text_hindi', '')
                }
            else:
                # Fallback to old parser
                parsed_data = parse_transaction(
                    transcript_data['transcript'],
                    transcript_data['language'],
                    shopkeeper_id=shopkeeper_id
                )
                parsed_data['customer_id'] = customer_id
            
            # If amount seems wrong (too small or default), ask user
            if parsed_data.get('amount', 0) <= 10:  # Less than ₹10
                print(f"\n⚠️  Could not extract amount from transcript.")
                print(f"   Transcript: {transcript_data['transcript']}")
                if parsed_data.get('product_name'):
                    print(f"   Product: {parsed_data['product_name']}")
                    if parsed_data.get('quantity'):
                        print(f"   Quantity: {parsed_data['quantity']} {parsed_data.get('unit', '')}")
                amount_input = input("   Enter amount in rupees (or press Enter for ₹500): ").strip()
                if amount_input:
                    try:
                        amount_rupees = float(amount_input)
                        parsed_data['amount'] = amount_rupees  # Keep in rupees
                    except ValueError:
                        print("   Invalid amount, using ₹500")
                        parsed_data['amount'] = 500.0
            
            # Confirm details
            print(f"\n📋 Transaction Details:")
            print(f"   Type: {parsed_data['type']}")
            if parsed_data.get('product_name'):
                print(f"   Product: {parsed_data['product_name']}")
                if parsed_data.get('quantity'):
                    print(f"   Quantity: {parsed_data['quantity']} {parsed_data.get('unit', '')}")
                if parsed_data.get('product_price'):
                    print(f"   Price per unit: ₹{parsed_data['product_price']:.2f}")
            print(f"   Amount: ₹{parsed_data.get('amount', 0):.2f}")
            print(f"   Customer: {parsed_data.get('customer_id', 'N/A')}")
            
            # Show Hindi confirmation text if available
            if parsed_data.get('confirmation_text_hindi'):
                print(f"\n📝 {parsed_data['confirmation_text_hindi']}")
            
            confirm = input("\n✅ Confirm? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled")
                continue
            
            # Send to backend
            send_to_backend(transcript_data, parsed_data, shopkeeper_id=shopkeeper_id)
            
        elif choice == '2':
            # Manual input
            transcript_data = manual_input_mode()
            if not transcript_data:
                continue
            
            # Parse transaction using new Hindi parser
            print("\n🔍 Parsing Hindi transaction...")
            
            if HINDI_PARSER_AVAILABLE and transcript_data['language'] == 'hi-IN':
                # Get customer list for fuzzy matching
                customer_list = get_customer_list()
                
                # Create product price lookup function
                lookup_price_fn = create_product_price_lookup(shopkeeper_id)
                
                # Parse using new Hindi parser
                hindi_result = parse_hindi_transaction(
                    transcript=transcript_data['transcript'],
                    customer_list=customer_list,
                    product_map=HINDI_PRODUCT_MAPPING if HINDI_PARSER_AVAILABLE else None,
                    lookup_product_price=lookup_price_fn
                )
                
                # Convert to format expected by send_to_backend
                # Amount is in rupees (backend will convert to paise)
                parsed_data = {
                    'type': hindi_result['type'],
                    'amount': hindi_result['amount'] or 500.0,  # Default ₹500 if not found (in rupees)
                    'customer_id': hindi_result['customer_id'] or customer_id,  # Fallback to random customer
                    'customer_confirmed': True,
                    'product_name': hindi_result['product'],
                    'quantity': hindi_result['quantity'],
                    'unit': hindi_result['unit'],
                    'product_price': hindi_result['price_per_unit'],
                    'confirmation_text_hindi': hindi_result.get('confirmation_text_hindi', '')
                }
            else:
                # Fallback to old parser
                parsed_data = parse_transaction(
                    transcript_data['transcript'],
                    transcript_data['language'],
                    shopkeeper_id=shopkeeper_id
                )
                parsed_data['customer_id'] = customer_id
            
            # If amount seems wrong (too small or default), ask user
            if parsed_data.get('amount', 0) <= 10:  # Less than ₹10
                print(f"\n⚠️  Could not extract amount from transcript.")
                print(f"   Transcript: {transcript_data['transcript']}")
                if parsed_data.get('product_name'):
                    print(f"   Product: {parsed_data['product_name']}")
                    if parsed_data.get('quantity'):
                        print(f"   Quantity: {parsed_data['quantity']} {parsed_data.get('unit', '')}")
                amount_input = input("   Enter amount in rupees (or press Enter for ₹500): ").strip()
                if amount_input:
                    try:
                        amount_rupees = float(amount_input)
                        parsed_data['amount'] = amount_rupees  # Keep in rupees
                    except ValueError:
                        print("   Invalid amount, using ₹500")
                        parsed_data['amount'] = 500.0
            
            # Confirm details
            print(f"\n📋 Transaction Details:")
            print(f"   Type: {parsed_data['type']}")
            if parsed_data.get('product_name'):
                print(f"   Product: {parsed_data['product_name']}")
                if parsed_data.get('quantity'):
                    print(f"   Quantity: {parsed_data['quantity']} {parsed_data.get('unit', '')}")
                if parsed_data.get('product_price'):
                    print(f"   Price per unit: ₹{parsed_data['product_price']:.2f}")
            print(f"   Amount: ₹{parsed_data.get('amount', 0):.2f}")
            print(f"   Customer: {parsed_data.get('customer_id', 'N/A')}")
            
            # Show Hindi confirmation text if available
            if parsed_data.get('confirmation_text_hindi'):
                print(f"\n📝 {parsed_data['confirmation_text_hindi']}")
            
            confirm = input("\n✅ Confirm? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled")
                continue
            
            # Send to backend
            send_to_backend(transcript_data, parsed_data, shopkeeper_id=shopkeeper_id)
            
        elif choice == '3':
            show_blockchain_status()
            
        elif choice == '4':
            print("\n👋 Exiting demo. Thank you!")
            break
        
        else:
            print("\n❌ Invalid option")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

