"""
Test script for newly implemented endpoints
Tests all the features added based on BACKEND_ARCHITECTURE_AND_REQUIREMENTS.md
"""
import requests
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional

BASE_URL = "http://localhost:5000/api"
test_results = []
test_ids = {}
session_cookies = {}  # Store session cookies for authenticated requests

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
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {method:6} {endpoint:60} [{status_code}] ({duration*1000:.0f}ms)")
    if error:
        print(f"         Error: {error}")
    elif response_data and not success:
        print(f"         Response: {str(response_data)[:100]}")

def test_endpoint(method: str, endpoint: str, data: Dict = None, 
                  params: Dict = None, expected_status = 200, 
                  use_cookies: str = None) -> Dict:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    headers = {"Content-Type": "application/json"}
    
    # Use session cookies if specified
    cookies = session_cookies.get(use_cookies) if use_cookies else None
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, cookies=cookies, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, cookies=cookies, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, cookies=cookies, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        duration = time.time() - start_time
        if isinstance(expected_status, list):
            success = response.status_code in expected_status
        else:
            success = response.status_code == expected_status
        
        # Store cookies for session-based auth
        if use_cookies and response.cookies:
            session_cookies[use_cookies] = response.cookies
        
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
    print("[*] Waiting for server to start...")
    for i in range(max_wait):
        try:
            response = requests.get(f"{BASE_URL}/admin/overview", timeout=2)
            if response.status_code in [200, 404]:
                print("[+] Server is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"   Attempt {i+1}/{max_wait}...")
    print("[-] Server did not start in time")
    return False

def get_test_shopkeeper_id():
    """Get a shopkeeper ID from the database"""
    result = test_endpoint("GET", "/shopkeeper")
    if result["success"] and result["data"] and "shopkeepers" in result["data"]:
        shopkeepers = result["data"]["shopkeepers"]
        if shopkeepers:
            return shopkeepers[0].get("id")
    return None

def get_test_cooperative_id():
    """Get a cooperative ID from the database"""
    result = test_endpoint("GET", "/cooperative")
    if result["success"] and result["data"] and "cooperatives" in result["data"]:
        cooperatives = result["data"]["cooperatives"]
        if cooperatives:
            return cooperatives[0].get("id")
    return None

def main():
    print("=" * 80)
    print("NEW ENDPOINTS TEST SUITE")
    print("Testing all newly implemented features")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Test started: {datetime.now().isoformat()}\n")
    
    # Wait for server
    if not wait_for_server():
        print("\n❌ Cannot proceed - server is not running")
        print("Please start the server with: python run.py")
        return
    
    # Get test IDs
    print("\n[*] Getting test data...")
    test_ids["shopkeeper_id"] = get_test_shopkeeper_id()
    test_ids["cooperative_id"] = get_test_cooperative_id()
    
    if not test_ids["shopkeeper_id"]:
        print("[-] No shopkeepers found in database. Please seed the database first.")
        print("Run: python database\\seeders\\seed_data.py")
        return
    
    print(f"[+] Using shopkeeper ID: {test_ids['shopkeeper_id']}")
    if test_ids["cooperative_id"]:
        print(f"[+] Using cooperative ID: {test_ids['cooperative_id']}")
    
    print("\n" + "=" * 80)
    print("TESTING NEW SHOPKEEPER ENDPOINTS")
    print("=" * 80 + "\n")
    
    # ==================== SHOPKEEPER LOGIN & AUTH ====================
    print("\n1. SHOPKEEPER LOGIN & AUTHENTICATION")
    print("-" * 80)
    
    # Get shopkeeper phone for testing
    shopkeeper_info = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}")
    test_phone = None
    if shopkeeper_info["success"] and shopkeeper_info["data"]:
        test_phone = shopkeeper_info["data"].get("phone", "+919876543210")
    else:
        test_phone = "+919876543210"
    
    print(f"   Using phone: {test_phone}")
    
    # Request OTP
    print("\n   1.1 Request OTP")
    otp_result = test_endpoint("POST", "/shopkeeper/login/request-otp", 
                              data={"phone": test_phone}, expected_status=200)
    
    # Note: In dev mode, OTP is logged to console
    # For testing, we'll need to check console or use a known OTP
    print("      ℹ️  Check console output for OTP code (dev mode)")
    
    # Verify OTP (this will likely fail unless we have the actual OTP)
    # But we test the endpoint structure
    print("\n   1.2 Verify OTP (will fail without actual OTP - expected)")
    test_endpoint("POST", "/shopkeeper/login/verify-otp",
                 data={"phone": test_phone, "otp_code": "000000"}, 
                 expected_status=[401, 400], use_cookies="shopkeeper")
    
    # Test /me endpoint (will fail without valid session - expected)
    print("\n   1.3 Get current shopkeeper (/me)")
    test_endpoint("GET", "/shopkeeper/me", expected_status=[401, 403], use_cookies="shopkeeper")
    
    # Test logout
    print("\n   1.4 Logout")
    test_endpoint("POST", "/shopkeeper/logout", expected_status=200, use_cookies="shopkeeper")
    
    # ==================== SHOPKEEPER PROFILE ====================
    print("\n2. SHOPKEEPER PROFILE MANAGEMENT")
    print("-" * 80)
    
    print("\n   2.1 Get shopkeeper profile")
    profile_result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/profile")
    
    print("\n   2.2 Update shopkeeper profile")
    update_data = {
        "name": "Updated Test Shop",
        "address": "Updated Test Address",
        "email": "updated@test.com"
    }
    test_endpoint("POST", f"/shopkeeper/{test_ids['shopkeeper_id']}/profile", 
                 data=update_data, expected_status=200)
    
    # ==================== QR CODE GENERATION ====================
    print("\n3. QR CODE GENERATION")
    print("-" * 80)
    
    print("\n   3.1 Generate QR code")
    qr_result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/qr-code")
    if qr_result["success"] and qr_result["data"]:
        print(f"      [+] QR code generated: {qr_result['data'].get('whatsapp_url', 'N/A')[:50]}...")
        if qr_result["data"].get("qr_code"):
            print(f"      [+] QR code image (base64): {len(qr_result['data']['qr_code'])} chars")
    
    # ==================== INVENTORY MANAGEMENT ====================
    print("\n4. INVENTORY MANAGEMENT")
    print("-" * 80)
    
    # Get existing inventory
    print("\n   4.1 Get inventory")
    inventory_result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/inventory")
    existing_product_id = None
    if inventory_result["success"] and inventory_result["data"] and "inventory" in inventory_result["data"]:
        inventory = inventory_result["data"]["inventory"]
        if inventory:
            existing_product_id = inventory[0].get("id")
            print(f"      Found {len(inventory)} products")
    
    # Add new product
    print("\n   4.2 Add new product")
    new_product = {
        "name": "Test Product " + str(int(time.time())),
        "price": 99.99,
        "stock_quantity": 50,
        "category": "Test Category",
        "description": "Test product for endpoint testing"
    }
    add_product_result = test_endpoint("POST", f"/shopkeeper/{test_ids['shopkeeper_id']}/inventory",
                                      data=new_product, expected_status=201)
    if add_product_result["success"] and add_product_result["data"]:
        test_ids["new_product_id"] = add_product_result["data"].get("id")
        print(f"      [+] Created product ID: {test_ids['new_product_id']}")
    
    # Delete product
    print("\n   4.3 Delete product")
    if test_ids.get("new_product_id"):
        test_endpoint("DELETE", f"/shopkeeper/{test_ids['shopkeeper_id']}/inventory/{test_ids['new_product_id']}",
                     expected_status=200)
    elif existing_product_id:
        print(f"      [!] Using existing product ID (will delete it): {existing_product_id}")
        test_endpoint("DELETE", f"/shopkeeper/{test_ids['shopkeeper_id']}/inventory/{existing_product_id}",
                     expected_status=200)
    
    # ==================== TRANSACTION ENDPOINTS ====================
    print("\n5. TRANSACTION ENDPOINTS")
    print("-" * 80)
    
    print("\n   5.1 Get recent transactions")
    recent_result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/transactions/recent",
                                 params={"limit": 10, "days": 30})
    
    print("\n   5.2 Get transaction stats")
    stats_result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/transactions/stats")
    if stats_result["success"] and stats_result["data"]:
        print(f"      Total sales: ₹{stats_result['data'].get('total_sales', 0)}")
        print(f"      Total credits: ₹{stats_result['data'].get('total_credits', 0)}")
    
    print("\n   5.3 Get credit summary")
    credit_summary = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/credit-summary")
    if credit_summary["success"] and credit_summary["data"]:
        print(f"      Total credits given: ₹{credit_summary['data'].get('total_credits_given', 0)}")
        print(f"      Outstanding credits: ₹{credit_summary['data'].get('outstanding_credits', 0)}")
    
    print("\n   5.4 Get debt summary")
    debt_summary = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/debt-summary")
    if debt_summary["success"] and debt_summary["data"]:
        print(f"      Customers with debt: {debt_summary['data'].get('customer_count', 0)}")
    
    # ==================== COOPERATIVE ENDPOINTS ====================
    print("\n6. COOPERATIVE ENDPOINTS")
    print("-" * 80)
    
    print("\n   6.1 Get shopkeeper's cooperatives")
    shopkeeper_coops = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/cooperatives")
    if shopkeeper_coops["success"] and shopkeeper_coops["data"]:
        print(f"      Cooperatives: {len(shopkeeper_coops['data'].get('cooperatives', []))}")
    
    print("\n   6.2 Leave cooperative")
    if test_ids.get("cooperative_id"):
        # First try to join (in case not already a member)
        test_endpoint("POST", f"/cooperative/{test_ids['cooperative_id']}/join",
                     data={"shopkeeper_id": test_ids["shopkeeper_id"]},
                     expected_status=[200, 400])
        
        # Then test leave
        test_endpoint("POST", f"/cooperative/{test_ids['cooperative_id']}/leave",
                     data={"shopkeeper_id": test_ids["shopkeeper_id"]},
                     expected_status=200)
    
    # ==================== WHATSAPP BOT ENDPOINTS ====================
    print("\n7. WHATSAPP BOT ENDPOINTS")
    print("-" * 80)
    
    print("\n   7.1 Get shopkeeper by phone")
    whatsapp_shopkeeper = test_endpoint("GET", f"/whatsapp/shopkeeper-by-phone",
                                       params={"phone": test_phone},
                                       expected_status=[200, 401, 403])
    
    print("\n   7.2 Get products for WhatsApp")
    whatsapp_products = test_endpoint("GET", f"/whatsapp/products",
                                     params={"shopkeeper_phone": test_phone},
                                     expected_status=[200, 401, 403])
    if whatsapp_products["success"] and whatsapp_products["data"]:
        print(f"      Products found: {len(whatsapp_products['data'].get('products', []))}")
        if whatsapp_products["data"].get("formatted_text"):
            print(f"      Formatted text length: {len(whatsapp_products['data']['formatted_text'])} chars")
    
    # ==================== SUPPLIER PORTAL ENDPOINTS ====================
    print("\n8. SUPPLIER PORTAL ENDPOINTS")
    print("-" * 80)
    
    # Note: Supplier endpoints require authentication
    # We'll test the geographic filtering endpoint structure
    
    print("\n   8.1 Get stores with geographic filter")
    geo_stores = test_endpoint("GET", "/supplier/stores",
                              params={"lat": 28.6139, "lng": 77.2090, "radius": 10},
                              expected_status=[200, 401, 403])
    if geo_stores["success"] and geo_stores["data"]:
        print(f"      Stores found: {geo_stores['data'].get('count', 0)}")
    
    print("\n   8.2 Get blockchain transactions (requires auth)")
    test_endpoint("GET", f"/supplier/blockchain/transactions",
                 params={"shopkeeper_id": test_ids["shopkeeper_id"]},
                 expected_status=[200, 401, 403])
    
    print("\n   8.3 Verify transaction on blockchain (requires auth)")
    test_endpoint("GET", "/supplier/blockchain/verify",
                 params={"tx_hash": "0x1234567890abcdef"},
                 expected_status=[200, 401, 403, 404])
    
    # ==================== ADMIN ENDPOINTS ====================
    print("\n9. ADMIN ENDPOINTS")
    print("-" * 80)
    
    print("\n   9.1 Inventory seeding")
    seed_data = {
        "products": [
            {
                "name": "Seeded Test Product 1",
                "price": 49.99,
                "stock_quantity": 100,
                "category": "Test"
            },
            {
                "name": "Seeded Test Product 2",
                "price": 79.99,
                "stock_quantity": 50,
                "category": "Test"
            }
        ],
        "shopkeeper_id": test_ids["shopkeeper_id"]
    }
    seed_result = test_endpoint("POST", "/admin/inventory/seed",
                               data=seed_data, expected_status=[201, 200])
    if seed_result["success"] and seed_result["data"]:
        print(f"      [+] Seeded {seed_result['data'].get('seeded_count', 0)} products")
    
    # ==================== CREDIT SCORE WITH LIMIT ====================
    print("\n10. CREDIT SCORE WITH LIMIT")
    print("-" * 80)
    
    print("\n   10.1 Get credit score (should include credit_limit)")
    credit_score_result = test_endpoint("GET", f"/shopkeeper/{test_ids['shopkeeper_id']}/credit-score")
    if credit_score_result["success"] and credit_score_result["data"]:
        score_data = credit_score_result["data"]
        print(f"      Credit score: {score_data.get('score', 'N/A')}")
        if "credit_limit" in score_data:
            print(f"      [+] Credit limit: {score_data.get('credit_limit', 0)}")
        else:
            print(f"      [!] Credit limit not found in response")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r["success"])
    failed_tests = total_tests - passed_tests
    avg_duration = sum(r["duration_ms"] for r in test_results) / total_tests if total_tests > 0 else 0
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"[+] Passed: {passed_tests}")
    print(f"[-] Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print(f"Average Response Time: {avg_duration:.2f}ms")
    
    # Group by category
    print("\n" + "=" * 80)
    print("RESULTS BY CATEGORY")
    print("=" * 80)
    
    categories = {
        "Shopkeeper Auth": ["/shopkeeper/login", "/shopkeeper/me", "/shopkeeper/logout"],
        "Profile": ["/shopkeeper/", "/profile"],
        "QR Code": ["/qr-code"],
        "Inventory": ["/inventory"],
        "Transactions": ["/transactions/"],
        "Cooperatives": ["/cooperatives", "/cooperative/", "/leave"],
        "WhatsApp": ["/whatsapp/"],
        "Supplier": ["/supplier/"],
        "Admin": ["/admin/inventory"]
    }
    
    for category, keywords in categories.items():
        category_tests = [r for r in test_results if any(kw in r["endpoint"] for kw in keywords)]
        if category_tests:
            category_passed = sum(1 for r in category_tests if r["success"])
            category_total = len(category_tests)
            print(f"{category:20} {category_passed:3}/{category_total:3} ({(category_passed/category_total*100):.1f}%)")
    
    # Save results
    report = {
        "test_run": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0,
        "average_duration_ms": avg_duration,
        "results": test_results
    }
    
    with open("new_endpoints_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[*] Detailed report saved to: new_endpoints_test_report.json")
    
    if failed_tests > 0:
        print("\n[!] Some tests failed. Check the output above for details.")
        print("Note: Some failures may be expected (e.g., authentication required, invalid OTP)")
        return 1
    else:
        print("\n[+] All tests completed successfully!")
        return 0

if __name__ == "__main__":
    exit(main())

