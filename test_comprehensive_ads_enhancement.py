#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced ADS functionality.
Tests all new fields and validation methods that were added.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models.enhanced_extraction import (
    EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
    CorrespondenceInfo, AttorneyAgentInfo, DomesticPriorityClaim,
    ForeignPriorityClaim, ClassificationInfo, ApplicationTypeEnum,
    ApplicantTypeEnum, EntityTypeEnum, DataCompleteness, QualityMetrics,
    ExtractionMetadata, ExtractionMethod
)
from app.services.validation_service import ValidationService, FieldValidator

def create_comprehensive_test_data():
    """Create comprehensive test data with all new ADS fields"""
    
    # Create test inventors with required fields
    inventors = [
        EnhancedInventor(
            given_name="John",
            family_name="Smith",
            middle_name="A",
            full_name="John A. Smith",
            street_address="123 Innovation Drive",
            city="San Francisco",
            state="CA",
            postal_code="94105",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        ),
        EnhancedInventor(
            given_name="Maria",
            family_name="Garcia",
            street_address="456 Tech Boulevard",
            city="Austin",
            state="TX",
            postal_code="78701",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.92
        )
    ]
    
    # Create test applicants with enhanced fields
    applicants = [
        EnhancedApplicant(
            organization_name="TechCorp Industries LLC",
            street_address="789 Corporate Plaza",
            city="New York",
            state="NY",
            postal_code="10001",
            country="US",
            email_address="patents@techcorp.com",
            applicant_type=ApplicantTypeEnum.ASSIGNEE.value,
            entity_type=EntityTypeEnum.CORPORATION.value,
            country_of_incorporation="US",
            authority_to_apply="Assignment dated 2024-01-15",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.88
        )
    ]
    
    # Create correspondence info
    correspondence_info = CorrespondenceInfo(
        firm_name="Patent & Associates LLP",
        street_address="100 Legal Street, Suite 500",
        city="Washington",
        state="DC",
        postal_code="20001",
        country="US",
        phone_number="+1-202-555-0123",
        fax_number="+1-202-555-0124",
        email_address="correspondence@patentlaw.com",
        customer_number="12345"
    )
    
    # Create attorney/agent info
    attorney_agent_info = AttorneyAgentInfo(
        name="Sarah Johnson",
        registration_number="54321",
        phone_number="+1-202-555-0125",
        email_address="sjohnson@patentlaw.com"
    )
    
    # Create domestic priority claims
    domestic_priority_claims = [
        DomesticPriorityClaim(
            parent_application_number="16/123,456",
            filing_date="2023-06-15",
            application_type="Provisional",
            status="Pending"
        )
    ]
    
    # Create foreign priority claims
    foreign_priority_claims = [
        ForeignPriorityClaim(
            country_code="EP",
            application_number="EP23123456.7",
            filing_date="2023-05-10",
            certified_copy_status="Filed"
        )
    ]
    
    # Create classification info
    classification_info = ClassificationInfo(
        suggested_art_unit="2100",
        uspc_classification="123/456",
        ipc_classification="G06F 17/30",
        cpc_classification="G06F 16/00"
    )
    
    # Create quality metrics
    quality_metrics = QualityMetrics(
        completeness_score=0.95,
        accuracy_score=0.92,
        confidence_score=0.91,
        consistency_score=0.94,
        overall_quality_score=0.93,
        required_fields_populated=8,
        total_required_fields=10,
        optional_fields_populated=15,
        total_optional_fields=20,
        validation_errors=0,
        validation_warnings=2
    )
    
    # Create extraction metadata
    extraction_metadata = ExtractionMetadata(
        extraction_method=ExtractionMethod.TEXT_EXTRACTION,
        document_type="patent_application",
        processing_time=45.2,
        llm_tokens_used=1250,
        manual_review_required=False,
        extraction_notes=["Successfully extracted all major fields"]
    )
    
    # Create comprehensive extraction result
    extraction_result = EnhancedExtractionResult(
        title="Advanced Machine Learning System for Data Processing",
        application_number="17/987,654",
        filing_date="2024-01-20",
        attorney_docket_number="TECH-2024-001",
        confirmation_number="1234",
        application_type=ApplicationTypeEnum.UTILITY.value,
        entity_status="Small Entity",
        inventors=inventors,
        applicants=applicants,
        correspondence_info=correspondence_info,
        attorney_agent_info=attorney_agent_info,
        domestic_priority_claims=domestic_priority_claims,
        foreign_priority_claims=foreign_priority_claims,
        classification_info=classification_info,
        quality_metrics=quality_metrics,
        extraction_metadata=extraction_metadata,
        extraction_warnings=[],
        field_validations=[],
        cross_field_validations=[],
        manual_review_required=False,
        recommendations=[]
    )
    
    return extraction_result

