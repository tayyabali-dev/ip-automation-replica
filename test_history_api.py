#!/usr/bin/env python3
"""
Test script to verify the enhanced applications API endpoints are working correctly.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"  # Correct API base URL
TEST_USER_EMAIL = "test@jwhd.com"  # Use the test user from seed_user.py
TEST_USER_PASSWORD = "test123"  # Use the test password from seed_user.py

def test_enhanced_applications_api():
    """Test the enhanced applications API endpoints"""
    
    print("🧪 Testing Enhanced Applications API...")
    
    # Step 1: Login to get authentication token
    print("\n1. Authenticating...")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        # Use form data for OAuth2PasswordRequestForm
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print("✅ Authentication successful")
        
        # Step 2: Test getting enhanced applications
        print("\n2. Testing GET /enhanced-applications...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        apps_response = requests.get(f"{BASE_URL}/enhanced-applications", headers=headers)
        
        if apps_response.status_code == 200:
            applications = apps_response.json()
            print(f"✅ Successfully retrieved {len(applications)} applications")
            
            if applications:
                print("\n📋 Sample application structure:")
                sample_app = applications[0]
                print(json.dumps({
                    "_id": sample_app.get("_id"),
                    "title": sample_app.get("title"),
                    "application_number": sample_app.get("application_number"),
                    "filing_date": sample_app.get("filing_date"),
                    "inventors_count": len(sample_app.get("inventors", [])),
                    "applicants_count": len(sample_app.get("applicants", [])),
                    "quality_score": sample_app.get("quality_metrics", {}).get("overall_quality_score"),
                    "workflow_status": sample_app.get("workflow_status"),
                    "created_at": sample_app.get("created_at")
                }, indent=2))
            else:
                print("📝 No applications found - this is normal if no applications have been processed yet")
            
            return True
        else:
            print(f"❌ Failed to retrieve applications: {apps_response.status_code} - {apps_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on the correct port.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_endpoints():
    """Test all relevant API endpoints"""
    print("🚀 Starting API endpoint tests...\n")
    
    # Test enhanced applications
    success = test_enhanced_applications_api()
    
    if success:
        print("\n🎉 All tests passed! The history functionality should work correctly.")
    else:
        print("\n💥 Tests failed. Please check the backend configuration and ensure:")
        print("   - Backend server is running")
        print("   - Database is connected")
        print("   - User authentication is working")
        print("   - Enhanced applications endpoints are properly registered")

if __name__ == "__main__":
    test_api_endpoints()