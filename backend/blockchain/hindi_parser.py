"""
Hindi Voice Transaction Parser

A clean, rule-based parser for Hindi voice transactions following the grammar:
"ग्राहक <नाम>, <लेनदेन_प्रकार> <मात्रा> <प्रोडक्ट> <कीमत>"
"""

import re
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass

# Try to import fuzzy matching library
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
# HINDI KEYWORD MAPPINGS (Centralized)
# ============================================================================

# Transaction type keywords
# CREDIT: Money owed / goods taken on credit (udhaar lena)
CREDIT_KEYWORDS = ['उधार', 'उधारी', 'कर्ज', 'कर्जा', 'उधार दे', 'कर्ज दे', 'उधार लिया', 'उधार ले', 'कर्ज लिया']
# SALE: Stock going out to customers
SALE_KEYWORDS = ['बिक्री', 'बेचो', 'दो', 'दीजिए', 'बेच', 'बेचना', 'बिकवा']
# BUYING: Stock coming in (inventory purchase from supplier/vendor)
BUYING_KEYWORDS = ['खरीद', 'खरीदा', 'खरीदी', 'लिया', 'ली', 'मंगाया', 'मंगाई', 'ऑर्डर', 'स्टॉक']

# Amount keywords
AMOUNT_KEYWORDS = ['रुपये', 'रुपए', 'रु', '₹', 'का दाम', 'की कीमत', 'दाम', 'कीमत', 'मूल्य']

# Quantity units (Hindi → English)
QUANTITY_UNITS = {
    'किलो': 'kg',
    'किलोग्राम': 'kg',
    'ग्राम': 'gram',
    'लीटर': 'liter',
    'लिटर': 'liter',
    'पैक': 'pack',
    'पैकेट': 'pack',
    'पीस': 'piece',
    'नग': 'piece',
    'टुकड़ा': 'piece',
}

# Product name mapping (Hindi → English)
PRODUCT_MAPPING = {
    # Vegetables
    'टमाटर': 'Tomatoes',
    'टोमैटो': 'Tomatoes',
    'आलू': 'Potatoes',
    'पोटैटो': 'Potatoes',
    'प्याज': 'Onions',
    'प्याज़': 'Onions',
    'बैंगन': 'Brinjal',
    'भिंडी': 'Okra',
    'गोभी': 'Cabbage',
    'फूलगोभी': 'Cauliflower',
    
    # Grains & Staples
    'चावल': 'Rice',
    'राइस': 'Rice',
    'गेहूं': 'Wheat Flour',
    'गेहूँ': 'Wheat Flour',
    'आटा': 'Wheat Flour',
    'दाल': 'Lentils',
    'चना': 'Chickpeas',
    'मूंग': 'Mung Beans',
    
    # Essentials
    'चीनी': 'Sugar',
    'शुगर': 'Sugar',
    'नमक': 'Salt',
    'साल्ट': 'Salt',
    'तेल': 'Cooking Oil',
    'ऑयल': 'Cooking Oil',
    'मसाला': 'Spices',
    'हल्दी': 'Turmeric',
    'धनिया': 'Coriander',
    
    # Beverages
    'चाय': 'Tea',
    'टी': 'Tea',
    'कॉफी': 'Coffee',
    'कोफी': 'Coffee',
    
    # Dairy
    'दूध': 'Milk',
    'मिल्क': 'Milk',
    'दही': 'Curd',
    'पनीर': 'Paneer',
    'अंडे': 'Eggs',
    'एग': 'Eggs',
    
    # Bakery
    'ब्रेड': 'Bread',
    'रोटी': 'Bread',
    'बिस्कुट': 'Biscuits',
    
    # Personal Care
    'साबुन': 'Soap',
    'सोप': 'Soap',
    'शैंपू': 'Shampoo',
    'शैम्पू': 'Shampoo',
    'टूथपेस्ट': 'Toothpaste',
    'दंतमंजन': 'Toothpaste',
    
    # Additional common items
    'मिर्च': 'Chili',
    'अदरक': 'Ginger',
    'लहसुन': 'Garlic',
    'टमाटर': 'Tomatoes',  # Duplicate but common variant
    'बीन्स': 'Beans',
    'मटर': 'Peas',
    'गाजर': 'Carrot',
    'मूली': 'Radish',
    'पालक': 'Spinach',
    'मेथी': 'Fenugreek',
    'धनिया': 'Coriander Leaves',
    'पुदीना': 'Mint',
}


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

