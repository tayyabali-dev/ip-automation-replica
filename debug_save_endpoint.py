import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.models.enhanced_extraction import EnhancedExtractionResult
from backend.app.api.endpoints.enhanced_applications import save_enhanced_application
from backend.app.db.mongodb import get_database
from backend.app.models.user import UserResponse

async def debug_save_endpoint():
    """Debug the save endpoint by calling it directly"""
    print("🔍 Debugging Save Endpoint...")
    
    try:
        # Create test data that matches the EnhancedExtractionResult model
        test_data = {
            "title": "Test Application",
            "application_number": "16/123456",
            "filing_date": "2024-01-15",
            "attorney_docket_number": "TEST-001",
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
                "document_type": "patent_application",
                "processing_time": 5.2
            },
            "manual_review_required": False,
            "extraction_warnings": [],
            "recommendations": [],
            "field_validations": [],
            "cross_field_validations": []
        }
        
        print("✅ Test data created")
        
        # Try to create EnhancedExtractionResult from the data
        try:
            extraction_result = EnhancedExtractionResult(**test_data)
            print("✅ EnhancedExtractionResult model created successfully")
        except Exception as e:
            print(f"❌ Failed to create EnhancedExtractionResult: {e}")
            print(f"Error type: {type(e)}")
            return
        
        # Create mock user
        mock_user = UserResponse(
            id="69820bd842b96a7f9e32a9d3",
            email="test@jwhd.com",
            full_name="Test User"
        )
        print("✅ Mock user created")
        
        # Get database connection
        try:
            db = await get_database()
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return
        
        # Try to save the application
        try:
            result = await save_enhanced_application(
                data=extraction_result,
                current_user=mock_user,
                db=db
            )
            print(f"✅ Application saved successfully: {result}")
            
        except Exception as e:
            print(f"❌ Failed to save application: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_save_endpoint())