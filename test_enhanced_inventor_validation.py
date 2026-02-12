#!/usr/bin/env python3
"""
Test script to verify enhanced inventor count validation with specific add/remove messages.
"""

import requests
import json

# Test data - Base case with 2 inventors
base_metadata = {
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
    "original_inventor_count": 2
}

# Test case 1: Inventor added (2 -> 3)
test_inventor_added = {
    **base_metadata,
    "inventors": [
        *base_metadata["inventors"],
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "street_address": "789 New St",
            "city": "Newtown",
            "state": "FL",
            "zip_code": "33101",
            "country": "US",
            "citizenship": "US"
        }
    ]
}

# Test case 2: Inventor removed (2 -> 1)
test_inventor_removed = {
    **base_metadata,
    "inventors": [base_metadata["inventors"][0]]  # Only keep first inventor
}

def test_enhanced_validation():
    """Test the enhanced inventor count validation messages"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Enhanced Inventor Count Validation")
    print("=" * 60)
    
    # Test 1: Valid case (no change)
    print("\n1️⃣ Testing VALID case (no change in inventor count)...")
    print(f"   Original count: {base_metadata['original_inventor_count']}")
    print(f"   Current count: {len(base_metadata['inventors'])}")
    
    try:
        response = requests.post(
            f"{base_url}/applications/generate-ads",
            json=base_metadata,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✅ SUCCESS: PDF generation allowed (as expected)")
        else:
            print(f"   ❌ UNEXPECTED: Got status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠️  Backend server not running. Please start with:")
        print("      cd backend && python -m uvicorn app.main:app --reload --port 8000")
        return
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Inventor added (2 -> 3)
    print("\n2️⃣ Testing INVENTOR ADDED case (2 -> 3)...")
    print(f"   Original count: {test_inventor_added['original_inventor_count']}")
    print(f"   Current count: {len(test_inventor_added['inventors'])}")
    
    try:
        response = requests.post(
            f"{base_url}/applications/generate-ads",
            json=test_inventor_added,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            # HTTP 400 with error details
            response_data = response.json()
            print("   ✅ SUCCESS: Validation blocked PDF generation (HTTP 400)")
            
            # The message field contains the error object
            error_obj = response_data.get('message', {})
            if isinstance(error_obj, dict):
                message = error_obj.get('message', '')
                action = error_obj.get('action', '')
                difference = error_obj.get('difference', 0)
            else:
                message = str(error_obj)
                action = ''
                difference = 0
                
            print(f"   📝 Message: {message}")
            print(f"   📝 Action: {action}")
            print(f"   📝 Difference: {difference}")
            
            # Check if message indicates addition
            if 'added' in message or 'have been added' in message or action == 'added':
                print("   ✅ SUCCESS: Message correctly indicates inventors were ADDED")
            else:
                print("   ❌ ISSUE: Message doesn't clearly indicate addition")
                
        elif response.status_code == 200:
            # HTTP 200 with error details in response body
            response_data = response.json()
            if (response_data.get('success') == False and
                response_data.get('generation_blocked') == True):
                print("   ✅ SUCCESS: Validation blocked PDF generation (HTTP 200)")
                message = response_data.get('message', '')
                print(f"   📝 Message: {message}")
                
                # Check if message indicates addition
                if 'added' in message or 'have been added' in message:
                    print("   ✅ SUCCESS: Message correctly indicates inventors were ADDED")
                else:
                    print("   ❌ ISSUE: Message doesn't clearly indicate addition")
            else:
                print("   ❌ FAILED: Expected blocked generation")
        else:
            print(f"   ❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Inventor removed (2 -> 1)
    print("\n3️⃣ Testing INVENTOR REMOVED case (2 -> 1)...")
    print(f"   Original count: {test_inventor_removed['original_inventor_count']}")
    print(f"   Current count: {len(test_inventor_removed['inventors'])}")
    
    try:
        response = requests.post(
            f"{base_url}/applications/generate-ads",
            json=test_inventor_removed,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            # HTTP 400 with error details
            response_data = response.json()
            print("   ✅ SUCCESS: Validation blocked PDF generation (HTTP 400)")
            
            # The message field contains the error object
            error_obj = response_data.get('message', {})
            if isinstance(error_obj, dict):
                message = error_obj.get('message', '')
                action = error_obj.get('action', '')
                difference = error_obj.get('difference', 0)
            else:
                message = str(error_obj)
                action = ''
                difference = 0
                
            print(f"   📝 Message: {message}")
            print(f"   📝 Action: {action}")
            print(f"   📝 Difference: {difference}")
            
            # Check if message indicates removal
            if 'removed' in message or 'have been removed' in message or action == 'removed':
                print("   ✅ SUCCESS: Message correctly indicates inventors were REMOVED")
            else:
                print("   ❌ ISSUE: Message doesn't clearly indicate removal")
                
        elif response.status_code == 200:
            # HTTP 200 with error details in response body
            response_data = response.json()
            if (response_data.get('success') == False and
                response_data.get('generation_blocked') == True):
                print("   ✅ SUCCESS: Validation blocked PDF generation (HTTP 200)")
                message = response_data.get('message', '')
                print(f"   📝 Message: {message}")
                
                # Check if message indicates removal
                if 'removed' in message or 'have been removed' in message:
                    print("   ✅ SUCCESS: Message correctly indicates inventors were REMOVED")
                else:
                    print("   ❌ ISSUE: Message doesn't clearly indicate removal")
            else:
                print("   ❌ FAILED: Expected blocked generation")
        else:
            print(f"   ❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Enhanced validation test completed!")
    print("\n📋 Expected Messages:")
    print("   Added: '1 inventor(s) have been added. Re-extraction from the source document is required.'")
    print("   Removed: '1 inventor(s) have been removed. Re-extraction from the source document is required.'")

if __name__ == "__main__":
    test_enhanced_validation()