def convert_number_word_to_digit(text: str) -> Optional[float]:
    """
    Convert Hindi or English number words to numeric value.
    Supports simple cases like "do kilo" (2 kg), "two packets" (2 packets).
    
    Args:
        text: Text containing number word
    
    Returns:
        Numeric value (float) or None if not found
    """
    text_lower = text.lower().strip()
    
    # Try Hindi number words first
    for word, value in HINDI_NUMBER_WORDS.items():
        if word in text_lower:
            return float(value)
    
    # Try English number words
    for word, value in ENGLISH_NUMBER_WORDS.items():
        if word in text_lower:
            return float(value)
    
    return None

def fuzzy_match_name(name: str, candidates: List[str], threshold: float = 0.6) -> Optional[str]:
    """
    Fuzzy match a name against a list of candidates.
    
    Args:
        name: Name to match
        candidates: List of candidate names
        threshold: Minimum similarity score (0-1)
    
    Returns:
        Best matching candidate or None
    """
    if not candidates or not name:
        return None
    
    if not FUZZY_AVAILABLE:
        # Fallback to simple substring matching
        name_lower = name.lower()
        for candidate in candidates:
            if name_lower in candidate.lower() or candidate.lower() in name_lower:
                return candidate
        return None
    
    try:
        # Use rapidfuzz if available
        from rapidfuzz import fuzz, process
        result = process.extractOne(name, candidates, scorer=fuzz.ratio)
        if result and result[1] >= threshold * 100:  # rapidfuzz returns 0-100
            return result[0]
    except:
        # Fallback to difflib
        try:
            from difflib import SequenceMatcher
            best_match = None
            best_score = 0
            
            for candidate in candidates:
                score = SequenceMatcher(None, name.lower(), candidate.lower()).ratio()
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = candidate
            
            return best_match
        except:
            pass
    
    return None


def extract_number_near_keyword(text: str, keywords: List[str], context_chars: int = 20) -> Optional[float]:
    """
    Extract a number that appears near any of the given keywords.
    
    Args:
        text: Input text
        keywords: List of keywords to search for
        context_chars: Number of characters before/after keyword to search
    
    Returns:
        First number found near keyword, or None
    """
    text_lower = text.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            # Find position of keyword
            idx = text_lower.find(keyword_lower)
            
            # Search before and after keyword
            start = max(0, idx - context_chars)
            end = min(len(text), idx + len(keyword) + context_chars)
            context = text[start:end]
            
            # Find all numbers in context
            numbers = re.findall(r'\d+(?:\.\d+)?', context)
            if numbers:
                try:
                    return float(numbers[0])
                except ValueError:
                    continue
    
    return None


# ============================================================================
# MAIN PARSER FUNCTIONS
# ============================================================================

def parse_hindi_intent(transcript: str) -> Dict[str, str]:
    """
    Parse transaction type from Hindi transcript.
    
    Args:
        transcript: Hindi transcript text
    
    Returns:
        {'type': 'sale' | 'credit', 'is_buying': bool}
    """
    transcript_lower = transcript.lower()
    is_buying = False
    
    # Priority: BUYING > CREDIT > SALE (more specific first)
    # Check for buying keywords first (stock coming in)
    for keyword in BUYING_KEYWORDS:
        if keyword in transcript_lower:
            return {'type': 'sale', 'is_buying': True}  # Map to 'sale' type (database constraint)
    
    # Check for credit keywords (udhaar lena)
    for keyword in CREDIT_KEYWORDS:
        if keyword in transcript_lower:
            return {'type': 'credit', 'is_buying': False}
    
    # Check for sale keywords (stock going out)
    for keyword in SALE_KEYWORDS:
        if keyword in transcript_lower:
            return {'type': 'sale', 'is_buying': False}
    
    # Default to credit if no keywords found (safer for shopkeepers)
    return {'type': 'credit', 'is_buying': False}


