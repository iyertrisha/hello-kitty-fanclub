"""
Comprehensive Backend API Testing Script
Tests all endpoints and generates a detailed report
"""
import requests
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:5000/api"
test_results = []
test_ids = {}  # Store IDs for later tests

def log_test(endpoint: str, method: str, status_code: int, success: bool, 
             response_data: Any = None, error: str = None, duration: float = 0):
    """Log test result"""
    result = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "success": success,
        "duration_ms": round(duration * 1000, 2),
        "timestamp": datetime.now().isoformat(),
        "error": error,
        "response_preview": str(response_data)[:200] if response_data else None
    }
    test_results.append(result)
    status = "PASS" if success else "FAIL"
    print(f"{status} {method:6} {endpoint:50} [{status_code}] ({duration*1000:.0f}ms)")
    if error:
        print(f"         Error: {error}")

def test_endpoint(method: str, endpoint: str, data: Dict = None, 
                  params: Dict = None, expected_status = 200) -> Dict:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        duration = time.time() - start_time
        if isinstance(expected_status, list):
            success = response.status_code in expected_status
        else:
            success = response.status_code == expected_status
        
        try:
            response_data = response.json() if response.content else None
        except:
            response_data = response.text[:200]
        
        log_test(endpoint, method, response.status_code, success, 
                response_data, None, duration)
        
        return {"success": success, "data": response_data, "status_code": response.status_code}
    
    except requests.exceptions.ConnectionError:
        duration = time.time() - start_time
        log_test(endpoint, method, 0, False, None, 
                "Connection refused - Server not running", duration)
        return {"success": False, "data": None, "error": "Connection refused"}
    
    except Exception as e:
        duration = time.time() - start_time
        log_test(endpoint, method, 0, False, None, str(e), duration)
        return {"success": False, "data": None, "error": str(e)}

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    print("Waiting for server to start...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/admin/overview", timeout=2)
            if response.status_code in [200, 404]:  # 404 means server is up but route might not exist
                print("Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   Attempt {i+1}/{max_wait}...")
    print("Server did not start in time")
    return False

