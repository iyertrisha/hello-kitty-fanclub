"""
Test script to check cooperatives API endpoint
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_cooperatives_endpoint():
    """Test the /admin/cooperatives endpoint"""
    try:
        print("Testing GET /api/admin/cooperatives...")
        response = requests.get(f"{BASE_URL}/admin/cooperatives")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Success! Response data:")
            print(json.dumps(data, indent=2))
            
            if 'cooperatives' in data:
                cooperatives = data['cooperatives']
                print(f"\n📊 Found {len(cooperatives)} cooperatives:")
                for i, coop in enumerate(cooperatives, 1):
                    print(f"\n{i}. {coop.get('name', 'N/A')}")
                    print(f"   ID: {coop.get('id', 'N/A')}")
                    print(f"   Members: {coop.get('member_count', 0)}")
                    print(f"   Revenue Split: {coop.get('revenue_split', 0)}%")
                    print(f"   is_active: {coop.get('is_active', 'N/A')}")
            else:
                print("⚠️  Response does not contain 'cooperatives' key")
                print(f"   Keys in response: {list(data.keys())}")
        else:
            print(f"\n❌ Error! Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask server is not running!")
        print("   Start the server with: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_cooperatives_endpoint()

