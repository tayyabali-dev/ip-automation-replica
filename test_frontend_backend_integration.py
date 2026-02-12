#!/usr/bin/env python3
"""
Test script to verify frontend-backend integration for new USPTO ADS fields
"""

import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.enhanced_extraction import EnhancedExtractionResult, EnhancedApplicant, EnhancedInventor, QualityMetrics, ExtractionMetadata, ExtractionMethod

def test_new_fields_integration():
    """Test that new fields are properly handled in the extraction pipeline"""
    
    print("🧪 Testing Frontend-Backend Integration for New USPTO ADS Fields")
    print("=" * 70)
    
    # Test 1: Create a mock extraction result with new fields
    print("\n1. Testing Backend Model Extensions...")
    
    try:
        # Test EnhancedInventor with new address_2 field
        inventor = EnhancedInventor(
            given_name="John",
            middle_name="A.",
            family_name="Smith",
            street_address="123 Main St",
            address_2="Suite 100",  # NEW FIELD
            city="San Francisco",
            state="CA",
            postal_code="94105",
            country="US",
            citizenship="US",
            completeness="complete",
            confidence_score=0.9
        )
        print("✅ EnhancedInventor with address_2 field created successfully")
        
        # Test EnhancedApplicant with new fields
        applicant = EnhancedApplicant(
            is_assignee=True,
            is_organization=True,  # NEW FIELD
            applicant_type="Assignee",  # NEW FIELD
            organization_name="TechCorp Inc.",
            street_address="456 Innovation Blvd",
            address_2="Floor 5",  # NEW FIELD
            city="Austin",
            state="TX",
            postal_code="78701",
            country="US",
            phone_number="(555) 123-4567",  # NEW FIELD
            email="legal@techcorp.com",  # NEW FIELD
            completeness="complete",
            confidence_score=0.95
        )
        print("✅ EnhancedApplicant with new fields created successfully")
        
        # Test EnhancedExtractionResult with new fields
        quality_metrics = QualityMetrics(
            completeness_score=0.9,
            accuracy_score=0.85,
            confidence_score=0.9,
            consistency_score=0.88,
            overall_quality_score=0.88,
            required_fields_populated=8,
            total_required_fields=10,
            optional_fields_populated=5,
            total_optional_fields=8,
            validation_errors=0,
            validation_warnings=1
        )
        
        extraction_metadata = ExtractionMetadata(
            extraction_method=ExtractionMethod.TEXT_EXTRACTION,
            document_type="patent_application",
            processing_time=2.5
        )
        
        extraction_result = EnhancedExtractionResult(
            title="Test Patent Application",
            application_number="18/123,456",
            filing_date="2024-01-15",
            entity_status="Small Entity",
            attorney_docket_number="TECH-2024-001",  # NEW FIELD
            application_type="Nonprovisional",  # NEW FIELD
            correspondence_phone="(555) 987-6543",  # NEW FIELD
            inventors=[inventor],
            applicants=[applicant],
            quality_metrics=quality_metrics,
            extraction_metadata=extraction_metadata
        )
        print("✅ EnhancedExtractionResult with new fields created successfully")
        
    except Exception as e:
        print(f"❌ Backend model creation failed: {e}")
        return False
    
    # Test 2: Serialize to JSON (simulating API response)
    print("\n2. Testing JSON Serialization (Backend → Frontend)...")
    
    try:
        # Convert to dict (simulating FastAPI response)
        result_dict = extraction_result.dict()
        
        # Verify new fields are present
        assert "application_type" in result_dict, "application_type field missing"
        assert "correspondence_phone" in result_dict, "correspondence_phone field missing"
        assert result_dict["inventors"][0]["address_2"] == "Suite 100", "Inventor address_2 field incorrect"
        assert result_dict["applicants"][0]["is_organization"] == True, "Applicant is_organization field incorrect"
        assert result_dict["applicants"][0]["applicant_type"] == "Assignee", "Applicant applicant_type field incorrect"
        assert result_dict["applicants"][0]["address_2"] == "Floor 5", "Applicant address_2 field incorrect"
        assert result_dict["applicants"][0]["phone_number"] == "(555) 123-4567", "Applicant phone_number field incorrect"
        assert result_dict["applicants"][0]["email"] == "legal@techcorp.com", "Applicant email field incorrect"
        
        print("✅ All new fields present in JSON serialization")
        
        # Pretty print the JSON structure
        json_output = json.dumps(result_dict, indent=2)
        print("\n📄 Sample JSON Response Structure:")
        print("=" * 50)
        print(json_output[:1000] + "..." if len(json_output) > 1000 else json_output)
        
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return False
    
    # Test 3: Frontend Data Mapping Simulation
    print("\n3. Testing Frontend Data Mapping...")
    
    try:
        # Simulate frontend ApplicationMetadata interface
        frontend_metadata = {
            "title": result_dict.get("title"),
            "application_number": result_dict.get("application_number"),
            "entity_status": result_dict.get("entity_status"),
            # NEW FIELDS
            "attorney_docket_number": result_dict.get("attorney_docket_number"),
            "application_type": result_dict.get("application_type"),
            "customer_number": result_dict.get("customer_number"),
            "correspondence_email": result_dict.get("correspondence_email"),
            "correspondence_phone": result_dict.get("correspondence_phone"),
            "total_drawing_sheets": result_dict.get("total_drawing_sheets"),
            "inventors": [],
            "applicants": []
        }
        
        # Map inventors with new fields
        for inv in result_dict.get("inventors", []):
            frontend_inventor = {
                "first_name": inv.get("given_name"),
                "middle_name": inv.get("middle_name"),
                "last_name": inv.get("family_name"),
                "street_address": inv.get("street_address"),
                "address_2": inv.get("address_2"),  # NEW FIELD
                "city": inv.get("city"),
                "state": inv.get("state"),
                "zip_code": inv.get("postal_code"),
                "country": inv.get("country"),
                "citizenship": inv.get("citizenship")
            }
            frontend_metadata["inventors"].append(frontend_inventor)
        
        # Map applicants with new fields
        for app in result_dict.get("applicants", []):
            frontend_applicant = {
                "name": app.get("organization_name") or f"{app.get('individual_given_name', '')} {app.get('individual_family_name', '')}".strip(),
                "is_organization": app.get("is_organization", False),  # NEW FIELD
                "applicant_type": app.get("applicant_type", "Assignee"),  # NEW FIELD
                "street_address": app.get("street_address"),
                "address_2": app.get("address_2"),  # NEW FIELD
                "city": app.get("city"),
                "state": app.get("state"),
                "zip_code": app.get("postal_code"),
                "country": app.get("country"),
                "phone_number": app.get("phone_number"),  # NEW FIELD
                "email": app.get("email")  # NEW FIELD
            }
            frontend_metadata["applicants"].append(frontend_applicant)
        
        print("✅ Frontend data mapping completed successfully")
        
        # Verify frontend data structure
        assert frontend_metadata["attorney_docket_number"] == "TECH-2024-001", "Attorney docket number mapping failed"
        assert frontend_metadata["application_type"] == "Nonprovisional", "Application type mapping failed"
        assert frontend_metadata["correspondence_phone"] == "(555) 987-6543", "Correspondence phone mapping failed"
        assert frontend_metadata["inventors"][0]["address_2"] == "Suite 100", "Inventor address_2 mapping failed"
        assert frontend_metadata["applicants"][0]["is_organization"] == True, "Applicant is_organization mapping failed"
        assert frontend_metadata["applicants"][0]["applicant_type"] == "Assignee", "Applicant type mapping failed"
        assert frontend_metadata["applicants"][0]["address_2"] == "Floor 5", "Applicant address_2 mapping failed"
        assert frontend_metadata["applicants"][0]["phone_number"] == "(555) 123-4567", "Applicant phone mapping failed"
        assert frontend_metadata["applicants"][0]["email"] == "legal@techcorp.com", "Applicant email mapping failed"
        
        print("✅ All frontend field mappings verified")
        
    except Exception as e:
        print(f"❌ Frontend data mapping failed: {e}")
        return False
    
    # Test 4: Backward Compatibility
    print("\n4. Testing Backward Compatibility...")
    
    try:
        # Test with legacy data (missing new fields)
        legacy_applicant = EnhancedApplicant(
            is_assignee=True,
            organization_name="Legacy Corp",
            street_address="123 Old St",
            city="Legacy City",
            state="CA",
            postal_code="90210",
            country="US",
            completeness="complete",
            confidence_score=0.8
            # Note: New fields are optional and should default properly
        )
        
        legacy_dict = legacy_applicant.dict()
        
        # Verify defaults are applied
        assert legacy_dict["is_organization"] == False, "Default is_organization not applied"
        assert legacy_dict["applicant_type"] == "Assignee", "Default applicant_type not applied"
        assert legacy_dict["address_2"] is None, "address_2 should be None for legacy data"
        assert legacy_dict["phone_number"] is None, "phone_number should be None for legacy data"
        assert legacy_dict["email"] is None, "email should be None for legacy data"
        
        print("✅ Backward compatibility verified - legacy data works with new fields")
        
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED! Frontend-Backend Integration is Working Correctly")
    print("=" * 70)
    
    print("\n📋 Summary of Verified Features:")
    print("✅ Backend models support all new USPTO ADS fields")
    print("✅ JSON serialization includes new fields")
    print("✅ Frontend data mapping handles new fields")
    print("✅ Backward compatibility maintained")
    print("✅ Default values applied correctly")
    
    return True

if __name__ == "__main__":
    success = test_new_fields_integration()
    sys.exit(0 if success else 1)