"""
Voice Transaction Parser Service

Unified parser for Hindi, English, and Kannada voice transactions.
Routes to appropriate language-specific parser based on language code.
"""

import re
import logging
from typing import Dict, Optional, List, Any, Callable
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

# Add blockchain directory to path for importing hindi_parser
blockchain_dir = Path(__file__).parent
if str(blockchain_dir) not in sys.path:
    sys.path.insert(0, str(blockchain_dir))

try:
    from hindi_parser import parse_hindi_transaction, PRODUCT_MAPPING as HINDI_PRODUCT_MAPPING
    HINDI_PARSER_AVAILABLE = True
except ImportError as e:
    HINDI_PARSER_AVAILABLE = False
    HINDI_PRODUCT_MAPPING = {}
    logger.warning(f"Hindi parser not available: {e}")

# Try to import database models
try:
    from database.models import Customer, Product, Shopkeeper
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logger.warning("Database models not available")

# Try to import fuzzy matching
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    try:
        from difflib import SequenceMatcher
        FUZZY_AVAILABLE = True
    except ImportError:
        FUZZY_AVAILABLE = False


# ============================================================================
# NUMBER WORD MAPPINGS (Hindi and English)
# ============================================================================

# Hindi number words (0-20, then tens, hundreds)
HINDI_NUMBER_WORDS = {
    'एक': 1, 'दो': 2, 'तीन': 3, 'चार': 4, 'पांच': 5, 'पाँच': 5,
    'छह': 6, 'छः': 6, 'सात': 7, 'आठ': 8, 'नौ': 9, 'दस': 10,
    'ग्यारह': 11, 'बारह': 12, 'तेरह': 13, 'चौदह': 14, 'पंद्रह': 15,
    'सोलह': 16, 'सत्रह': 17, 'अठारह': 18, 'उन्नीस': 19, 'बीस': 20,
    'तीस': 30, 'चालीस': 40, 'पचास': 50, 'साठ': 60, 'सत्तर': 70,
    'अस्सी': 80, 'नब्बे': 90, 'सौ': 100, 'हज़ार': 1000
}

# English number words (0-20, then tens, hundreds)
ENGLISH_NUMBER_WORDS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
    'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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
        logger.warning(f"Error getting customer list: {e}")
        return []


def create_product_price_lookup(shopkeeper_id: str) -> Callable[[str], Optional[float]]:
    """
    Create a function to lookup product prices for a shopkeeper.
    
    Args:
        shopkeeper_id: Shopkeeper ID
    
    Returns:
        Function that takes product_name and returns price in rupees, or None
    """
    def lookup_price(product_name: str) -> Optional[float]:
        if not DATABASE_AVAILABLE:
            return None
        
        try:
            # Try to find shopkeeper first
            if shopkeeper_id == 'shop_demo' or not shopkeeper_id:
                shopkeeper = Shopkeeper.objects().first()
                if not shopkeeper:
                    return None
                actual_shopkeeper_id = str(shopkeeper.id)
            else:
                Shopkeeper.objects.get(id=shopkeeper_id)
                actual_shopkeeper_id = shopkeeper_id
            
            # Search for product (case-insensitive)
            product = Product.objects(
                shopkeeper_id=actual_shopkeeper_id,
                name__iexact=product_name
            ).first()
            
            if product:
                return product.price
            else:
                # Try partial match
                product = Product.objects(
                    shopkeeper_id=actual_shopkeeper_id,
                    name__icontains=product_name
                ).first()
                if product:
                    return product.price
            
            return None
        except Exception as e:
            logger.warning(f"Error looking up product price: {e}")
            return None
    
    return lookup_price


