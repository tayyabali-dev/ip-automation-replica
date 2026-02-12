import requests
import json

def test_minimal_save():
    """Test the save API endpoint with absolute minimal data"""
    print("🧪 Testing Save API with absolute minimal data...")
    
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
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Absolute minimal test data - just required fields
        test_data = {
            "inventors": [
                {
                    "completeness": "complete",
                    "confidence_score": 0.9
                }
            ],
            "applicants": [],
            "domestic_priority_claims": [],
            "foreign_priority_claims": [],
            "quality_metrics": {
                "overall_quality_score": 0.85,
                "completeness_score": 0.90,
                "accuracy_score": 0.80,
                "confidence_score": 0.85,
                "consistency_score": 0.90,
                "required_fields_populated": 1,
                "total_required_fields": 1,
                "optional_fields_populated": 0,
                "total_optional_fields": 1,
                "validation_errors": 0,
                "validation_warnings": 0
            },
            "extraction_metadata": {
                "extraction_method": "text_extraction",
                "document_type": "application_data_sheet",
                "processing_time": 1.0
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
        else:
            print(f"❌ Failed to save application: {save_response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_minimal_save()