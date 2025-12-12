"""
Mock Data Generator for Kirana Store Management System

Generates realistic test data for:
- Shopkeeper history
- Transaction data
- Customer data
- Product catalogs

Used for testing verification services without real database.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


# Sample product catalog (prices in paise)
SAMPLE_PRODUCTS = {
    'चावल (1kg)': 6000,      # Rice
    'आटा (1kg)': 4000,       # Flour
    'दाल (1kg)': 12000,      # Lentils
    'तेल (1L)': 15000,       # Oil
    'चीनी (1kg)': 4500,      # Sugar
    'नमक (1kg)': 2000,       # Salt
    'मैगी': 1400,            # Maggie
    'बिस्कुट': 2000,         # Biscuits
    'साबुन': 3500,           # Soap
    'शैम्पू': 12000,         # Shampoo
    'चाय पत्ती': 5000,       # Tea leaves
    'दूध (500ml)': 2500,     # Milk
    'ब्रेड': 4000,           # Bread
    'अंडे (6)': 4200,        # Eggs
    'प्याज (1kg)': 3000,     # Onion
    'आलू (1kg)': 2500,       # Potato
    'टमाटर (1kg)': 4000,     # Tomato
}

SAMPLE_PRODUCTS_ENGLISH = {
    'Rice (1kg)': 6000,
    'Flour (1kg)': 4000,
    'Lentils (1kg)': 12000,
    'Oil (1L)': 15000,
    'Sugar (1kg)': 4500,
    'Salt (1kg)': 2000,
    'Maggie': 1400,
    'Biscuits': 2000,
    'Soap': 3500,
    'Shampoo': 12000,
    'Tea leaves': 5000,
    'Milk (500ml)': 2500,
    'Bread': 4000,
    'Eggs (6)': 4200,
    'Onion (1kg)': 3000,
    'Potato (1kg)': 2500,
    'Tomato (1kg)': 4000,
}

# Sample customer names
SAMPLE_CUSTOMERS = [
    {'id': 'cust_001', 'name': 'राहुल शर्मा', 'phone': '+919876543210'},
    {'id': 'cust_002', 'name': 'प्रिया पटेल', 'phone': '+919876543211'},
    {'id': 'cust_003', 'name': 'अमित कुमार', 'phone': '+919876543212'},
    {'id': 'cust_004', 'name': 'सुनीता देवी', 'phone': '+919876543213'},
    {'id': 'cust_005', 'name': 'विकास यादव', 'phone': '+919876543214'},
    {'id': 'cust_006', 'name': 'Rahul Sharma', 'phone': '+919876543215'},
    {'id': 'cust_007', 'name': 'Priya Patel', 'phone': '+919876543216'},
    {'id': 'cust_008', 'name': 'Amit Kumar', 'phone': '+919876543217'},
]

# Sample shopkeeper data
SAMPLE_SHOPKEEPERS = [
    {'id': 'shop_001', 'name': 'राजू किराना स्टोर', 'address': 'MG Road, Delhi'},
    {'id': 'shop_002', 'name': 'शर्मा जनरल स्टोर', 'address': 'Sector 15, Noida'},
    {'id': 'shop_003', 'name': 'Raju Kirana Store', 'address': 'MG Road, Delhi'},
]

# Sample transcripts
SAMPLE_TRANSCRIPTS = {
    'credit_hindi': [
        "राहुल को 500 रुपये का उधार दे दो",
        "प्रिया को 200 रुपये का क्रेडिट",
        "अमित को 1000 रुपये उधार",
        "सुनीता को पांच सौ का उधार",
        "विकास को तीन सौ रुपये क्रेडिट दे दो",
    ],
    'credit_english': [
        "Give 500 rupees credit to Rahul",
        "Credit 200 rupees to Priya",
        "Give Amit 1000 rupees udhar",
        "500 rupees credit for Sunita",
        "Credit 300 to Vikas",
    ],
    'sale_hindi': [
        "2 किलो चावल 120 रुपये",
        "1 लीटर तेल 150 रुपये",
        "मैगी 14 रुपये",
        "1 किलो आटा 40 रुपये",
        "साबुन और शैम्पू 155 रुपये",
    ],
    'sale_english': [
        "2 kg rice 120 rupees",
        "1 liter oil 150 rupees",
        "Maggie 14 rupees",
        "1 kg flour 40 rupees",
        "Soap and shampoo 155 rupees",
    ],
    'repay_hindi': [
        "राहुल ने 300 रुपये चुकाए",
        "प्रिया का 200 रुपये आया",
        "अमित ने पूरा उधार चुका दिया",
    ],
    'repay_english': [
        "Rahul paid 300 rupees",
        "Priya paid back 200 rupees",
        "Amit cleared his credit",
    ],
}


def generate_shopkeeper_history(
    average_daily_sales: int = 500000,  # ₹5,000 in paise
    total_transactions: int = 150,
    num_customers: int = 5
) -> Dict[str, Any]:
    """
    Generate mock shopkeeper history for testing.
    
    Args:
        average_daily_sales: Average daily sales in paise
        total_transactions: Total number of transactions
        num_customers: Number of customers with credit history
    
    Returns:
        Dict with shopkeeper history data
    """
    # Generate customer credits today (0-3 per customer)
    customer_credits_today = {}
    for customer in SAMPLE_CUSTOMERS[:num_customers]:
        customer_credits_today[customer['id']] = random.randint(0, 3)
    
    # Generate purchase history (some customers have history, some don't)
    customer_purchase_history = {}
    for i, customer in enumerate(SAMPLE_CUSTOMERS[:num_customers]):
        if random.random() > 0.3:  # 70% have purchase history
            num_purchases = random.randint(3, 20)
            customer_purchase_history[customer['id']] = [
                {
                    'date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    'amount': random.randint(5000, 50000)  # ₹50 to ₹500
                }
                for _ in range(num_purchases)
            ]
        else:
            customer_purchase_history[customer['id']] = []  # No history (credit-only)
    
    return {
        'average_daily_sales': average_daily_sales,
        'total_transactions': total_transactions,
        'customer_credits_today': customer_credits_today,
        'customer_purchase_history': customer_purchase_history,
        'product_catalog': {**SAMPLE_PRODUCTS, **SAMPLE_PRODUCTS_ENGLISH},
        'sales_today': random.randint(0, average_daily_sales),
        'last_updated': datetime.now().isoformat()
    }


def generate_transaction_data(
    transcript: str,
    tx_type: str = 'credit',
    amount: Optional[int] = None,
    customer_id: Optional[str] = None,
    shopkeeper_id: str = 'shop_001',
    customer_confirmed: bool = False,
    language: str = 'hi-IN'
) -> Dict[str, Any]:
    """
    Generate mock transaction data for testing.
    
    Args:
        transcript: Text transcript from STT
        tx_type: Transaction type ('credit', 'sale', 'repay')
        amount: Amount in paise (auto-generated if None)
        customer_id: Customer ID (auto-selected if None)
        shopkeeper_id: Shopkeeper ID
        customer_confirmed: Whether customer confirmed
        language: Language code
    
    Returns:
        Dict with transaction data
    """
    # Auto-generate amount if not provided
    if amount is None:
        if tx_type == 'credit':
            amount = random.randint(10000, 100000)  # ₹100 to ₹1,000
        elif tx_type == 'sale':
            amount = random.randint(1000, 50000)    # ₹10 to ₹500
        else:  # repay
            amount = random.randint(10000, 50000)   # ₹100 to ₹500
    
    # Auto-select customer if not provided
    if customer_id is None:
        customer = random.choice(SAMPLE_CUSTOMERS)
        customer_id = customer['id']
    
    base_data = {
        'transcript': transcript,
        'type': tx_type,
        'amount': amount,
        'customer_id': customer_id,
        'shopkeeper_id': shopkeeper_id,
        'customer_confirmed': customer_confirmed,
        'language': language,
        'timestamp': datetime.now().isoformat()
    }
    
    # Add sale-specific fields
    if tx_type == 'sale':
        products = list(SAMPLE_PRODUCTS.keys()) if language == 'hi-IN' else list(SAMPLE_PRODUCTS_ENGLISH.keys())
        product = random.choice(products)
        base_data['product'] = product
        base_data['price'] = amount
        base_data['quantity'] = random.randint(1, 5)
    
    return base_data


def generate_customer_data(
    customer_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate mock customer data.
    
    Args:
        customer_id: Specific customer ID or random
    
    Returns:
        Dict with customer data
    """
    if customer_id:
        customer = next((c for c in SAMPLE_CUSTOMERS if c['id'] == customer_id), None)
        if not customer:
            customer = random.choice(SAMPLE_CUSTOMERS)
    else:
        customer = random.choice(SAMPLE_CUSTOMERS)
    
    return {
        **customer,
        'total_purchases': random.randint(10000, 500000),  # ₹100 to ₹5,000
        'total_credits': random.randint(5000, 100000),     # ₹50 to ₹1,000
        'credit_balance': random.randint(0, 50000),        # ₹0 to ₹500
        'created_at': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
    }