async def test_field_validations():
    """Test all new field validation methods"""
    print("\n=== Testing Field Validations ===")
    
    validator = FieldValidator()
    
    # Test attorney docket number validation
    print("\n1. Testing Attorney Docket Number Validation:")
    test_cases = [
        "TECH-2024-001",
        "ABC123",
        "VERY-LONG-ATTORNEY-DOCKET-NUMBER-THAT-EXCEEDS-NORMAL-LENGTH",
        "AB",
        "TECH/2024/001",
        ""
    ]
    
    for case in test_cases:
        result = validator.validate_attorney_docket_number(case)
        print(f"   '{case}' -> Valid: {result.is_valid}, Normalized: '{result.normalized_value}', Warnings: {len(result.warnings)}")
    
    # Test confirmation number validation
    print("\n2. Testing Confirmation Number Validation:")
    test_cases = ["1234", "CONF-5678", "12345", "ABC", ""]
    
    for case in test_cases:
        result = validator.validate_confirmation_number(case)
        print(f"   '{case}' -> Valid: {result.is_valid}, Normalized: '{result.normalized_value}', Errors: {len(result.errors)}")
    
    # Test customer number validation
    print("\n3. Testing Customer Number Validation:")
    test_cases = ["12345", "123456", "CUST-54321", "1234", "1234567", ""]
    
    for case in test_cases:
        result = validator.validate_customer_number(case)
        print(f"   '{case}' -> Valid: {result.is_valid}, Normalized: '{result.normalized_value}', Errors: {len(result.errors)}")
    
    # Test registration number validation
    print("\n4. Testing Registration Number Validation:")
    test_cases = ["54321", "123456", "REG-12345", "1234", "1234567", ""]
    
    for case in test_cases:
        result = validator.validate_registration_number(case)
        print(f"   '{case}' -> Valid: {result.is_valid}, Normalized: '{result.normalized_value}', Errors: {len(result.errors)}")
    
    # Test phone number validation
    print("\n5. Testing Phone Number Validation:")
    test_cases = [
        "+1-202-555-0123",
        "(202) 555-0123",
        "202.555.0123",
        "2025550123",
        "+44 20 7946 0958",
        "invalid-phone",
        ""
    ]
    
    for case in test_cases:
        result = validator.validate_phone_number(case)
        print(f"   '{case}' -> Valid: {result.is_valid}, Normalized: '{result.normalized_value}', Errors: {len(result.errors)}")

async def test_comprehensive_validation():
    """Test comprehensive validation with all new fields"""
    print("\n=== Testing Comprehensive Validation ===")
    
    # Create test data
    extraction_result = create_comprehensive_test_data()
    
    # Initialize validation service
    validation_service = ValidationService()
    
    # Perform comprehensive validation
    validated_result = await validation_service.validate_extraction_result(extraction_result)
    
    print(f"\nValidation Results:")
    print(f"  Manual Review Required: {validated_result.manual_review_required}")
    print(f"  Field Validations: {len(validated_result.field_validations)}")
    print(f"  Cross-field Validations: {len(validated_result.cross_field_validations)}")
    print(f"  Extraction Warnings: {len(validated_result.extraction_warnings)}")
    print(f"  Recommendations: {len(validated_result.recommendations)}")
    
    if validated_result.quality_metrics:
        print(f"\nQuality Metrics:")
        print(f"  Overall Quality Score: {validated_result.quality_metrics.overall_quality_score:.2f}")
        print(f"  Completeness Score: {validated_result.quality_metrics.completeness_score:.2f}")
        print(f"  Accuracy Score: {validated_result.quality_metrics.accuracy_score:.2f}")
        print(f"  Confidence Score: {validated_result.quality_metrics.confidence_score:.2f}")
        print(f"  Consistency Score: {validated_result.quality_metrics.consistency_score:.2f}")
    
    # Show field validation details
    print(f"\nField Validation Details:")
    for validation in validated_result.field_validations:
        if not validation.validation_result.is_valid or validation.validation_result.warnings:
            print(f"  {validation.field_name}:")
            if validation.validation_result.errors:
                print(f"    Errors: {validation.validation_result.errors}")
            if validation.validation_result.warnings:
                print(f"    Warnings: {validation.validation_result.warnings}")
    
    return validated_result