def fuzzy_match_customer(customer_name: str, customer_list: List[Dict[str, Any]], threshold: float = 0.6) -> Optional[str]:
    """
    Fuzzy match customer name against customer list.
    
    Args:
        customer_name: Name to match
        customer_list: List of customer dicts with 'id' and 'name'
        threshold: Similarity threshold (0.0-1.0)
    
    Returns:
        Customer ID if match found, None otherwise
    """
    if not customer_list or not customer_name:
        return None
    
    if FUZZY_AVAILABLE:
        try:
            from rapidfuzz import process
            result = process.extractOne(
                customer_name,
                [c['name'] for c in customer_list],
                scorer=fuzz.ratio
            )
            if result and result[1] >= threshold * 100:
                matched_name = result[0]
                for customer in customer_list:
                    if customer['name'] == matched_name:
                        return customer['id']
        except ImportError:
            pass
    
    # Fallback to simple substring match
    customer_name_lower = customer_name.lower()
    for customer in customer_list:
        if customer_name_lower in customer['name'].lower() or customer['name'].lower() in customer_name_lower:
            return customer['id']
    
    return None


# ============================================================================
# ENGLISH PARSER
# ============================================================================

# English transaction type keywords
# CREDIT: Money owed / goods taken on credit
ENGLISH_CREDIT_KEYWORDS = ['credit', 'loan', 'udhar', 'udhari', 'lend', 'advance', 'borrowed', 'due']
# SALE: Stock going out to customers
ENGLISH_SALE_KEYWORDS = ['sale', 'sell', 'sold', 'sold to', 'gave', 'given']
# BUYING: Stock coming in (inventory purchase from supplier/vendor)
ENGLISH_BUYING_KEYWORDS = ['buy', 'bought', 'purchase', 'purchased', 'stock', 'inventory', 'ordered']

# English amount keywords
ENGLISH_AMOUNT_KEYWORDS = ['rupees', 'rupee', 'rs', '₹', 'price', 'cost', 'amount', 'value']

# English quantity units
ENGLISH_QUANTITY_UNITS = {
    'kg': 'kg',
    'kilo': 'kg',
    'kilogram': 'kg',
    'gram': 'gram',
    'grams': 'gram',
    'liter': 'liter',
    'litre': 'liter',
    'l': 'liter',
    'pack': 'pack',
    'packet': 'pack',
    'piece': 'piece',
    'pieces': 'piece',
    'pcs': 'piece',
}

# Common English product names
ENGLISH_PRODUCT_NAMES = [
    'tomatoes', 'potatoes', 'onions', 'rice', 'wheat', 'flour', 'sugar', 'salt',
    'oil', 'tea', 'coffee', 'milk', 'bread', 'eggs', 'soap', 'shampoo',
    'brinjal', 'okra', 'cabbage', 'cauliflower', 'lentils', 'chickpeas'
]


