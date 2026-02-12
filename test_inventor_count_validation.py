#!/usr/bin/env python3
"""
Test script to verify inventor count validation works correctly.
This simulates the frontend sending metadata with different inventor counts.
"""

import requests
import json

# Test data with original inventor count
test_metadata_valid = {
    "title": "Test Patent Application",
    "application_number": "18/123,456",
    "entity_status": "Small Entity",
    "inventors": [
        {
            "first_name": "John",
            "last_name": "Doe",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "country": "US",
            "citizenship": "US"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "street_address": "456 Oak Ave",
            "city": "Somewhere",
            "state": "NY",
            "zip_code": "67890",
            "country": "US",
            "citizenship": "US"
        }
    ],
    "applicants": [
        {
            "name": "Test Company LLC",
            "street_address": "789 Business Blvd",
            "city": "Corporate",
            "state": "TX",
            "zip_code": "54321",
            "country": "US"
        }
    ],
    "total_drawing_sheets": 5,
    "original_inventor_count": 2  # This matches the actual inventor count
}

# Test data with mismatched inventor count (should trigger validation error)
test_metadata_invalid = {
    **test_metadata_valid,
    "inventors": [
        # Only one inventor, but original_inventor_count is 2
        {
            "first_name": "John",
            "last_name": "Doe",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345",
            "country": "US",
            "citizenship": "US"
        }
    ],
    "original_inventor_count": 2  # Original had 2, but now we only have 1
}

def test_validation():
    """Test the inventor count validation"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Inventor Count Validation")
    print("=" * 50)
    
    # Test 1: Valid case (inventor count matches)
    print("\n1️⃣ Testing VALID case (inventor count matches original)...")
    print(f"   Original count: {test_metadata_valid['original_inventor_count']}")
    print(f"   Current count: {len(test_metadata_valid['inventors'])}")
    
    try:
        response = requests.post(
            f"{base_url}/applications/generate-ads",
            json=test_metadata_valid,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: PDF generation allowed (as expected)")
        else:
            print(f"   ❌ UNEXPECTED: Got status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Backend server not running. Please start with:")
        print("      cd backend && python -m uvicorn app.main:app --reload --port 8000")
        return
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Invalid case (inventor count mismatch)
    print("\n2️⃣ Testing INVALID case (inventor count changed)...")
    print(f"   Original count: {test_metadata_invalid['original_inventor_count']}")
    print(f"   Current count: {len(test_metadata_invalid['inventors'])}")
    
    try:
        response = requests.post(
            f"{base_url}/applications/generate-ads",
            json=test_metadata_invalid,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("   ✅ SUCCESS: Validation blocked PDF generation with HTTP 400 (as expected)")
            try:
                error_data = response.json()
                detail = error_data.get('detail', {})
                if detail.get('error') == 'inventor_count_changed':
                    print(f"   📝 Error message: {detail.get('message')}")
                else:
                    print(f"   📝 Response: {error_data}")
            except:
                print(f"   📝 Response: {response.text}")
        elif response.status_code == 200:
            # Check if it's a successful block with error details
            try:
                response_data = response.json()
                if (response_data.get('success') == False and
                    response_data.get('generation_blocked') == True and
                    'inventor_count_changed' in response_data.get('message', '')):
                    print("   ✅ SUCCESS: Validation blocked PDF generation with HTTP 200 + error details (working correctly)")
                    print(f"   📝 PDF Generated: {response_data.get('pdf_generated')}")
                    print(f"   📝 Generation Blocked: {response_data.get('generation_blocked')}")
                    # Extract clean error message
                    message = response_data.get('message', '')
                    if 'ADS generation failed: 400:' in message:
                        try:
                            error_part = message.split('ADS generation failed: 400: ')[1]
                            error_obj = eval(error_part)  # Safe since we control the format
                            clean_message = error_obj.get('message', message)
                            print(f"   📝 Error message: {clean_message}")
                        except:
                            print(f"   📝 Raw message: {message}")
                    else:
                        print(f"   📝 Message: {message}")
                else:
                    print(f"   ❌ UNEXPECTED: Got 200 but validation didn't work properly")
                    print(f"   Response: {response.text}")
            except:
                print(f"   ❌ UNEXPECTED: Got 200 but couldn't parse response")
                print(f"   Response: {response.text}")
        else:
            print(f"   ❌ FAILED: Expected 400 or 200 with error details, got {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_validation()