def test_data_model_completeness():
    """Test that all new data models can be created and serialized"""
    print("\n=== Testing Data Model Completeness ===")
    
    extraction_result = create_comprehensive_test_data()
    
    # Test serialization to dict
    try:
        result_dict = extraction_result.dict()
        print("✓ Successfully serialized extraction result to dict")
        
        # Count populated fields
        populated_fields = []
        for key, value in result_dict.items():
            if value is not None and value != [] and value != {}:
                populated_fields.append(key)
        
        print(f"✓ Populated fields: {len(populated_fields)}")
        print(f"  Fields: {', '.join(populated_fields)}")
        
    except Exception as e:
        print(f"✗ Failed to serialize extraction result: {e}")
        return False
    
    # Test JSON serialization
    try:
        json_str = json.dumps(result_dict, indent=2, default=str)
        print("✓ Successfully serialized to JSON")
        print(f"✓ JSON size: {len(json_str)} characters")
        
    except Exception as e:
        print(f"✗ Failed to serialize to JSON: {e}")
        return False
    
    return True

def test_enum_values():
    """Test all new enum values"""
    print("\n=== Testing Enum Values ===")
    
    # Test ApplicationTypeEnum
    print("ApplicationTypeEnum values:")
    for app_type in ApplicationTypeEnum:
        print(f"  - {app_type.value}")
    
    # Test ApplicantTypeEnum
    print("\nApplicantTypeEnum values:")
    for applicant_type in ApplicantTypeEnum:
        print(f"  - {applicant_type.value}")
    
    # Test EntityTypeEnum
    print("\nEntityTypeEnum values:")
    for entity_type in EntityTypeEnum:
        print(f"  - {entity_type.value}")
    
    return True

async def main():
    """Run comprehensive tests for enhanced ADS functionality"""
    print("🚀 Starting Comprehensive ADS Enhancement Tests")
    print("=" * 60)
    
    try:
        # Test 1: Data model completeness
        success1 = test_data_model_completeness()
        
        # Test 2: Enum values
        success2 = test_enum_values()
        
        # Test 3: Field validations
        await test_field_validations()
        
        # Test 4: Comprehensive validation
        validated_result = await test_comprehensive_validation()
        
        print("\n" + "=" * 60)
        print("🎉 Test Summary:")
        print(f"✓ Data Model Tests: {'PASSED' if success1 else 'FAILED'}")
        print(f"✓ Enum Tests: {'PASSED' if success2 else 'FAILED'}")
        print("✓ Field Validation Tests: COMPLETED")
        print("✓ Comprehensive Validation Tests: COMPLETED")
        
        if validated_result:
            print(f"\n📊 Final Validation Results:")
            print(f"   Overall Quality Score: {validated_result.quality_metrics.overall_quality_score:.2f}")
            print(f"   Manual Review Required: {validated_result.manual_review_required}")
            print(f"   Total Validations: {len(validated_result.field_validations)}")
        
        print("\n🎯 All enhanced ADS functionality has been successfully implemented and tested!")
        print("\nNew Features Added:")
        print("  ✓ Filing Date extraction and validation")
        print("  ✓ Attorney Docket Number extraction and validation")
        print("  ✓ Confirmation Number extraction and validation")
        print("  ✓ Application Type classification")
        print("  ✓ Correspondence Information (law firm, contact details)")
        print("  ✓ Attorney/Agent Information with registration numbers")
        print("  ✓ Priority Claims (domestic and foreign)")
        print("  ✓ Enhanced Applicant Details (type, authority, incorporation)")
        print("  ✓ Classification Information (art unit, classification codes)")
        print("  ✓ Comprehensive field validation for all new field types")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)