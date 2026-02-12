import requests

def test_endpoints():
    """Test if enhanced applications endpoints are reachable"""
    print("🧪 Testing Enhanced Applications Endpoints...")
    
    # Login first
    login_data = {
        "username": "test@jwhd.com",
        "password": "test123"
    }
    
    try:
        print("1. Authenticating...")
        login_response = requests.post("http://localhost:8000/api/v1/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Authentication failed: {login_response.status_code}")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test GET enhanced-applications endpoint
        print("2. Testing GET /enhanced-applications...")
        get_response = requests.get(
            "http://localhost:8000/api/v1/enhanced-applications",
            headers=headers
        )
        
        print(f"📊 GET Response status: {get_response.status_code}")
        print(f"📄 GET Response: {get_response.text}")
        
        # Test if the save endpoint exists (should get 422 for missing body, not 404)
        print("3. Testing POST /save-enhanced-application (no body)...")
        post_response = requests.post(
            "http://localhost:8000/api/v1/save-enhanced-application",
            headers=headers
        )
        
        print(f"📊 POST Response status: {post_response.status_code}")
        print(f"📄 POST Response: {post_response.text}")
        
        if post_response.status_code == 404:
            print("❌ Endpoint not found - routing issue!")
        elif post_response.status_code == 422:
            print("✅ Endpoint exists but missing request body (expected)")
        else:
            print(f"🤔 Unexpected response: {post_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_endpoints()