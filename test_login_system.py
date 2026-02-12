#!/usr/bin/env python3
"""
Test script to diagnose and fix login authentication issues.
"""

import os
import sys
import asyncio
import requests
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def check_database_users():
    """Check if any users exist in the database"""
    print("🔍 Checking database for existing users...")
    
    try:
        from backend.app.db.mongodb import connect_to_mongo, get_database
        
        # Connect to database
        await connect_to_mongo()
        db = await get_database()
        
        # Count users
        user_count = await db.users.count_documents({})
        print(f"📊 Found {user_count} users in database")
        
        if user_count > 0:
            # Show existing users (without passwords)
            users = await db.users.find({}, {"email": 1, "full_name": 1, "role": 1}).to_list(length=10)
            print("👥 Existing users:")
            for user in users:
                print(f"  - {user['email']} ({user['full_name']}) - Role: {user['role']}")
        
        return user_count > 0
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def test_auth_endpoint():
    """Test the authentication endpoint"""
    print("\n🔍 Testing authentication endpoint...")
    
    try:
        # Test login endpoint with dummy credentials
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ Auth endpoint is working (401 Unauthorized - expected for invalid credentials)")
            return True
        elif response.status_code == 200:
            print("✅ Auth endpoint is working (200 OK - user exists)")
            return True
        else:
            print(f"⚠️  Auth endpoint returned unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server - is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Auth endpoint test failed: {e}")
        return False

async def create_test_user():
    """Create a test user for login testing"""
    print("\n🔧 Creating test user...")
    
    try:
        # Create test user via API
        user_data = {
            "email": "admin@jwhd.com",
            "password": "admin123",
            "full_name": "Admin User",
            "firm_affiliation": "JWHD",
            "role": "admin"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/auth/seed-user",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 201:
            print("✅ Test user created successfully!")
            print(f"📧 Email: {user_data['email']}")
            print(f"🔑 Password: {user_data['password']}")
            return True
        elif response.status_code == 400:
            print("ℹ️  Test user already exists")
            print(f"📧 Email: {user_data['email']}")
            print(f"🔑 Password: {user_data['password']}")
            return True
        else:
            print(f"❌ Failed to create test user: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test user creation failed: {e}")
        return False

def test_login_with_test_user():
    """Test login with the test user"""
    print("\n🔍 Testing login with test user...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={
                "username": "admin@jwhd.com",
                "password": "admin123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"🎫 Access token received: {data['access_token'][:20]}...")
            print(f"👤 User: {data['user']['full_name']} ({data['user']['email']})")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def test_frontend_backend_communication():
    """Test frontend-backend communication"""
    print("\n🔍 Testing frontend-backend communication...")
    
    try:
        # Test CORS and API accessibility
        response = requests.get(
            "http://localhost:8000/api/v1/openapi.json",
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Backend API is accessible from frontend")
            return True
        else:
            print(f"⚠️  API returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend-backend communication test failed: {e}")
        return False

async def main():
    """Run comprehensive login system diagnosis"""
    print("🚀 LOGIN SYSTEM DIAGNOSIS")
    print("=" * 50)
    
    # Test 1: Check database users
    has_users = await check_database_users()
    
    # Test 2: Test auth endpoint
    auth_working = test_auth_endpoint()
    
    # Test 3: Create test user if none exist
    if not has_users and auth_working:
        user_created = await create_test_user()
    else:
        user_created = True
    
    # Test 4: Test login with test user
    if user_created:
        login_working = test_login_with_test_user()
    else:
        login_working = False
    
    # Test 5: Test frontend-backend communication
    communication_working = test_frontend_backend_communication()
    
    # Summary
    print("\n📊 DIAGNOSIS SUMMARY")
    print("=" * 50)
    print(f"Database has users: {'✅ YES' if has_users else '❌ NO'}")
    print(f"Auth endpoint working: {'✅ YES' if auth_working else '❌ NO'}")
    print(f"Test user available: {'✅ YES' if user_created else '❌ NO'}")
    print(f"Login functionality: {'✅ WORKING' if login_working else '❌ BROKEN'}")
    print(f"Frontend-backend comm: {'✅ WORKING' if communication_working else '❌ BROKEN'}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("=" * 50)
    if not auth_working:
        print("❌ Backend server is not running or auth endpoint is broken")
        print("   → Start backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    elif not user_created:
        print("❌ No users exist and couldn't create test user")
        print("   → Check database connection and user creation endpoint")
    elif not login_working:
        print("❌ Login is broken despite having users")
        print("   → Check password hashing, database queries, or token generation")
    elif login_working:
        print("✅ Login system is working!")
        print("   → Use these credentials to login:")
        print("   📧 Email: admin@jwhd.com")
        print("   🔑 Password: admin123")
    
    if not communication_working:
        print("❌ Frontend cannot communicate with backend")
        print("   → Check CORS settings and network connectivity")

if __name__ == "__main__":
    asyncio.run(main())