def extract_customer_name(transcript: str, customer_list: List[Dict[str, Any]]) -> Optional[str]:
    """
    Extract customer name from transcript using fuzzy matching.
    
    Args:
        transcript: Hindi transcript
        customer_list: List of customer dicts with 'id' and 'name' keys
    
    Returns:
        Customer ID (str) or None
    """
    # Pattern: "ग्राहक <name>" or just "<name>" at start
    patterns = [
        r'ग्राहक\s+([^\s,]+)',
        r'^([^\s,]+)\s*,',  # Name at start before comma
    ]
    
    extracted_name = None
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            extracted_name = match.group(1).strip()
            break
    
    if not extracted_name:
        return None
    
    # Get all customer names
    customer_names = [c['name'] for c in customer_list if 'name' in c]
    
    # Fuzzy match
    matched_name = fuzzy_match_name(extracted_name, customer_names, threshold=0.5)
    
    if matched_name:
        # Find customer ID
        for customer in customer_list:
            if customer.get('name') == matched_name:
                return customer.get('id')
    
    return None


def extract_product(transcript: str, product_map: Dict[str, str] = None) -> Optional[str]:
    """
    Extract product name from transcript using fuzzy matching.
    
    Args:
        transcript: Hindi transcript
        product_map: Dictionary mapping Hindi product names to English (default: PRODUCT_MAPPING)
    
    Returns:
        English product name or None
    """
    if product_map is None:
        product_map = PRODUCT_MAPPING
    
    transcript_lower = transcript.lower()
    
    # Direct mapping first
    for hindi_name, english_name in product_map.items():
        if hindi_name in transcript or hindi_name.lower() in transcript_lower:
            return english_name
    
    # Fuzzy match if direct match fails
    hindi_products = list(product_map.keys())
    matched_hindi = fuzzy_match_name(transcript, hindi_products, threshold=0.4)
    
    if matched_hindi:
        return product_map.get(matched_hindi)
    
    return None


def extract_quantity_and_unit(transcript: str) -> Dict[str, Any]:
    """
    Extract quantity and unit from transcript.
    Supports both numeric digits and number words (Hindi/English).
    
    Args:
        transcript: Hindi/English transcript
    
    Returns:
        {'quantity': float, 'unit': str} or {'quantity': None, 'unit': None}
    """
    # First, try numeric patterns: "<number> <unit>"
    for hindi_unit, english_unit in QUANTITY_UNITS.items():
        # Pattern: numeric digit before unit
        pattern1 = rf'(\d+(?:\.\d+)?)\s*{re.escape(hindi_unit)}'
        match1 = re.search(pattern1, transcript, re.IGNORECASE)
        if match1:
            try:
                quantity = float(match1.group(1))
                return {'quantity': quantity, 'unit': english_unit}
            except ValueError:
                continue
        
        # Pattern: unit after number (with space variations)
        pattern2 = rf'(\d+(?:\.\d+)?)\s+{re.escape(hindi_unit)}'
        match2 = re.search(pattern2, transcript, re.IGNORECASE)
        if match2:
            try:
                quantity = float(match2.group(1))
                return {'quantity': quantity, 'unit': english_unit}
            except ValueError:
                continue
    
    # Second, try number words: "<number_word> <unit>"
    # Check for Hindi number words
    for hindi_unit, english_unit in QUANTITY_UNITS.items():
        for hindi_number, numeric_value in HINDI_NUMBER_WORDS.items():
            # Pattern: Hindi number word before unit
            pattern = rf'{re.escape(hindi_number)}\s+{re.escape(hindi_unit)}'
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                return {'quantity': float(numeric_value), 'unit': english_unit}
    
    # Check for English number words
    for hindi_unit, english_unit in QUANTITY_UNITS.items():
        for english_number, numeric_value in ENGLISH_NUMBER_WORDS.items():
            # Pattern: English number word before unit (works with English unit names too)
            # Also try with Hindi units (mixed language)
            patterns = [
                rf'{re.escape(english_number)}\s+{re.escape(hindi_unit)}',
                rf'{re.escape(english_number)}\s+{re.escape(english_unit)}',
            ]
            for pattern in patterns:
                match = re.search(pattern, transcript, re.IGNORECASE)
                if match:
                    return {'quantity': float(numeric_value), 'unit': english_unit}
    
    # If no unit found, look for standalone numbers (assume kg for common items)
    numbers = re.findall(r'\d+(?:\.\d+)?', transcript)
    if numbers:
        # For sale transactions, first number might be quantity
        # For credit, it's usually amount
        try:
            quantity = float(numbers[0])
            # Default to kg if no unit specified
            return {'quantity': quantity, 'unit': 'kg'}
        except ValueError:
            pass
    
    return {'quantity': None, 'unit': None}


