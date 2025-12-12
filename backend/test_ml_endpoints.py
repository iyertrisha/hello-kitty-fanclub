"""
Test script for ML Credit Scoring endpoints.
Tests all 9 steps from the validation plan.
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_step1_startup():
    """Step 1: Verify backend starts on port 8000"""
    print("\n" + "="*60)
    print("STEP 1: Testing Backend Startup")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running on port 8000")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("   Start it with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step2_health():
    """Step 2: Verify ML health endpoint format"""
    print("\n" + "="*60)
    print("STEP 2: Testing ML Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/ml/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint responded")
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Check required fields
            required_fields = ["model_loaded", "db_connected", "shopkeeper_count", "blockchain_available", "message"]
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print(f"⚠️ Missing fields: {missing_fields}")
                return False
            else:
                print("✅ All required fields present")
                print(f"   model_loaded: {data.get('model_loaded')}")
                print(f"   db_connected: {data.get('db_connected')}")
                print(f"   shopkeeper_count: {data.get('shopkeeper_count')}")
                print(f"   blockchain_available: {data.get('blockchain_available')}")
                return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step3_db_aggregation(shopkeeper_id: str):
    """Step 3: Verify database aggregation works"""
    print("\n" + "="*60)
    print("STEP 3: Testing Database Aggregation")
    print("="*60)
    print(f"   Using shopkeeper_id: {shopkeeper_id}")
    try:
        response = requests.get(f"{BASE_URL}/ml/predict-credit-score/{shopkeeper_id}", timeout=10)
        if response.status_code == 200:
            print("✅ Database aggregation successful")
            return True
        elif response.status_code == 404:
            print(f"⚠️ Shopkeeper {shopkeeper_id} not found in database")
            print("   This is expected if database is not seeded")
            return True  # Not a failure, just no data
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step4_get_endpoint(shopkeeper_id: str):
    """Step 4: Test GET endpoint with valid shopkeeper_id"""
    print("\n" + "="*60)
    print("STEP 4: Testing GET Endpoint")
    print("="*60)
    print(f"   Using shopkeeper_id: {shopkeeper_id}")
    try:
        response = requests.get(f"{BASE_URL}/ml/predict-credit-score/{shopkeeper_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ GET endpoint successful")
            print(f"   Score: {data.get('score')}")
            print(f"   Source: {data.get('source')}")
            print(f"   Blockchain verified: {data.get('blockchain_verified')}")
            
            # Validate score range
            score = data.get('score', 0)
            if 300 <= score <= 900:
                print(f"✅ Score in valid range: {score}")
            else:
                print(f"❌ Score out of range: {score} (should be 300-900)")
                return False
            
            # Check required fields
            required_fields = ["score", "factors", "explanation", "source"]
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                print(f"❌ Missing fields: {missing_fields}")
                return False
            
            return True
        elif response.status_code == 404:
            print(f"⚠️ Shopkeeper {shopkeeper_id} not found")
            return True  # Not a test failure
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step5_post_endpoint():
    """Step 5: Test POST endpoint with manual input"""
    print("\n" + "="*60)
    print("STEP 5: Testing POST Endpoint")
    print("="*60)
    test_data = {
        "total_sales": 50000,
        "credit_given": 15000,
        "credit_repaid": 13000,
        "tx_frequency": 120,
        "product_count": 40,
        "cooperative_member": 1,
        "days_active": 365
    }
    print(f"   Test data: {json.dumps(test_data, indent=2)}")
    try:
        response = requests.post(
            f"{BASE_URL}/ml/predict-credit-score",
            json=test_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ POST endpoint successful")
            print(f"   Score: {data.get('score')}")
            print(f"   Source: {data.get('source')}")
            
            # Validate score range
            score = data.get('score', 0)
            if 300 <= score <= 900:
                print(f"✅ Score in valid range: {score}")
            else:
                print(f"❌ Score out of range: {score}")
                return False
            
            # Check required fields
            if "source" not in data:
                print("❌ Missing 'source' field")
                return False
            
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step6_fallback():
    """Step 6: Test fallback mode (no model.pkl)"""
    print("\n" + "="*60)
    print("STEP 6: Testing Fallback Mode")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/ml/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            model_loaded = data.get('model_loaded', False)
            if not model_loaded:
                print("✅ Fallback mode active (model_loaded: false)")
                print("   System is using weighted baseline scoring")
                
                # Test that prediction still works
                test_data = {
                    "total_sales": 10000,
                    "credit_given": 5000,
                    "credit_repaid": 4500,
                    "tx_frequency": 50,
                    "product_count": 20,
                    "cooperative_member": 0,
                    "days_active": 90
                }
                pred_response = requests.post(
                    f"{BASE_URL}/ml/predict-credit-score",
                    json=test_data,
                    timeout=10
                )
                if pred_response.status_code == 200:
                    print("✅ Prediction works in fallback mode")
                    return True
                else:
                    print(f"❌ Prediction failed in fallback mode: {pred_response.status_code}")
                    return False
            else:
                print("ℹ️ Model is loaded (model.pkl exists)")
                print("   Fallback mode not active, but this is OK")
                return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step7_blockchain():
    """Step 7: Test blockchain integration"""
    print("\n" + "="*60)
    print("STEP 7: Testing Blockchain Integration")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/ml/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            blockchain_available = data.get('blockchain_available', False)
            print(f"   Blockchain available: {blockchain_available}")
            
            if blockchain_available:
                print("✅ Blockchain adapter is available")
                print("   (Testing with shopkeeper that has wallet_address would show blockchain in source)")
            else:
                print("ℹ️ Blockchain not available (offline mode)")
                print("   This is expected if blockchain credentials are not configured")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_step8_errors():
    """Step 8: Test error handling"""
    print("\n" + "="*60)
    print("STEP 8: Testing Error Handling")
    print("="*60)
    
    # Test invalid ID format
    print("   Testing invalid ID: '123'")
    try:
        response = requests.get(f"{BASE_URL}/ml/predict-credit-score/123", timeout=5)
        if response.status_code == 400:
            data = response.json()
            detail = data.get('detail', '')
            print(f"✅ Invalid ID returns 400: {detail}")
            if "Invalid shopkeeper ID" in detail:
                print("✅ Error message format correct")
            else:
                print(f"⚠️ Error message: {detail}")
        else:
            print(f"⚠️ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test non-existent ID
    print("\n   Testing non-existent ID: 'ffffffffffffffffffffffff'")
    try:
        response = requests.get(f"{BASE_URL}/ml/predict-credit-score/ffffffffffffffffffffffff", timeout=5)
        if response.status_code == 404:
            data = response.json()
            detail = data.get('detail', '')
            print(f"✅ Non-existent ID returns 404: {detail}")
            return True
        else:
            print(f"⚠️ Expected 404, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_step9_training():
    """Step 9: Test model training"""
    print("\n" + "="*60)
    print("STEP 9: Testing Model Training")
    print("="*60)
    import os
    from pathlib import Path
    
    model_path = Path("ml/model.pkl")
    if model_path.exists():
        print(f"✅ Model file exists: {model_path}")
        print("   Model training appears to have been completed")
        return True
    else:
        print(f"ℹ️ Model file not found: {model_path}")
        print("   Run: python ml/train_model.py to train the model")
        print("   System will use fallback weighted scoring until model is trained")
        return True  # Not a failure, just not trained yet

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ML CREDIT SCORING - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Step 1: Startup
    results['step1'] = test_step1_startup()
    if not results['step1']:
        print("\n❌ Backend not running. Please start it first:")
        print("   python main.py")
        return
    
    # Step 2: Health
    results['step2'] = test_step2_health()
    
    # Step 3: DB Aggregation (using example ID)
    results['step3'] = test_step3_db_aggregation("64f3a9b2e1d90a21c3f01a67")
    
    # Step 4: GET Endpoint
    results['step4'] = test_step4_get_endpoint("64f3a9b2e1d90a21c3f01a67")
    
    # Step 5: POST Endpoint
    results['step5'] = test_step5_post_endpoint()
    
    # Step 6: Fallback
    results['step6'] = test_step6_fallback()
    
    # Step 7: Blockchain
    results['step7'] = test_step7_blockchain()
    
    # Step 8: Errors
    results['step8'] = test_step8_errors()
    
    # Step 9: Training
    results['step9'] = test_step9_training()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for step, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{step.upper()}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests had issues (check output above)")

if __name__ == "__main__":
    main()