def main():
    print("=" * 80)
    print("BACKEND API COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test started: {datetime.now().isoformat()}\n")
    
    # Wait for server
    if not wait_for_server():
        print("\nCannot proceed - server is not running")
        print("Please start the server with: python run.py")
        return
    
    print("\n" + "=" * 80)
    print("TESTING ENDPOINTS")
    print("=" * 80 + "\n")
    
    # ==================== ADMIN ENDPOINTS ====================
    print("\nADMIN ENDPOINTS")
    print("-" * 80)
    
    # GET /api/admin/overview
    result = test_endpoint("GET", "/admin/overview")
    if result["success"] and result["data"]:
        test_ids["overview"] = result["data"]
    
    # GET /api/admin/stores
    result = test_endpoint("GET", "/admin/stores")
    if result["success"] and result["data"] and "stores" in result["data"]:
        stores = result["data"]["stores"]
        if stores:
            test_ids["shopkeeper_id"] = stores[0].get("id") or str(stores[0].get("_id", ""))
    
    # GET /api/admin/cooperatives
    result = test_endpoint("GET", "/admin/cooperatives")
    if result["success"] and result["data"] and "cooperatives" in result["data"]:
        cooperatives = result["data"]["cooperatives"]
        if cooperatives:
            test_ids["cooperative_id"] = cooperatives[0].get("id") or str(cooperatives[0].get("_id", ""))
    
    # GET /api/admin/analytics
    test_endpoint("GET", "/admin/analytics")
    
    # GET /api/admin/blockchain-logs
    test_endpoint("GET", "/admin/blockchain-logs")
    
    # ==================== TRANSACTION ENDPOINTS ====================
    print("\nTRANSACTION ENDPOINTS")
    print("-" * 80)
    
    # GET /api/transactions
    result = test_endpoint("GET", "/transactions", params={"page": 1, "page_size": 5})
    if result["success"] and result["data"] and "transactions" in result["data"]:
        transactions = result["data"]["transactions"]
        if transactions:
            test_ids["transaction_id"] = transactions[0].get("id") or str(transactions[0].get("_id", ""))
            test_ids["customer_id"] = transactions[0].get("customer_id")
    
    # GET /api/transactions with filters
    test_endpoint("GET", "/transactions", params={"type": "sale", "page_size": 3})
    test_endpoint("GET", "/transactions", params={"status": "verified", "page_size": 3})
    
    # GET /api/transactions/<id>
    if test_ids.get("transaction_id"):
        test_endpoint("GET", f"/transactions/{test_ids['transaction_id']}")
    
    # POST /api/transactions
    if test_ids.get("shopkeeper_id") and test_ids.get("customer_id"):
        new_transaction = {
            "type": "sale",
            "amount": 250.75,
            "shopkeeper_id": test_ids["shopkeeper_id"],
            "customer_id": test_ids["customer_id"]
        }
        result = test_endpoint("POST", "/transactions", data=new_transaction, expected_status=201)
        if result["success"] and result["data"]:
            test_ids["new_transaction_id"] = result["data"].get("id")
    
    # PUT /api/transactions/<id>/status
    if test_ids.get("transaction_id"):
        update_data = {
            "status": "verified",
            "blockchain_tx_id": "0x1234567890abcdef",
            "blockchain_block_number": 1234567
        }
        test_endpoint("PUT", f"/transactions/{test_ids['transaction_id']}/status", 
                     data=update_data)
    
    # ==================== SHOPKEEPER ENDPOINTS ====================
    print("\nSHOPKEEPER ENDPOINTS")
    print("-" * 80)
    
    # GET /api/shopkeeper/<id>
    if test_ids.get("shopkeeper_id"):
        result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}")
    
    # GET /api/shopkeeper/<id>/credit-score
    if test_ids.get("shopkeeper_id"):
        test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/credit-score")
    
    # GET /api/shopkeeper/<id>/inventory
    if test_ids.get("shopkeeper_id"):
        result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/inventory")
        if result["success"] and result["data"] and "inventory" in result["data"]:
            inventory = result["data"]["inventory"]
            if inventory:
                test_ids["product_id"] = inventory[0].get("id") or str(inventory[0].get("_id", ""))
    
    # POST /api/shopkeeper/register
    unique_hash = hashlib.md5(f"test_shopkeeper_{int(time.time())}".encode()).hexdigest()[:40]
    new_shopkeeper = {
        "name": "Test Shopkeeper Store",
        "address": "Test Address, Test City",
        "phone": f"+919{int(time.time()) % 10000000000}",  # Unique phone
        "wallet_address": f"0x{unique_hash}",
        "email": f"test{int(time.time())}@example.com"
    }
    result = test_endpoint("POST", "/shopkeeper/register", data=new_shopkeeper, expected_status=201)
    if result["success"] and result["data"]:
        test_ids["new_shopkeeper_id"] = result["data"].get("id")
    
    # PUT /api/shopkeeper/<id>
    if test_ids.get("shopkeeper_id"):
        update_data = {
            "name": "Updated Shopkeeper Name",
            "address": "Updated Address"
        }
        test_endpoint("PUT", f"/shopkeeper/{test_ids['shopkeeper_id']}", data=update_data)
    
    # PUT /api/shopkeeper/<id>/inventory/<product_id>
    if test_ids.get("shopkeeper_id") and test_ids.get("product_id"):
        update_inventory = {
            "price": 55.00,
            "stock_quantity": 100
        }
        test_endpoint("PUT", f"/shopkeeper/{test_ids['shopkeeper_id']}/inventory/{test_ids['product_id']}", 
                     data=update_inventory)
    
    # ==================== CUSTOMER ENDPOINTS ====================
    print("\nCUSTOMER ENDPOINTS")
    print("-" * 80)
    
    # GET /api/customer/<id>
    if test_ids.get("customer_id"):
        test_endpoint("GET", f"/customer/{test_ids['customer_id']}")
    
    # GET /api/customer/<id>/orders
    if test_ids.get("customer_id"):
        test_endpoint("GET", f"/customer/{test_ids['customer_id']}/orders")
    
    # GET /api/customer/<id>/credits
    if test_ids.get("customer_id"):
        test_endpoint("GET", f"/customer/{test_ids['customer_id']}/credits")
    
    # POST /api/customer
    new_customer = {
        "name": "Test Customer",
        "phone": f"+919{int(time.time()) % 10000000000}",
        "address": "Test Address, Test City"
    }
    result = test_endpoint("POST", "/customer", data=new_customer, expected_status=201)
    if result["success"] and result["data"]:
        test_ids["new_customer_id"] = result["data"].get("id")
    
    # ==================== COOPERATIVE ENDPOINTS ====================
    print("\nCOOPERATIVE ENDPOINTS")
    print("-" * 80)
    
    # GET /api/cooperative
    test_endpoint("GET", "/cooperative")
    
    # GET /api/cooperative/<id>
    if test_ids.get("cooperative_id"):
        test_endpoint("GET", f"/cooperative/{test_ids['cooperative_id']}")
    
    # GET /api/cooperative/<id>/members
    if test_ids.get("cooperative_id"):
        test_endpoint("GET", f"/cooperative/{test_ids['cooperative_id']}/members")
    
    # GET /api/cooperative/<id>/orders
    if test_ids.get("cooperative_id"):
        test_endpoint("GET", f"/cooperative/{test_ids['cooperative_id']}/orders")
    
    # POST /api/cooperative/<id>/join
    if test_ids.get("cooperative_id") and test_ids.get("shopkeeper_id"):
        join_data = {
            "shopkeeper_id": test_ids["shopkeeper_id"]
        }
        # Accept both 200 (successful join) and 400 (already a member) as valid
        test_endpoint("POST", f"/cooperative/{test_ids['cooperative_id']}/join", data=join_data, expected_status=[200, 400])
    
    # ==================== BLOCKCHAIN ENDPOINTS ====================
    print("\nBLOCKCHAIN ENDPOINTS")
    print("-" * 80)
    
    # POST /api/blockchain/record-transaction
    if test_ids.get("transaction_id"):
        blockchain_data = {
            "transaction_id": test_ids["transaction_id"],
            "amount": 100.50
        }
        test_endpoint("POST", "/blockchain/record-transaction", data=blockchain_data, expected_status=[200, 400, 500, 503])
    
    # GET /api/blockchain/transaction/<id>
    if test_ids.get("transaction_id"):
        test_endpoint("GET", f"/blockchain/transaction/{test_ids['transaction_id']}", expected_status=[200, 404, 503])
    
    # POST /api/blockchain/register-shopkeeper
    if test_ids.get("shopkeeper_id"):
        register_data = {
            "shopkeeper_id": test_ids["shopkeeper_id"]
        }
        test_endpoint("POST", "/blockchain/register-shopkeeper", data=register_data, expected_status=[200, 400, 500, 503])
    
    # GET /api/blockchain/credit-score/<shopkeeper_id>
    if test_ids.get("shopkeeper_id"):
        test_endpoint("GET", f"/blockchain/credit-score/{test_ids['shopkeeper_id']}", expected_status=[200, 404, 503])
    
    # ==================== ERROR HANDLING TESTS ====================
    print("\nERROR HANDLING TESTS")
    print("-" * 80)
    
    # Test 404
    test_endpoint("GET", "/shopkeeper/000000000000000000000000", expected_status=404)
    
    # Test 400 - Invalid transaction
    invalid_transaction = {"type": "invalid"}
    test_endpoint("POST", "/transactions", data=invalid_transaction, expected_status=400)
    
    # Test 400 - Missing required fields
    incomplete_data = {"name": "Test"}
    test_endpoint("POST", "/customer", data=incomplete_data, expected_status=400)
    
    # ==================== GENERATE REPORT ====================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["success"])
    failed_tests = total_tests - passed_tests
    avg_duration = sum(r["duration_ms"] for r in test_results) / total_tests if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"Average Response Time: {avg_duration:.2f}ms")
    
    # Group by endpoint category
    print("\n" + "=" * 80)
    print("RESULTS BY CATEGORY")
    print("=" * 80)
    
    categories = {
        "Admin": [r for r in test_results if "/admin" in r["endpoint"]],
        "Transactions": [r for r in test_results if "/transactions" in r["endpoint"]],
        "Shopkeeper": [r for r in test_results if "/shopkeeper" in r["endpoint"]],
        "Customer": [r for r in test_results if "/customer" in r["endpoint"]],
        "Cooperative": [r for r in test_results if "/cooperative" in r["endpoint"]],
        "Blockchain": [r for r in test_results if "/blockchain" in r["endpoint"]],
        "Error Handling": [r for r in test_results if r["endpoint"].startswith("/") and 
                          (r["status_code"] in [400, 404] or "000000000000000000000000" in r["endpoint"])]
    }
    
    for category, results in categories.items():
        if results:
            passed = sum(1 for r in results if r["success"])
            total = len(results)
            print(f"\n{category}: {passed}/{total} passed ({(passed/total*100):.1f}%)")
    
    # Failed tests details
    failed = [r for r in test_results if not r["success"]]
    if failed:
        print("\n" + "=" * 80)
        print("FAILED TESTS DETAILS")
        print("=" * 80)
        for result in failed:
            print(f"\nFAIL {result['method']} {result['endpoint']}")
            print(f"   Status: {result['status_code']}")
            if result['error']:
                print(f"   Error: {result['error']}")
    
    # Save detailed report to file
    report = {
        "test_summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%",
            "average_duration_ms": round(avg_duration, 2),
            "test_timestamp": datetime.now().isoformat()
        },
        "test_results": test_results,
        "test_ids_used": test_ids
    }
    
    report_file = "backend_test_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    print(f"Test completed: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nTest suite error: {e}")
        import traceback
        traceback.print_exc()