def extract_amount(transcript: str, tx_type: str) -> Optional[float]:
    """
    Extract amount from transcript.
    
    For credit: largest number near रुपये = amount
    For sale: number near रुपये = price
    
    Args:
        transcript: Hindi transcript
        tx_type: 'credit' or 'sale'
    
    Returns:
        Amount in rupees (float) or None
        NOTE: Backend expects rupees and will convert to paise
    """
    # Find number near amount keywords
    amount_rupees = extract_number_near_keyword(transcript, AMOUNT_KEYWORDS)
    
    if amount_rupees:
        return float(amount_rupees)  # Return in rupees
    
    # If no amount keyword found, use heuristics
    all_numbers = re.findall(r'\d+(?:\.\d+)?', transcript)
    if not all_numbers:
        return None
    
    numbers = [float(n) for n in all_numbers]
    
    if tx_type == 'credit':
        # For credit, largest number is likely the amount
        amount_rupees = max(numbers)
    else:
        # For sale, look for number that's not quantity
        # If we have quantity, amount should be different number
        quantity_data = extract_quantity_and_unit(transcript)
        if quantity_data['quantity']:
            # Amount is the other number (exclude quantity)
            other_numbers = [n for n in numbers if abs(n - quantity_data['quantity']) > 0.1]
            if other_numbers:
                amount_rupees = max(other_numbers)
            else:
                # No amount found - don't use quantity as amount
                return None
        else:
            amount_rupees = max(numbers)
    
    return float(amount_rupees)  # Return in rupees


def assemble_transaction_object(
    customer_id: Optional[str],
    tx_type: str,
    product: Optional[str],
    quantity: Optional[float],
    unit: Optional[str],
    amount: Optional[float],
    price_per_unit: Optional[float] = None,
    customer_name: Optional[str] = None,
    is_buying: bool = False
) -> Dict[str, Any]:
    """
    Assemble final transaction object and generate Hindi confirmation text.
    
    Args:
        customer_id: Customer ID
        tx_type: 'sale' or 'credit'
        product: Product name (English)
        quantity: Quantity
        unit: Unit (kg, gram, etc.)
        amount: Amount in paise
        price_per_unit: Price per unit in rupees
        customer_name: Customer name (for confirmation text)
    
    Returns:
        Complete transaction object with confirmation text
    """
    # Build Hindi confirmation text
    confirmation_parts = []
    
    if customer_name:
        confirmation_parts.append(f"ग्राहक {customer_name}")
    elif customer_id:
        confirmation_parts.append(f"ग्राहक {customer_id}")
    else:
        confirmation_parts.append("ग्राहक")
    
    if tx_type == 'credit':
        confirmation_parts.append("उधार")
        if amount:
            confirmation_parts.append(f"{amount:.0f} रुपये")
    else:  # sale
        confirmation_parts.append("बिक्री")
        if quantity and unit:
            unit_hindi = {v: k for k, v in QUANTITY_UNITS.items()}.get(unit, unit)
            confirmation_parts.append(f"{quantity:.0f} {unit_hindi}")
        if product:
            # Find Hindi name for product
            product_hindi = None
            for hindi, english in PRODUCT_MAPPING.items():
                if english == product:
                    product_hindi = hindi
                    break
            if product_hindi:
                confirmation_parts.append(product_hindi)
        if amount:
            confirmation_parts.append(f"{amount:.0f} रुपये")
    
    confirmation_text = "आपने कहा: " + ", ".join(confirmation_parts) + "। पुष्टि करें?"
    
    result = {
        'customer_id': customer_id,
        'type': tx_type,
        'product': product,
        'quantity': quantity,
        'unit': unit,
        'amount': amount,
        'price_per_unit': price_per_unit,
        'customer_name': customer_name,
        'confirmation_text_hindi': confirmation_text
    }
    
    # Add metadata for buying transactions (mapped to 'sale' type)
    if is_buying:
        result['is_buying'] = True  # Flag to indicate this is a buying/inventory transaction
        result['transaction_subtype'] = 'buying'  # Store original intent
    
    return result


