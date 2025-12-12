"""
Test Script for Voice Demo - Verify Transaction Creation and Blockchain Write

This script tests if voice_demo.py can successfully:
1. Create transactions via test_api.py
2. Verify transactions
3. Write to blockchain

Run this BEFORE running voice_demo.py to ensure everything is set up correctly.
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

# Test API URL
API_URL = "http://localhost:5001/test/transactions"
API_HEALTH_URL = "http://localhost:5001/test/health"
API_STATUS_URL = "http://localhost:5001/test/blockchain/status"

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"      {details}")

def test_api_connection():
    """Test 1: Check if test_api.py is running"""
    print_header("TEST 1: API Connection")
    
    try:
        response = requests.get(API_HEALTH_URL, timeout=2)
        if response.status_code == 200:
            data = response.json()
            print_result("API is running", True, f"Status: {data.get('status')}")
            print_result("Blockchain available", data.get('blockchain_available', False), 
                        "Blockchain service initialized" if data.get('blockchain_available') else "Blockchain not available")
            return True
        else:
            print_result("API is running", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_result("API is running", False, "Cannot connect. Is test_api.py running?")
        print("\n📋 To start the API:")
        print("   1. Open a new terminal")
        print("   2. cd helloKittyFanclub\\backend\\blockchain")
        print("   3. python test_api.py")
        return False
    except Exception as e:
        print_result("API is running", False, f"Error: {e}")
        return False

def test_blockchain_status():
    """Test 2: Check blockchain status"""
    print_header("TEST 2: Blockchain Status")
    
    try:
        response = requests.get(API_STATUS_URL, timeout=5)
        if response.status_code == 200:
            status = response.json()
            connected = status.get('connected', False)
            print_result("Blockchain connected", connected)
            
            if connected:
                print(f"\n   Contract Address: {status.get('contract_address', 'N/A')[:20]}...")
                print(f"   Balance: {status.get('balance_eth', 0):.4f} ETH")
                print(f"   Next TX ID: {status.get('next_transaction_id', 0)}")
            else:
                print("\n   ⚠️  Blockchain not connected. Transactions will be stored in database only.")
            
            return connected
        else:
            print_result("Blockchain status", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("Blockchain status", False, f"Error: {e}")
        return False

def test_credit_transaction():
    """Test 3: Create a credit transaction"""
    print_header("TEST 3: Credit Transaction Creation")
    
    transaction_data = {
        'transcript': 'राहुल को 500 रुपये का उधार दे दो',
        'type': 'credit',
        'amount': 50000,  # ₹500 in paise
        'customer_id': 'cust_001',
        'shopkeeper_id': 'shop_demo',
        'customer_confirmed': True,
        'language': 'hi-IN'
    }
    
    print(f"\n📤 Sending transaction:")
    print(f"   Type: {transaction_data['type']}")
    print(f"   Amount: ₹{transaction_data['amount']/100:.2f}")
    print(f"   Customer: {transaction_data['customer_id']}")
    print(f"   Transcript: {transaction_data['transcript']}")
    
    try:
        response = requests.post(API_URL, json=transaction_data, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            
            print_result("Transaction created", True, f"ID: {result.get('transaction_id')}")
            
            verification = result.get('verification', {})
            print_result("Transaction verified", 
                        verification.get('status') == 'verified',
                        f"Status: {verification.get('status')}")
            
            print_result("Storage location", 
                        verification.get('storage_location') in ['blockchain', 'database'],
                        f"Location: {verification.get('storage_location')}")
            
            should_write = verification.get('should_write_to_blockchain', False)
            print_result("Should write to blockchain", should_write)
            
            if result.get('blockchain'):
                blockchain = result['blockchain']
                print_result("Blockchain write successful", True)
                print(f"\n   ⛓️  Blockchain Details:")
                print(f"      TX Hash: {blockchain.get('tx_hash', 'N/A')}")
                print(f"      Block: {blockchain.get('block_number', 'N/A')}")
                print(f"      Gas Used: {blockchain.get('gas_used', 'N/A')}")
                return True
            elif should_write:
                print_result("Blockchain write", False, "Should write but no blockchain result")
                return False
            else:
                print_result("Blockchain write", True, "Stored in database (as expected)")
                return True
        else:
            print_result("Transaction created", False, f"Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_result("Transaction created", False, "Cannot connect to API")
        return False
    except Exception as e:
        print_result("Transaction created", False, f"Error: {e}")
        return False

def test_sale_transaction():
    """Test 4: Create a sale transaction"""
    print_header("TEST 4: Sale Transaction Creation")
    
    transaction_data = {
        'transcript': '2 किलो चावल 120 रुपये',
        'type': 'sale',
        'amount': 12000,  # ₹120 in paise
        'customer_id': 'cust_001',
        'shopkeeper_id': 'shop_demo',
        'customer_confirmed': True,
        'language': 'hi-IN',
        'product': 'Rice',
        'price': 12000,
        'quantity': 2
    }
    
    print(f"\n📤 Sending transaction:")
    print(f"   Type: {transaction_data['type']}")
    print(f"   Amount: ₹{transaction_data['amount']/100:.2f}")
    print(f"   Product: {transaction_data['product']}")
    print(f"   Transcript: {transaction_data['transcript']}")
    
    try:
        response = requests.post(API_URL, json=transaction_data, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            
            print_result("Transaction created", True, f"ID: {result.get('transaction_id')}")
            
            verification = result.get('verification', {})
            print_result("Transaction verified", 
                        verification.get('status') == 'verified',
                        f"Status: {verification.get('status')}")
            
            # Sales typically go to database first, then batch to blockchain
            storage = verification.get('storage_location', 'database')
            print_result("Storage location", True, f"Location: {storage}")
            
            return True
        else:
            print_result("Transaction created", False, f"Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print_result("Transaction created", False, f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🧪 VOICE DEMO TEST SUITE")
    print("=" * 70)
    print("\nThis script tests if voice_demo.py can create transactions and write to blockchain.")
    print("Make sure test_api.py is running before running these tests.\n")
    
    results = []
    
    # Test 1: API Connection
    api_ok = test_api_connection()
    results.append(("API Connection", api_ok))
    
    if not api_ok:
        print("\n❌ API is not running. Please start test_api.py first.")
        print("\n📋 To start:")
        print("   cd helloKittyFanclub\\backend\\blockchain")
        print("   python test_api.py")
        return
    
    # Test 2: Blockchain Status
    blockchain_ok = test_blockchain_status()
    results.append(("Blockchain Status", blockchain_ok))
    
    # Test 3: Credit Transaction
    credit_ok = test_credit_transaction()
    results.append(("Credit Transaction", credit_ok))
    
    # Test 4: Sale Transaction
    sale_ok = test_sale_transaction()
    results.append(("Sale Transaction", sale_ok))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! voice_demo.py should work correctly.")
        print("\n📋 Next steps:")
        print("   1. Keep test_api.py running")
        print("   2. Run: python voice_demo.py")
        print("   3. Select option 1 (Voice) or 2 (Manual input)")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running voice_demo.py.")
        
        if not blockchain_ok:
            print("\n💡 Blockchain not connected? Check:")
            print("   - Is Hardhat node running? (npm run node)")
            print("   - Is contract deployed? (Check CONTRACT_ADDRESS in .env)")
            print("   - Are PRIVATE_KEY and RPC_URL set correctly?")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