def generate_test_scenarios() -> List[Dict[str, Any]]:
    """
    Generate a list of test scenarios covering various cases.
    
    Returns:
        List of test scenario dictionaries
    """
    scenarios = []
    
    # Scenario 1: Normal credit (Hindi) - should pass
    scenarios.append({
        'name': 'Normal credit transaction (Hindi)',
        'data': generate_transaction_data(
            transcript=random.choice(SAMPLE_TRANSCRIPTS['credit_hindi']),
            tx_type='credit',
            amount=50000,  # ₹500
            customer_confirmed=True,
            language='hi-IN'
        ),
        'shopkeeper_history': generate_shopkeeper_history(average_daily_sales=500000),
        'expected_result': 'verified'
    })
    
    # Scenario 2: Normal credit (English) - should pass
    scenarios.append({
        'name': 'Normal credit transaction (English)',
        'data': generate_transaction_data(
            transcript=random.choice(SAMPLE_TRANSCRIPTS['credit_english']),
            tx_type='credit',
            amount=30000,  # ₹300
            customer_confirmed=True,
            language='en-IN'
        ),
        'shopkeeper_history': generate_shopkeeper_history(average_daily_sales=500000),
        'expected_result': 'verified'
    })
    
    # Scenario 3: High amount credit - flagged (HIGH risk)
    # Score 0.60 = HIGH risk → always flagged, regardless of confirmation
    scenarios.append({
        'name': 'High amount credit (flagged - HIGH risk)',
        'data': generate_transaction_data(
            transcript="राहुल को 5000 रुपये का उधार",
            tx_type='credit',
            amount=500000,  # ₹5,000 - high amount
            customer_confirmed=False,
            language='hi-IN'
        ),
        'shopkeeper_history': generate_shopkeeper_history(average_daily_sales=200000),  # Low daily sales
        'expected_result': 'flagged'  # HIGH risk (score 0.60) → always flagged
    })
    
    # Scenario 4: Credit with no purchase history - verified (LOW risk + confirmed)
    # Score 0.20 = LOW risk, customer_confirmed=True, amount < ₹2000 → verified
    history_no_purchases = generate_shopkeeper_history()
    history_no_purchases['customer_purchase_history']['cust_001'] = []
    scenarios.append({
        'name': 'Credit to customer with no purchase history (verified)',
        'data': generate_transaction_data(
            transcript="नए ग्राहक को 200 रुपये का उधार",
            tx_type='credit',
            amount=20000,  # ₹200 - below ₹2000 threshold
            customer_id='cust_001',
            customer_confirmed=True,
            language='hi-IN'
        ),
        'shopkeeper_history': history_no_purchases,
        'expected_result': 'verified'  # LOW risk + confirmed = verified
    })
    
    # Scenario 5: Normal sale (Hindi) - verified with matching catalog price
    # Product price matches catalog, so no price deviation flag
    scenarios.append({
        'name': 'Normal sale transaction (Hindi)',
        'data': {
            'transcript': "मैगी 14 रुपये",
            'type': 'sale',
            'amount': 1400,  # ₹14 - matches Maggie price in catalog
            'customer_id': 'cust_001',
            'shopkeeper_id': 'shop_001',
            'customer_confirmed': False,
            'language': 'hi-IN',
            'product': 'मैगी',  # Matches catalog key
            'price': 1400,  # Exact catalog price
            'quantity': 1
        },
        'shopkeeper_history': generate_shopkeeper_history(),
        'expected_result': 'verified'
    })
    
    # Scenario 6: Sale with price deviation
    history_with_catalog = generate_shopkeeper_history()
    scenarios.append({
        'name': 'Sale with price deviation (flagged)',
        'data': {
            **generate_transaction_data(
                transcript="2 kg rice 200 rupees",  # Higher than catalog
                tx_type='sale',
                amount=20000,  # ₹200 instead of ₹120
                language='en-IN'
            ),
            'product': 'Rice (1kg)',
            'price': 20000,  # 233% of catalog price
            'quantity': 2
        },
        'shopkeeper_history': history_with_catalog,
        'expected_result': 'flagged'
    })
    
    # Scenario 7: Repayment
    scenarios.append({
        'name': 'Repayment transaction (Hindi)',
        'data': generate_transaction_data(
            transcript=random.choice(SAMPLE_TRANSCRIPTS['repay_hindi']),
            tx_type='repay',
            amount=30000,  # ₹300
            customer_confirmed=True,
            language='hi-IN'
        ),
        'shopkeeper_history': generate_shopkeeper_history(),
        'expected_result': 'verified'
    })
    
    return scenarios