# ============================================================================
# MAIN PARSER FUNCTION
# ============================================================================

def parse_hindi_transaction(
    transcript: str,
    customer_list: List[Dict[str, Any]],
    product_map: Dict[str, str] = None,
    lookup_product_price: callable = None
) -> Dict[str, Any]:
    """
    Main parser function for Hindi voice transactions.
    
    Args:
        transcript: Hindi transcript text
        customer_list: List of customer dicts with 'id' and 'name'
        product_map: Dictionary mapping Hindi to English product names
        lookup_product_price: Function to lookup product price (product_name, shopkeeper_id) -> float
    
    Returns:
        Complete transaction object with all fields
    """
    # Step 1: Parse intent (transaction type)
    intent = parse_hindi_intent(transcript)
    tx_type = intent['type']
    is_buying = intent.get('is_buying', False)  # Flag for buying transactions
    
    # Step 2: Extract customer name
    customer_id = extract_customer_name(transcript, customer_list)
    customer_name = None
    if customer_id:
        # Get customer name for confirmation text
        for customer in customer_list:
            if customer.get('id') == customer_id:
                customer_name = customer.get('name')
                break
    
    # Fallback: Extract name even if fuzzy match failed (for new customers)
    if customer_name is None:
        # Pattern: "ग्राहक <name>" or just "<name>" at start
        patterns = [
            r'ग्राहक\s+([^\s,]+)',
            r'^([^\s,]+)\s*,',  # Name at start before comma
        ]
        
        extracted_name = None
        for pattern in patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                extracted_name = match.group(1).strip()
                # Skip if it's a number or common word
                if extracted_name.isdigit() or extracted_name in ['रुपये', 'रुपया', '₹', '₹']:
                    continue
                if extracted_name and len(extracted_name) > 1:
                    customer_name = extracted_name
                    break
    
    # Step 3: Extract product (for sale transactions)
    product = None
    if tx_type == 'sale':
        product = extract_product(transcript, product_map)
    
    # Step 4: Extract quantity and unit (for sale transactions)
    quantity = None
    unit = None
    if tx_type == 'sale':
        qty_data = extract_quantity_and_unit(transcript)
        quantity = qty_data['quantity']
        unit = qty_data['unit']
    
    # Step 5: Extract amount
    amount = extract_amount(transcript, tx_type)
    
    # Step 6: Calculate price per unit (for sale transactions)
    price_per_unit = None
    if tx_type == 'sale' and product and quantity and lookup_product_price:
        # Try to get price from database
        try:
            price_per_unit = lookup_product_price(product)
            if price_per_unit and amount is None:
                # Calculate amount from price × quantity (in rupees)
                amount = float(price_per_unit * quantity)
        except:
            pass
    
    # If amount still not found and we have price_per_unit, calculate it
    if amount is None and price_per_unit and quantity:
        amount = float(price_per_unit * quantity)
    
    # Step 7: Assemble transaction object
    return assemble_transaction_object(
        customer_id=customer_id,
        tx_type=tx_type,
        product=product,
        quantity=quantity,
        unit=unit,
        amount=amount,
        price_per_unit=price_per_unit,
        customer_name=customer_name,
        is_buying=is_buying
    )