def parse_english_transaction(
    transcript: str,
    customer_list: List[Dict[str, Any]],
    product_map: Dict[str, str] = None,
    lookup_product_price: Callable[[str], Optional[float]] = None
) -> Dict[str, Any]:
    """
    Parse English voice transaction transcript.
    
    Args:
        transcript: English transcript text
        customer_list: List of customer dicts with 'id' and 'name'
        product_map: Dictionary mapping product names (not used for English)
        lookup_product_price: Function to lookup product price
    
    Returns:
        Complete transaction object with all fields
    """
    transcript_lower = transcript.lower()
    
    # Step 1: Parse transaction type
    # Priority: BUYING > SALE > CREDIT (more specific first)
    tx_type = 'credit'  # Default
    is_buying = False  # Flag to track if this is a buying transaction
    
    if any(keyword in transcript_lower for keyword in ENGLISH_BUYING_KEYWORDS):
        tx_type = 'sale'  # Map to 'sale' type (database constraint)
        is_buying = True  # Mark as buying for metadata
    elif any(keyword in transcript_lower for keyword in ENGLISH_SALE_KEYWORDS):
        tx_type = 'sale'
    elif any(keyword in transcript_lower for keyword in ENGLISH_CREDIT_KEYWORDS):
        tx_type = 'credit'
    
    # Step 2: Extract customer name
    customer_id = None
    customer_name = None
    
    # Look for customer name patterns: "customer <name>", "<name> customer", "for <name>", "to <name>"
    customer_patterns = [
        r'customer\s+([^\s,]+)',  # "customer <name>"
        r'([^\s,]+)\s+customer',  # "<name> customer"
        r'for\s+([^\s,]+)',  # "for <name>"
        r'to\s+([^\s,]+)',  # "to <name>"
        r'^([^\s,]+)\s+',  # Name at start: "John 500 rupees"
        r'([^\s,]+)\s+\d+',  # Name before number: "...John 500"
        r'([^\s,]+)\s+rupees?',  # Name before "rupees"
        r'([^\s,]+)\s+rs\.?',  # Name before "rs"
    ]
    
    for pattern in customer_patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            potential_name = match.group(1).strip()
            
            # Skip if it's a number or common word
            if potential_name.isdigit() or potential_name.lower() in ['rupees', 'rupee', 'rs', '₹']:
                continue
            
            customer_id = fuzzy_match_customer(potential_name, customer_list)
            if customer_id:
                for customer in customer_list:
                    if customer['id'] == customer_id:
                        customer_name = customer['name']
                        break
                break
            
            # Fallback: Use extracted name even if fuzzy match fails (for new customers)
            if potential_name and len(potential_name) > 1:
                if not potential_name.isdigit() and len(potential_name) >= 2:
                    customer_name = potential_name
                    break
    
    # Final fallback: Extract first word as customer name if nothing found
    if customer_name is None:
        words = transcript.split()
        skip_words = ['rupees', 'rupee', 'rs', '₹', 'customer', 'for', 'to', 'credit', 'sale', 'buy', 'bought', 'purchase']
        for word in words:
            # Remove common punctuation
            clean_word = word.strip('.,!?;:')
            if clean_word.isdigit() or clean_word.lower() in skip_words:
                continue
            if clean_word and len(clean_word) >= 2:
                customer_name = clean_word
                break
    
    # Step 3: Extract product (for sale transactions)
    product = None
    if tx_type == 'sale':
        for prod_name in ENGLISH_PRODUCT_NAMES:
            if prod_name in transcript_lower:
                product = prod_name.capitalize()
                break
    
    # Step 4: Extract quantity and unit (for sale transactions)
    quantity = None
    unit = None
    if tx_type == 'sale':
        # Pattern 1: Numeric digits - "2 kg", "1.5 liter", "3 pieces"
        qty_patterns = [
            r'(\d+\.?\d*)\s*(kg|kilo|kilogram|gram|grams|liter|litre|l|pack|packet|piece|pieces|pcs)',
            r'(\d+\.?\d*)\s*(?:of|x)\s*(\w+)',
        ]
        
        for pattern in qty_patterns:
            match = re.search(pattern, transcript_lower)
            if match:
                try:
                    quantity = float(match.group(1))
                    unit_str = match.group(2) if len(match.groups()) > 1 else None
                    if unit_str:
                        unit = ENGLISH_QUANTITY_UNITS.get(unit_str.lower(), unit_str.lower())
                    break
                except (ValueError, IndexError):
                    continue
        
        # Pattern 2: English number words - "two kg", "three packets", "one piece"
        if quantity is None:
            for english_number, numeric_value in ENGLISH_NUMBER_WORDS.items():
                for unit_key, unit_value in ENGLISH_QUANTITY_UNITS.items():
                    pattern = rf'{re.escape(english_number)}\s+{re.escape(unit_key)}'
                    match = re.search(pattern, transcript_lower)
                    if match:
                        quantity = float(numeric_value)
                        unit = unit_value
                        break
                if quantity is not None:
                    break
    
    # Step 5: Extract amount
    amount = None
    
    # Pattern: "500 rupees", "₹500", "500 rs", "500"
    amount_patterns = [
        r'₹\s*(\d+)',
        r'(\d+)\s*(?:rupees|rupee|rs|₹)',
        r'(?:rupees|rupee|rs|₹)\s*(\d+)',
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            try:
                amount_value = float(match.group(1))
                amount = amount_value  # In rupees
                break
            except (ValueError, IndexError):
                continue
    
    # If no amount found, look for standalone numbers
    # BUT exclude numbers that are part of quantity patterns
    if amount is None:
        # Find all numbers in the transcript
        all_numbers = re.findall(r'\d+(?:\.\d+)?', transcript)
        
        if all_numbers:
            # Convert to floats for comparison
            number_values = [float(n) for n in all_numbers]
            
            # If we found a quantity, exclude that number from amount consideration
            if quantity is not None:
                # Remove the quantity value from consideration
                number_values = [n for n in number_values if abs(n - quantity) > 0.01]
            
            # Also exclude numbers that are immediately followed by quantity units
            # (they're definitely quantities, not amounts)
            excluded_numbers = set()
            for unit in ENGLISH_QUANTITY_UNITS.keys():
                pattern = rf'(\d+(?:\.\d+)?)\s*{re.escape(unit)}'
                for match in re.finditer(pattern, transcript_lower):
                    try:
                        excluded_numbers.add(float(match.group(1)))
                    except (ValueError, IndexError):
                        pass
            
            # Remove excluded numbers
            number_values = [n for n in number_values if n not in excluded_numbers]
            
            # Only use remaining numbers as potential amounts
            # Prefer larger numbers (more likely to be amounts than small quantities)
            if number_values:
                try:
                    # Use the largest remaining number as amount
                    amount = max(number_values)
                except (ValueError, TypeError):
                    pass
    
    # Step 6: Calculate price per unit (for sale transactions)
    price_per_unit = None
    if tx_type == 'sale' and product and quantity and lookup_product_price:
        try:
            price_per_unit = lookup_product_price(product)
        except Exception as e:
            logger.warning(f"Error looking up product price: {e}")
    
    # Assemble result
    result = {
        'type': tx_type,
        'amount': amount,
        'customer_id': customer_id,
        'customer_name': customer_name,
        'product': product,
        'quantity': quantity,
        'unit': unit,
        'price_per_unit': price_per_unit,
        'confirmation_text': f"Transaction: {tx_type} of {amount or 'N/A'} rupees" if amount else "Transaction recorded"
    }
    
    # Add metadata for buying transactions (mapped to 'sale' type)
    if is_buying:
        result['is_buying'] = True  # Flag to indicate this is a buying/inventory transaction
        result['transaction_subtype'] = 'buying'  # Store original intent
    
    return result


# ============================================================================
# KANNADA PARSER
# ============================================================================

# Kannada transaction type keywords
KANNADA_CREDIT_KEYWORDS = ['ಉದಾರ', 'ಕರ್ಜ', 'ಸಾಲ', 'ಉದಾರಿ']  # udhar, karja, saal, udhari
KANNADA_SALE_KEYWORDS = ['ಮಾರಾಟ', 'ಖರೀದಿ', 'ಕೊಳ್ಳು', 'ಮಾರು']  # maraat, kharidi, kollu, maru

# Kannada amount keywords
KANNADA_AMOUNT_KEYWORDS = ['ರೂಪಾಯಿ', 'ರೂ', '₹', 'ಬೆಲೆ', 'ದಾಮ']  # rupayi, ru, ₹, bele, dam

# Kannada quantity units (Kannada → English)
KANNADA_QUANTITY_UNITS = {
    'ಕಿಲೋ': 'kg',      # kilo
    'ಕಿಲೋಗ್ರಾಂ': 'kg',  # kilogram
    'ಗ್ರಾಂ': 'gram',    # gram
    'ಲೀಟರ್': 'liter',   # liter
    'ಪ್ಯಾಕ್': 'pack',    # pack
    'ತುಂಡು': 'piece',    # piece
}

# Common Kannada product names (Kannada → English)
KANNADA_PRODUCT_NAMES = {
    'ಟೊಮಾಟೊ': 'Tomatoes',      # tomato
    'ಆಲೂಗಡ್ಡೆ': 'Potatoes',     # alugadde
    'ಈರುಳ್ಳಿ': 'Onions',         # eerulli
    'ಅಕ್ಕಿ': 'Rice',             # akki
    'ಗೋಧಿ': 'Wheat Flour',       # godhi
    'ಸಕ್ಕರೆ': 'Sugar',            # sakkare
    'ಉಪ್ಪು': 'Salt',              # uppu
    'ಎಣ್ಣೆ': 'Cooking Oil',       # enne
    'ಚಹಾ': 'Tea',                 # chaha
    'ಕಾಫಿ': 'Coffee',            # kaafi
    'ಹಾಲು': 'Milk',               # haalu
    'ಬ್ರೆಡ್': 'Bread',            # bread
    'ಮೊಟ್ಟೆ': 'Eggs',             # motte
}


def parse_kannada_transaction(
    transcript: str,
    customer_list: List[Dict[str, Any]],
    product_map: Dict[str, str] = None,
    lookup_product_price: Callable[[str], Optional[float]] = None
) -> Dict[str, Any]:
    """
    Parse Kannada voice transaction transcript.
    
    Args:
        transcript: Kannada transcript text
        customer_list: List of customer dicts with 'id' and 'name'
        product_map: Dictionary mapping product names (not used for Kannada)
        lookup_product_price: Function to lookup product price
    
    Returns:
        Complete transaction object with all fields
    """
    # Step 1: Parse transaction type
    tx_type = 'credit'
    if any(keyword in transcript for keyword in KANNADA_SALE_KEYWORDS):
        tx_type = 'sale'
    elif any(keyword in transcript for keyword in KANNADA_CREDIT_KEYWORDS):
        tx_type = 'credit'
    
    # Step 2: Extract customer name (simple pattern matching)
    customer_id = None
    customer_name = None
    
    # #region agent log
    import json, os, time
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.cursor', 'debug.log')
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location':'voice_parser.py:477','message':'Kannada customer extraction start','data':{'transcript':transcript[:100],'customer_list_len':len(customer_list) if customer_list else 0},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H1'})+'\n')
    except: pass
    # #endregion
    
    # Kannada postpositions to strip (ಗೆ, ಕ್ಕೆ, ನಿಗೆ, etc.)
    kannada_postpositions = ['ಗೆ', 'ಕ್ಕೆ', 'ನಿಗೆ', 'ಗಾಗಿ', 'ನಿಂದ', 'ದಿಂದ', 'ಅಲ್ಲಿ', 'ನಲ್ಲಿ']
    
    # Look for common patterns
    customer_patterns = [
        r'ಗ್ರಾಹಕ\s+([^\s,]+)',  # "customer <name>" or "customer <name>ಗೆ"
        r'([^\s,]+)\s+ಗ್ರಾಹಕ',  # "<name> customer"
        r'ಗ್ರಾಹಕ\s+([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)',  # "customer <name>ಗೆ" (explicit)
        r'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+[^\s]*ಉದಾರ',  # "<name>ಗೆ ... udhaar"
        r'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+[^\s]*ಕರ್ಜ',  # "<name>ಗೆ ... karja"
        r'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+[^\s]*ಸಾಲ',  # "<name>ಗೆ ... saal"
    ]
    
    for pattern in customer_patterns:
        match = re.search(pattern, transcript)
        if match:
            potential_name = match.group(1).strip()
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'location':'voice_parser.py:495','message':'Pattern matched','data':{'pattern':pattern,'matched_text':potential_name},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H1'})+'\n')
            except: pass
            # #endregion
            
            # Strip Kannada postpositions from the name
            original_name = potential_name
            for postpos in kannada_postpositions:
                if potential_name.endswith(postpos):
                    potential_name = potential_name[:-len(postpos)]
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({'location':'voice_parser.py:502','message':'Postposition stripped','data':{'original':original_name,'stripped':potential_name,'postpos':postpos},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H3'})+'\n')
                    except: pass
                    # #endregion
                    break
            
            # Try fuzzy matching
            customer_id = fuzzy_match_customer(potential_name, customer_list)
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({'location':'voice_parser.py:506','message':'Fuzzy match result','data':{'potential_name':potential_name,'customer_id':customer_id},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H2'})+'\n')
            except: pass
            # #endregion
            if customer_id:
                for customer in customer_list:
                    if customer['id'] == customer_id:
                        customer_name = customer['name']
                        break
                break
    
    # If no match found, try extracting name directly before credit keywords
    if customer_id is None:
        # Pattern: extract name before "ಗೆ" or "ಕ್ಕೆ" that appears before credit keywords
        credit_keyword_pattern = '|'.join(KANNADA_CREDIT_KEYWORDS)
        pattern = rf'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+[^\s]*?(?:{credit_keyword_pattern})'
        match = re.search(pattern, transcript)
        if match:
            potential_name = match.group(1).strip()
            customer_id = fuzzy_match_customer(potential_name, customer_list)
            if customer_id:
                for customer in customer_list:
                    if customer['id'] == customer_id:
                        customer_name = customer['name']
                        break
    
    # If still no match, try extracting name before "ಗೆ" or "ಕ್ಕೆ" at start of sentence or before amounts
    # This handles cases like "ಸೀತೆಗೆ 500 ರೂಪಾಯಿ" (Seetha-ge 500 rupees)
    if customer_id is None:
        # Pattern: name ending with ಗೆ/ಕ್ಕೆ at start or before numbers/amounts
        patterns = [
            r'^([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+',  # Name at start: "ಸೀತೆಗೆ 500..."
            r'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+\d+',  # Name before number: "...ಸೀತೆಗೆ 500"
            r'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+[^\s]*ರೂಪಾಯಿ',  # Name before "ರೂಪಾಯಿ"
            r'([^\s,]+?)(?:ಗೆ|ಕ್ಕೆ|ನಿಗೆ)\s+[^\s]*ರೂ',  # Name before "ರೂ"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, transcript)
            if match:
                potential_name = match.group(1).strip()
                
                # Skip if it's a number or amount keyword
                if potential_name.isdigit() or potential_name in ['ರೂಪಾಯಿ', 'ರೂ', '₹']:
                    continue
                
                # Try fuzzy matching
                customer_id = fuzzy_match_customer(potential_name, customer_list)
                if customer_id:
                    for customer in customer_list:
                        if customer['id'] == customer_id:
                            customer_name = customer['name']
                            break
                    break
                
                # If fuzzy match fails but we have a name, use it directly (for new customers)
                # This allows the name to be displayed even if not in customer list
                if potential_name and len(potential_name) > 1:
                    # Check if it looks like a name (not a number, not too short)
                    if not potential_name.isdigit() and len(potential_name) >= 2:
                        customer_name = potential_name
                        # #region agent log
                        try:
                            with open(log_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({'location':'voice_parser.py:560','message':'Using extracted name as fallback','data':{'customer_name':customer_name},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H2'})+'\n')
                        except: pass
                        # #endregion
                        break
    
    # Fallback: Extract first word as customer name if nothing found
    if customer_name is None:
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'location':'voice_parser.py:601','message':'Entering first word fallback','data':{'transcript':transcript},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H1'})+'\n')
        except: pass
        # #endregion
        # Extract first meaningful word (skip numbers, skip common words)
        words = transcript.split()
        skip_words = ['ರೂಪಾಯಿ', 'ರೂ', '₹', 'ಉದಾರ', 'ಕರ್ಜ', 'ಸಾಲ', 'ಗ್ರಾಹಕ', 'ಖರ್ಚ', 'ಮಾರಾಟ', 'ಖರೀದಿ']
        for word in words:
            # Skip if it's a number, amount keyword, or transaction keyword
            if word.isdigit() or word in skip_words:
                continue
            # Skip if it ends with postposition (extract base)
            base_word = word
            for postpos in kannada_postpositions:
                if word.endswith(postpos):
                    base_word = word[:-len(postpos)]
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({'location':'voice_parser.py:615','message':'Stripping postposition in fallback','data':{'word':word,'base_word':base_word,'postpos':postpos},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H3'})+'\n')
                    except: pass
                    # #endregion
                    break
            if base_word and len(base_word) >= 2:
                customer_name = base_word
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({'location':'voice_parser.py:622','message':'Using first word fallback','data':{'customer_name':customer_name,'word':word,'base_word':base_word},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H1'})+'\n')
                except: pass
                # #endregion
                break
    
    # Step 3: Extract product (for sale transactions)
    product = None
    if tx_type == 'sale':
        for kannada_name, english_name in KANNADA_PRODUCT_NAMES.items():
            if kannada_name in transcript:
                product = english_name
                break
    
    # Step 4: Extract quantity and unit (for sale transactions)
    quantity = None
    unit = None
    if tx_type == 'sale':
        # Pattern: "2 ಕಿಲೋ", "1.5 ಲೀಟರ್"
        qty_patterns = [
            r'(\d+\.?\d*)\s*(ಕಿಲೋ|ಕಿಲೋಗ್ರಾಂ|ಗ್ರಾಂ|ಲೀಟರ್|ಪ್ಯಾಕ್|ತುಂಡು)',
        ]
        
        for pattern in qty_patterns:
            match = re.search(pattern, transcript)
            if match:
                try:
                    quantity = float(match.group(1))
                    unit_str = match.group(2)
                    unit = KANNADA_QUANTITY_UNITS.get(unit_str, unit_str)
                    break
                except (ValueError, IndexError):
                    continue
    
    # Step 5: Extract amount
    amount = None
    
    # Pattern: "500 ರೂಪಾಯಿ", "₹500", "500 ರೂ"
    amount_patterns = [
        r'₹\s*(\d+)',
        r'(\d+)\s*(?:ರೂಪಾಯಿ|ರೂ|₹)',
        r'(?:ರೂಪಾಯಿ|ರೂ|₹)\s*(\d+)',
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, transcript)
        if match:
            try:
                amount_value = float(match.group(1))
                amount = amount_value  # In rupees
                break
            except (ValueError, IndexError):
                continue
    
    # If no amount found, look for standalone numbers
    # BUT exclude numbers that are part of quantity patterns
    if amount is None:
        # Find all numbers in the transcript
        all_numbers = re.findall(r'\d+(?:\.\d+)?', transcript)
        
        if all_numbers:
            # Convert to floats for comparison
            number_values = [float(n) for n in all_numbers]
            
            # If we found a quantity, exclude that number from amount consideration
            if quantity is not None:
                # Remove the quantity value from consideration
                number_values = [n for n in number_values if abs(n - quantity) > 0.01]
            
            # Also exclude numbers that are immediately followed by quantity units
            # (they're definitely quantities, not amounts)
            excluded_numbers = set()
            for unit in KANNADA_QUANTITY_UNITS.keys():
                pattern = rf'(\d+(?:\.\d+)?)\s*{re.escape(unit)}'
                for match in re.finditer(pattern, transcript):
                    try:
                        excluded_numbers.add(float(match.group(1)))
                    except (ValueError, IndexError):
                        pass
            
            # Remove excluded numbers
            number_values = [n for n in number_values if n not in excluded_numbers]
            
            # Only use remaining numbers as potential amounts
            if number_values:
                try:
                    # Use the largest remaining number as amount
                    amount = max(number_values)
                except (ValueError, TypeError):
                    pass
    
    # Step 6: Calculate price per unit (for sale transactions)
    price_per_unit = None
    if tx_type == 'sale' and product and quantity and lookup_product_price:
        try:
            price_per_unit = lookup_product_price(product)
        except Exception as e:
            logger.warning(f"Error looking up product price: {e}")
    
    # Assemble result
    # Ensure customer_name is set even if customer_id is None (for new customers)
    # This allows the UI to display the extracted name even if not in customer list
    result = {
        'type': tx_type,
        'amount': amount,
        'customer_id': customer_id,
        'customer_name': customer_name,  # Will be set even if customer_id is None
        'product': product,
        'quantity': quantity,
        'unit': unit,
        'price_per_unit': price_per_unit,
        'confirmation_text': f"Transaction: {tx_type} of {amount or 'N/A'} rupees" if amount else "Transaction recorded"
    }
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({'location':'voice_parser.py:662','message':'Parser result assembled','data':{'customer_id':customer_id,'customer_name':customer_name,'type':tx_type,'amount':amount},'timestamp':int(time.time()*1000),'sessionId':'debug-session','runId':'run1','hypothesisId':'H4'})+'\n')
    except: pass
    # #endregion
    
    return result


# ============================================================================
# UNIFIED PARSER
# ============================================================================

def parse_transcript(
    transcript: str,
    language: str,
    shopkeeper_id: str = None,
    customer_list: List[Dict[str, Any]] = None,
    product_map: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Unified parser that routes to appropriate language-specific parser.
    
    Args:
        transcript: Voice transcript text
        language: Language code ('hi-IN', 'en-IN', 'kn-IN')
        shopkeeper_id: Shopkeeper ID for product price lookup
        customer_list: Optional customer list (if None, will fetch from database)
        product_map: Optional product mapping (for Hindi parser)
    
    Returns:
        Complete transaction object with all fields:
        {
            'type': str,              # 'credit' or 'sale'
            'amount': float,          # Amount in rupees
            'customer_id': str,      # Customer ID (if found)
            'customer_name': str,     # Customer name (if found)
            'product': str,           # Product name (for sales)
            'quantity': float,        # Quantity (for sales)
            'unit': str,              # Unit (for sales)
            'price_per_unit': float,  # Price per unit (for sales)
            'confirmation_text': str  # Confirmation message
        }
    """
    # Get customer list if not provided
    if customer_list is None:
        customer_list = get_customer_list()
    
    # Create product price lookup function
    lookup_price_fn = None
    if shopkeeper_id:
        lookup_price_fn = create_product_price_lookup(shopkeeper_id)
    
    # Route to appropriate parser
    if language == 'hi-IN':
        if not HINDI_PARSER_AVAILABLE:
            logger.warning("Hindi parser not available, using fallback")
            return parse_english_transaction(transcript, customer_list, product_map, lookup_price_fn)
        
        # Use Hindi parser
        if product_map is None:
            product_map = HINDI_PRODUCT_MAPPING
        
        return parse_hindi_transaction(
            transcript=transcript,
            customer_list=customer_list,
            product_map=product_map,
            lookup_product_price=lookup_price_fn
        )
    
    elif language == 'en-IN':
        return parse_english_transaction(
            transcript=transcript,
            customer_list=customer_list,
            product_map=product_map,
            lookup_product_price=lookup_price_fn
        )
    
    elif language == 'kn-IN':
        return parse_kannada_transaction(
            transcript=transcript,
            customer_list=customer_list,
            product_map=product_map,
            lookup_product_price=lookup_price_fn
        )
    
    else:
        logger.warning(f"Unsupported language: {language}, defaulting to English parser")
        return parse_english_transaction(
            transcript=transcript,
            customer_list=customer_list,
            product_map=product_map,
            lookup_product_price=lookup_price_fn
        )