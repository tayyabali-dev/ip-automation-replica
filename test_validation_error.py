import requests
import json

def test_validation_error():
    """Test to see the exact validation error"""
    print("🧪 Testing Save API to see validation errors...")
    
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
        
        # Test with empty object to see what fields are required
        print("2. Testing with empty object...")
        empty_response = requests.post(
            "http://localhost:8000/api/v1/save-enhanced-application",
            json={},
            headers=headers
        )
        
        print(f"📊 Empty object response status: {empty_response.status_code}")
        print(f"📄 Empty object response: {empty_response.text}")
        
        # Test with just the required fields we know about
        print("3. Testing with minimal required fields...")
        minimal_data = {
            "inventors": [],
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
        
        minimal_response = requests.post(
            "http://localhost:8000/api/v1/save-enhanced-application",
            json=minimal_data,
            headers=headers
        )
        
        print(f"📊 Minimal data response status: {minimal_response.status_code}")
        print(f"📄 Minimal data response: {minimal_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_validation_error()