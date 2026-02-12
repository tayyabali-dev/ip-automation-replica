#!/usr/bin/env python3
"""
Fix login issue by ensuring a test user exists and testing the login functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.db.mongodb import get_database
from app.core.security import get_password_hash, verify_password
from app.models.user import UserInDB
from datetime import datetime

async def fix_login_issue():
    """Fix login issue by creating a test user and verifying login functionality."""
    
    print("🔧 Fixing Login Issue")
    print("=" * 40)
    
    try:
        # Get database connection
        db = await get_database()
        
        # Check if any users exist
        print("📊 Checking existing users...")
        user_count = await db.users.count_documents({})
        print(f"Found {user_count} users in database")
        
        if user_count == 0:
            print("\n👤 Creating test user...")
            
            # Create a test user
            test_user = UserInDB(
                email="test@jwhd.com",
                full_name="Test User",
                firm_affiliation="JWHD Law Firm",
                role="paralegal",
                hashed_password=get_password_hash("TestPass123!"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert user into database
            result = await db.users.insert_one(test_user.model_dump(by_alias=True))
            print(f"✅ Test user created with ID: {result.inserted_id}")
            print(f"   Email: test@jwhd.com")
            print(f"   Password: TestPass123!")
            
        else:
            print("\n👥 Listing existing users:")
            async for user in db.users.find({}, {"email": 1, "full_name": 1, "role": 1}):
                print(f"   - {user['email']} ({user['full_name']}) - {user['role']}")
        
        # Test password verification
        print("\n🔐 Testing password verification...")
        test_password = "TestPass123!"
        hashed = get_password_hash(test_password)
        is_valid = verify_password(test_password, hashed)
        print(f"Password verification test: {'✅ PASS' if is_valid else '❌ FAIL'}")
        
        # Test login with existing user
        print("\n🧪 Testing login functionality...")
        test_user = await db.users.find_one({"email": "test@jwhd.com"})
        
        if test_user:
            # Test correct password
            is_correct = verify_password("TestPass123!", test_user["hashed_password"])
            print(f"Correct password test: {'✅ PASS' if is_correct else '❌ FAIL'}")
            
            # Test incorrect password
            is_incorrect = verify_password("WrongPassword", test_user["hashed_password"])
            print(f"Incorrect password test: {'✅ PASS' if not is_incorrect else '❌ FAIL'}")
            
            print(f"\n📋 Login Instructions:")
            print(f"   Email: test@jwhd.com")
            print(f"   Password: TestPass123!")
            print(f"   URL: http://localhost:3000/login")
            
        else:
            print("❌ No test user found")
        
        # Check database connection
        print(f"\n🔗 Database connection test...")
        try:
            await db.command("ping")
            print("✅ Database connection: OK")
        except Exception as e:
            print(f"❌ Database connection: FAILED - {e}")
        
        print(f"\n✅ Login issue diagnosis complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error during login fix: {e}")
        import traceback
        traceback.print_exc()
        return False

async def create_additional_users():
    """Create additional test users with different roles."""
    
    print("\n👥 Creating additional test users...")
    
    try:
        db = await get_database()
        
        additional_users = [
            {
                "email": "admin@jwhd.com",
                "password": "AdminPass123!",
                "full_name": "Admin User",
                "role": "admin",
                "firm_affiliation": "JWHD Law Firm"
            },
            {
                "email": "attorney@jwhd.com", 
                "password": "AttorneyPass123!",
                "full_name": "Attorney User",
                "role": "attorney",
                "firm_affiliation": "JWHD Law Firm"
            }
        ]
        
        for user_data in additional_users:
            # Check if user already exists
            existing = await db.users.find_one({"email": user_data["email"]})
            if existing:
                print(f"   User {user_data['email']} already exists")
                continue
                
            # Create new user
            new_user = UserInDB(
                email=user_data["email"],
                full_name=user_data["full_name"],
                firm_affiliation=user_data["firm_affiliation"],
                role=user_data["role"],
                hashed_password=get_password_hash(user_data["password"]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            result = await db.users.insert_one(new_user.model_dump(by_alias=True))
            print(f"   ✅ Created {user_data['email']} (Password: {user_data['password']})")
        
        print(f"\n📋 All Available Login Credentials:")
        print(f"   test@jwhd.com / TestPass123!")
        print(f"   admin@jwhd.com / AdminPass123!")
        print(f"   attorney@jwhd.com / AttorneyPass123!")
        
    except Exception as e:
        print(f"❌ Error creating additional users: {e}")

if __name__ == "__main__":
    success = asyncio.run(fix_login_issue())
    if success:
        asyncio.run(create_additional_users())
    sys.exit(0 if success else 1)