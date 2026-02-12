#!/usr/bin/env python3
"""
Script to get the actual user credentials from the database.
"""

import os
import sys
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def get_user_credentials():
    """Get user credentials from database"""
    print("🔍 Retrieving user credentials from database...")
    
    try:
        from backend.app.db.mongodb import connect_to_mongo, get_database
        
        # Connect to database
        await connect_to_mongo()
        db = await get_database()
        
        # Get all users with their hashed passwords
        users = await db.users.find({}).to_list(length=10)
        
        print(f"📊 Found {len(users)} users:")
        print("=" * 50)
        
        for user in users:
            print(f"📧 Email: {user['email']}")
            print(f"👤 Name: {user['full_name']}")
            print(f"🏢 Firm: {user.get('firm_affiliation', 'N/A')}")
            print(f"👔 Role: {user['role']}")
            print(f"🔐 Password Hash: {user['hashed_password'][:20]}...")
            print("-" * 30)
        
        # Try to determine if there's a common password pattern
        print("\n💡 LIKELY CREDENTIALS TO TRY:")
        print("=" * 50)
        print("Since these are test users, try these common passwords:")
        for user in users:
            print(f"📧 {user['email']}")
            print("🔑 Possible passwords to try:")
            print("   - password")
            print("   - test123")
            print("   - admin123")
            print("   - testpassword")
            print("   - 123456")
            print()
        
        return users
        
    except Exception as e:
        print(f"❌ Failed to get user credentials: {e}")
        return []

async def main():
    """Main function"""
    print("🔐 USER CREDENTIALS RETRIEVAL")
    print("=" * 50)
    
    users = await get_user_credentials()
    
    if users:
        print("✅ Retrieved user information successfully!")
        print("\n📝 NEXT STEPS:")
        print("1. Try logging in with one of the emails above")
        print("2. Use common test passwords like 'password', 'test123', etc.")
        print("3. If none work, we'll need to reset a user's password")
    else:
        print("❌ Could not retrieve user information")

if __name__ == "__main__":
    asyncio.run(main())