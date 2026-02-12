import requests
import json

def test_save_api():
    """Test the save API endpoint with correct data format"""
    print("🧪 Testing Save Enhanced Application API with correct format...")
    
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
            print(f"Response: {login_response.text}")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test data with correct format
        test_data = {
            "title": "Test Application",
            "application_number": "16/123456",
            "filing_date": "2024-01-15",
            "entity_status": "large",
            "inventors": [
                {
                    "given_name": "John",
                    "family_name": "Doe",
                    "full_name": "John Doe",
                    "city": "New York",
                    "state": "NY",
                    "country": "US",
                    "citizenship": "US",
                    "street_address": "123 Main St",
                    "postal_code": "10001",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "applicants": [
                {
                    "organization_name": "Test Company Inc.",
                    "street_address": "456 Business Ave",
                    "city": "New York",
                    "state": "NY", 
                    "postal_code": "10002",
                    "country": "US",
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "domestic_priority_claims": [],
            "foreign_priority_claims": [],
            "quality_metrics": {
                "overall_quality_score": 0.85,
                "completeness_score": 0.90,
                "accuracy_score": 0.80,
                "confidence_score": 0.85,
                "consistency_score": 0.90,
                "required_fields_populated": 8,
                "total_required_fields": 10,
                "optional_fields_populated": 5,
                "total_optional_fields": 8,
                "validation_errors": 0,
                "validation_warnings": 1
            },
            "extraction_metadata": {
                "extraction_method": "text_extraction",
                "document_type": "application_data_sheet",
                "processing_time": 5.2
            },
            "manual_review_required": False,
            "extraction_warnings": [],
            "recommendations": [],
            "field_validations": [],
            "cross_field_validations": []
        }
        
        print("2. Testing POST /save-enhanced-application...")
        save_response = requests.post(
            "http://localhost:8000/api/v1/save-enhanced-application",
            json=test_data,
            headers=headers
        )
        
        print(f"📊 Response status: {save_response.status_code}")
        print(f"📄 Response: {save_response.text}")
        
        if save_response.status_code == 201:
            print("✅ Application saved successfully!")
            response_data = save_response.json()
            print(f"📋 Application ID: {response_data.get('application_id')}")
            print(f"📊 Quality Score: {response_data.get('quality_score')}")
        else:
            print(f"❌ Failed to save application: {save_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_save_api()