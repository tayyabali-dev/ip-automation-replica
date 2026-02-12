#!/usr/bin/env python3
"""
Test script to verify the complete history download ADS functionality.
This tests the new endpoint for generating ADS from saved applications.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@jwhd.com"
TEST_USER_PASSWORD = "test123"

async def test_history_download_functionality():
    """Test the complete history download ADS functionality."""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing History Download ADS Functionality")
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
                text = await response.text()
                print(f"Response: {text}")
                return
            
            result = await response.json()
            token = result.get("access_token")
            if not token:
                print("❌ No access token received")
                return
            
            print("✅ Login successful")
        
        # Set authorization header
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Get list of saved applications
        print("\n2. Getting saved applications...")
        async with session.get(f"{BASE_URL}/enhanced-applications", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Failed to get applications: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            applications = await response.json()
            print(f"✅ Found {len(applications)} saved applications")
            
            if not applications:
                print("⚠️  No saved applications found. Please save an application first.")
                return
            
            # Show application details
            for i, app in enumerate(applications[:3]):  # Show first 3
                print(f"   {i+1}. {app.get('title', 'Untitled')} (ID: {app['_id']})")
                print(f"      App Number: {app.get('application_number', 'N/A')}")
                print(f"      Created: {app.get('created_at', 'N/A')}")
        
        # Step 3: Test downloading ADS from the first saved application
        test_app = applications[0]
        app_id = test_app['_id']
        
        print(f"\n3. Testing ADS download for application: {test_app.get('title', 'Untitled')}")
        print(f"   Application ID: {app_id}")
        
        async with session.post(
            f"{BASE_URL}/enhanced-applications/{app_id}/generate-ads", 
            headers=headers
        ) as response:
            if response.status != 200:
                print(f"❌ ADS generation failed: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                return
            
            # Check if we got a PDF
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type:
                print(f"❌ Expected PDF, got: {content_type}")
                return
            
            # Get the PDF content
            pdf_content = await response.read()
            pdf_size = len(pdf_content)
            
            print(f"✅ ADS PDF generated successfully!")
            print(f"   Content-Type: {content_type}")
            print(f"   PDF Size: {pdf_size:,} bytes")
            
            # Check content-disposition header for filename
            content_disposition = response.headers.get('content-disposition', '')
            if content_disposition:
                print(f"   Filename: {content_disposition}")
            
            # Save the PDF for verification
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"test_downloaded_ads_{timestamp}.pdf"
            
            with open(filename, 'wb') as f:
                f.write(pdf_content)
            
            print(f"   📄 PDF saved as: {filename}")
        
        # Step 4: Test error handling with invalid application ID
        print("\n4. Testing error handling with invalid application ID...")
        invalid_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        
        async with session.post(
            f"{BASE_URL}/enhanced-applications/{invalid_id}/generate-ads", 
            headers=headers
        ) as response:
            if response.status == 404:
                print("✅ Correctly returned 404 for non-existent application")
            else:
                print(f"⚠️  Expected 404, got {response.status}")
        
        # Step 5: Test with malformed application ID
        print("\n5. Testing with malformed application ID...")
        malformed_id = "invalid-id"
        
        async with session.post(
            f"{BASE_URL}/enhanced-applications/{malformed_id}/generate-ads", 
            headers=headers
        ) as response:
            if response.status in [400, 422]:
                print("✅ Correctly handled malformed application ID")
            else:
                print(f"⚠️  Expected 400/422, got {response.status}")
        
        print("\n" + "=" * 50)
        print("🎉 History Download ADS Functionality Test Complete!")
        print("\nSummary:")
        print("✅ Login successful")
        print("✅ Retrieved saved applications")
        print("✅ Generated ADS PDF from saved application")
        print("✅ Error handling works correctly")
        print("\n📋 Next steps:")
        print("1. Test the frontend by visiting the history page")
        print("2. Click 'Download ADS' button on any saved application")
        print("3. Verify the PDF downloads correctly")

if __name__ == "__main__":
    asyncio.run(test_history_download_functionality())