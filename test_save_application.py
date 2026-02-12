#!/usr/bin/env python3
"""
Test script to verify the save enhanced application API endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@jwhd.com"
TEST_USER_PASSWORD = "test123"

def test_save_application_api():
    """Test the save enhanced application API endpoint"""
    
    print("🧪 Testing Save Enhanced Application API...")
    
    # Step 1: Login to get authentication token
    print("\n1. Authenticating...")
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
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
        
        # Step 2: Test saving an enhanced application
        print("\n2. Testing POST /save-enhanced-application...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create test application data
        test_application = {
            "title": "Test Application for History",
            "application_number": "TEST/123456",
            "filing_date": datetime.now().isoformat(),
            "entity_status": "Small Entity",
            "attorney_docket_number": "TEST-001",
            "confirmation_number": "1234",
            "application_type": "utility",
            "inventors": [
                {
                    "given_name": "John",
                    "middle_name": "A",
                    "family_name": "Doe",
                    "full_name": "John A Doe",
                    "street_address": "123 Test St",
                    "address_line_2": "",
                    "city": "Test City",
                    "state": "CA",
                    "postal_code": "12345",
                    "country": "US",
                    "citizenship": "US",
                    "sequence_number": 1,
                    "completeness": "complete",
                    "confidence_score": 0.95
                }
            ],
            "applicants": [
                {
                    "is_assignee": True,
                    "organization_name": "Test Company Inc",
                    "individual_given_name": "",
                    "individual_family_name": "",
                    "street_address": "456 Company Ave",
                    "address_line_2": "",
                    "city": "Test City",
                    "state": "CA",
                    "postal_code": "12345",
                    "country": "US",
                    "customer_number": "",
                    "email_address": "test@company.com",
                    "phone_number": "555-1234",
                    "relationship_to_inventors": "assignee",
                    "legal_entity_type": "corporation",
                    "completeness": "complete",
                    "confidence_score": 0.95
                }
            ],
            "correspondence_info": None,
            "attorney_agent_info": None,
            "domestic_priority_claims": [],
            "foreign_priority_claims": [],
            "classification_info": None,
            "quality_metrics": {
                "completeness_score": 0.95,
                "accuracy_score": 0.95,
                "confidence_score": 0.95,
                "consistency_score": 0.95,
                "overall_quality_score": 0.95,
                "required_fields_populated": 2,
                "total_required_fields": 2,
                "optional_fields_populated": 0,
                "total_optional_fields": 1,
                "validation_errors": 0,
                "validation_warnings": 0
            },
            "extraction_metadata": {
                "extraction_method": "text_extraction",
                "document_type": "application_data_sheet",
                "processing_time": 0,
                "llm_tokens_used": 0,
                "fallback_level_used": None,
                "manual_review_required": False,
                "extraction_notes": ["Test application for debugging"]
            },
            "manual_review_required": False,
            "extraction_warnings": [],
            "recommendations": [],
            "field_validations": [],
            "cross_field_validations": []
        }
        
        save_response = requests.post(
            f"{BASE_URL}/save-enhanced-application", 
            json=test_application,
            headers=headers
        )
        
        print(f"📤 Save request sent to: {BASE_URL}/save-enhanced-application")
        print(f"📊 Response status: {save_response.status_code}")
        print(f"📄 Response headers: {dict(save_response.headers)}")
        
        if save_response.status_code == 201:
            response_data = save_response.json()
            print("✅ Application saved successfully!")
            print(f"📋 Application ID: {response_data.get('application_id')}")
            print(f"📊 Quality Score: {response_data.get('quality_score')}")
            print(f"🔍 Manual Review Required: {response_data.get('manual_review_required')}")
            return True
        else:
            print(f"❌ Failed to save application: {save_response.status_code}")
            print(f"📄 Response: {save_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_save_application_api()
    if success:
        print("\n🎉 Save API test passed! The endpoint is working correctly.")
    else:
        print("\n💥 Save API test failed. There's an issue with the endpoint.")