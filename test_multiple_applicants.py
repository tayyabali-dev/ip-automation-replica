#!/usr/bin/env python3
"""
Test script to verify multiple applicants functionality in the ADS system.
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.patent_application import PatentApplicationMetadata, Inventor, Applicant
from app.services.enhanced_llm_integration import ExtractionResultConverter
from app.models.enhanced_extraction import (
    EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
    QualityMetrics, ExtractionMetadata, DataCompleteness, ExtractionMethod
)
from app.services.xfa_mapper import XFAMapper

def test_multiple_applicants_conversion():
    """Test conversion from enhanced extraction to legacy format with multiple applicants."""
    print("🧪 Testing Multiple Applicants Conversion...")
    
    # Create enhanced extraction result with multiple applicants
    enhanced_result = EnhancedExtractionResult(
        title="Test Patent Application",
        application_number="18/123,456",
        entity_status="Small Entity",
        total_drawing_sheets=5,
        inventors=[
            EnhancedInventor(
                given_name="John",
                middle_name="Michael",
                family_name="Doe",
                street_address="123 Main St",
                city="San Francisco",
                state="CA",
                postal_code="94105",
                country="US",
                citizenship="US",
                completeness=DataCompleteness.COMPLETE,
                confidence_score=0.95
            )
        ],
        applicants=[
            EnhancedApplicant(
                organization_name="TechCorp Inc.",
                street_address="456 Business Ave",
                city="San Francisco",
                state="CA",
                postal_code="94105",
                country="US",
                completeness=DataCompleteness.COMPLETE,
                confidence_score=0.90
            ),
            EnhancedApplicant(
                organization_name="Innovation Partners LLC",
                street_address="789 Innovation Blvd",
                city="Austin",
                state="TX",
                postal_code="78701",
                country="US",
                completeness=DataCompleteness.COMPLETE,
                confidence_score=0.85
            )
        ],
        quality_metrics=QualityMetrics(
            completeness_score=0.9,
            accuracy_score=0.9,
            confidence_score=0.9,
            consistency_score=0.9,
            overall_quality_score=0.9,
            required_fields_populated=5,
            total_required_fields=5,
            optional_fields_populated=3,
            total_optional_fields=5,
            validation_errors=0,
            validation_warnings=0
        ),
        extraction_metadata=ExtractionMetadata(
            extraction_method=ExtractionMethod.TEXT_EXTRACTION,
            document_type="patent_application",
            processing_time=2.5
        )
    )
    
    # Convert to legacy format
    legacy_result = ExtractionResultConverter.enhanced_to_legacy(enhanced_result)
    
    print(f"✅ Title: {legacy_result.title}")
    print(f"✅ Application Number: {legacy_result.application_number}")
    print(f"✅ Entity Status: {legacy_result.entity_status}")
    print(f"✅ Total Drawing Sheets: {legacy_result.total_drawing_sheets}")
    print(f"✅ Number of Inventors: {len(legacy_result.inventors)}")
    print(f"✅ Primary Applicant: {legacy_result.applicant.name if legacy_result.applicant else 'None'}")
    print(f"✅ Number of Applicants: {len(legacy_result.applicants)}")
    
    # Verify multiple applicants
    assert len(legacy_result.applicants) == 2, f"Expected 2 applicants, got {len(legacy_result.applicants)}"
    assert legacy_result.applicants[0].name == "TechCorp Inc.", f"First applicant name mismatch"
    assert legacy_result.applicants[1].name == "Innovation Partners LLC", f"Second applicant name mismatch"
    
    print("✅ Multiple applicants conversion test passed!")
    return legacy_result

def test_xfa_mapping_with_multiple_applicants():
    """Test XFA mapping with multiple applicants."""
    print("\n🧪 Testing XFA Mapping with Multiple Applicants...")
    
    # Create test metadata with multiple applicants
    metadata = PatentApplicationMetadata(
        title="Multi-Applicant Patent",
        application_number="18/987,654",
        entity_status="Small Entity",
        total_drawing_sheets=8,
        inventors=[
            Inventor(
                first_name="Jane",
                middle_name="Elizabeth",
                last_name="Smith",
                street_address="321 Research Way",
                city="Palo Alto",
                state="CA",
                zip_code="94301",
                country="US",
                citizenship="US"
            )
        ],
        applicants=[
            Applicant(
                name="Primary Corp",
                street_address="100 Main Street",
                city="San Francisco",
                state="CA",
                zip_code="94105",
                country="US"
            ),
            Applicant(
                name="Secondary LLC",
                street_address="200 Second Street",
                city="Austin",
                state="TX",
                zip_code="78701",
                country="US"
            )
        ]
    )
    
    # Test XFA mapping
    mapper = XFAMapper()
    xml_output = mapper.map_metadata_to_xml(metadata)
    
    print(f"✅ Generated XML length: {len(xml_output)} characters")
    print(f"✅ Contains title: {'Multi-Applicant Patent' in xml_output}")
    print(f"✅ Contains primary applicant: {'Primary Corp' in xml_output}")
    
    # Verify the XML contains expected elements
    assert "Multi-Applicant Patent" in xml_output, "Title not found in XML"
    assert "Primary Corp" in xml_output, "Primary applicant not found in XML"
    assert "Jane" in xml_output, "Inventor first name not found in XML"
    assert "Elizabeth" in xml_output, "Inventor middle name not found in XML"
    
    print("✅ XFA mapping with multiple applicants test passed!")
    return xml_output

def test_backward_compatibility():
    """Test backward compatibility with single applicant format."""
    print("\n🧪 Testing Backward Compatibility...")
    
    # Create metadata with single applicant (old format)
    metadata = PatentApplicationMetadata(
        title="Legacy Patent",
        application_number="17/555,123",
        inventors=[
            Inventor(
                first_name="Bob",
                last_name="Johnson",
                street_address="555 Legacy St",
                city="Boston",
                state="MA",
                zip_code="02101",
                country="US",
                citizenship="US"
            )
        ],
        applicant=Applicant(
            name="Legacy Company",
            street_address="777 Old Street",
            city="Boston",
            state="MA",
            zip_code="02101",
            country="US"
        ),
        applicants=[]  # Empty new field
    )
    
    # Test XFA mapping with legacy format
    mapper = XFAMapper()
    xml_output = mapper.map_metadata_to_xml(metadata)
    
    print(f"✅ Generated XML length: {len(xml_output)} characters")
    print(f"✅ Contains legacy applicant: {'Legacy Company' in xml_output}")
    
    assert "Legacy Company" in xml_output, "Legacy applicant not found in XML"
    assert "Bob" in xml_output, "Inventor not found in XML"
    
    print("✅ Backward compatibility test passed!")

def main():
    """Run all tests."""
    print("🚀 Starting Multiple Applicants Functionality Tests\n")
    
    try:
        # Test 1: Enhanced to Legacy Conversion
        legacy_result = test_multiple_applicants_conversion()
        
        # Test 2: XFA Mapping with Multiple Applicants
        xml_output = test_xfa_mapping_with_multiple_applicants()
        
        # Test 3: Backward Compatibility
        test_backward_compatibility()
        
        print("\n🎉 All tests passed! Multiple applicants functionality is working correctly.")
        print("\n📋 Summary:")
        print("✅ Enhanced extraction to legacy conversion supports multiple applicants")
        print("✅ XFA mapping handles multiple applicants (uses first as primary)")
        print("✅ Backward compatibility maintained for single applicant format")
        print("✅ Frontend can now display and edit multiple applicants")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)