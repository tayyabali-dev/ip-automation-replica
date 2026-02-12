#!/usr/bin/env python3
"""
Debug script to examine the structure of saved applications and identify conversion issues.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@jwhd.com"
TEST_USER_PASSWORD = "test123"

async def debug_saved_application_structure():
    """Debug the structure of saved applications."""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Debugging Saved Application Structure")
        print("=" * 50)
        
        # Step 1: Login to get JWT token
        print("\n1. Logging in...")
        login_data = {
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        async with session.post(
            f"{BASE_URL}/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                return
            
            result = await response.json()
            token = result.get("access_token")
            print("✅ Login successful")
        
        # Set authorization header
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get list of saved applications
        print("\n2. Getting saved applications...")
        async with session.get(f"{BASE_URL}/enhanced-applications", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Failed to get applications: {response.status}")
                return
            
            applications = await response.json()
            print(f"✅ Found {len(applications)} saved applications")
            
            if not applications:
                print("⚠️  No saved applications found.")
                return
        
        # Step 3: Get detailed structure of the first application
        test_app = applications[0]
        app_id = test_app['_id']
        
        print(f"\n3. Getting detailed structure for application: {app_id}")
        async with session.get(f"{BASE_URL}/enhanced-applications/{app_id}", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Failed to get application details: {response.status}")
                return
            
            app_details = await response.json()
            
            # Save the structure to a file for analysis
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"saved_app_structure_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(app_details, f, indent=2, default=str)
            
            print(f"✅ Application structure saved to: {filename}")
            
            # Analyze the structure
            print(f"\n4. Analyzing application structure:")
            print(f"   Top-level keys: {list(app_details.keys())}")
            
            # Check for required fields
            required_fields = [
                'title', 'application_number', 'filing_date', 'inventors', 
                'applicants', 'quality_metrics', 'extraction_metadata'
            ]
            
            missing_fields = []
            present_fields = []
            
            for field in required_fields:
                if field in app_details:
                    present_fields.append(field)
                    if isinstance(app_details[field], list):
                        print(f"   ✅ {field}: {len(app_details[field])} items")
                    elif isinstance(app_details[field], dict):
                        print(f"   ✅ {field}: {len(app_details[field])} keys")
                    else:
                        print(f"   ✅ {field}: {app_details[field]}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {field}: MISSING")
            
            # Check quality_metrics structure if present
            if 'quality_metrics' in app_details:
                qm = app_details['quality_metrics']
                print(f"\n   Quality Metrics structure:")
                for key, value in qm.items():
                    print(f"     - {key}: {value}")
            
            # Check extraction_metadata structure if present
            if 'extraction_metadata' in app_details:
                em = app_details['extraction_metadata']
                print(f"\n   Extraction Metadata structure:")
                for key, value in em.items():
                    print(f"     - {key}: {value}")
            
            print(f"\n5. Summary:")
            print(f"   Present fields: {len(present_fields)}/{len(required_fields)}")
            print(f"   Missing fields: {missing_fields}")
            
            if missing_fields:
                print(f"\n⚠️  Missing required fields may cause conversion issues.")
            else:
                print(f"\n✅ All required fields are present.")
            
            # Try to identify the specific conversion issue
            print(f"\n6. Testing conversion to EnhancedExtractionResult...")
            
            # Remove MongoDB-specific fields (simulate what the endpoint does)
            clean_data = {k: v for k, v in app_details.items() if k not in ['_id', 'created_by', 'created_at', 'workflow_status']}
            
            # Save the clean data for manual inspection
            clean_filename = f"clean_app_data_{timestamp}.json"
            with open(clean_filename, 'w') as f:
                json.dump(clean_data, f, indent=2, default=str)
            
            print(f"   Clean data saved to: {clean_filename}")
            print(f"   Clean data keys: {list(clean_data.keys())}")

if __name__ == "__main__":
    asyncio.run(debug_saved_application_structure())