# Convenience functions for quick data generation
def get_sample_credit_data(language: str = 'hi-IN') -> Dict[str, Any]:
    """Get sample credit transaction data"""
    transcripts = SAMPLE_TRANSCRIPTS['credit_hindi'] if language == 'hi-IN' else SAMPLE_TRANSCRIPTS['credit_english']
    return generate_transaction_data(
        transcript=random.choice(transcripts),
        tx_type='credit',
        customer_confirmed=True,
        language=language
    )


def get_sample_sale_data(language: str = 'hi-IN') -> Dict[str, Any]:
    """Get sample sale transaction data"""
    transcripts = SAMPLE_TRANSCRIPTS['sale_hindi'] if language == 'hi-IN' else SAMPLE_TRANSCRIPTS['sale_english']
    return generate_transaction_data(
        transcript=random.choice(transcripts),
        tx_type='sale',
        language=language
    )


def get_sample_shopkeeper_history() -> Dict[str, Any]:
    """Get sample shopkeeper history"""
    return generate_shopkeeper_history()


if __name__ == '__main__':
    # Demo: Print sample data
    print("=" * 60)
    print("MOCK DATA GENERATOR - SAMPLE OUTPUT")
    print("=" * 60)
    
    print("\n📝 Sample Credit Data (Hindi):")
    print(get_sample_credit_data('hi-IN'))
    
    print("\n📝 Sample Sale Data (English):")
    print(get_sample_sale_data('en-IN'))
    
    print("\n📊 Sample Shopkeeper History:")
    history = get_sample_shopkeeper_history()
    print(f"  Average Daily Sales: ₹{history['average_daily_sales']/100:.2f}")
    print(f"  Total Transactions: {history['total_transactions']}")
    print(f"  Products in Catalog: {len(history['product_catalog'])}")
    
    print("\n🧪 Test Scenarios:")
    scenarios = generate_test_scenarios()
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario['name']} → Expected: {scenario['expected_result']}")

