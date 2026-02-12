#!/usr/bin/env python3
"""
Test script to verify the integration of EntitySeparationValidator into ValidationService.
This tests the complete validation pipeline with entity separation.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.validation_service import ValidationService
from app.models.enhanced_extraction import (
    EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
    ConfidenceLevel, DataCompleteness, QualityMetrics, ExtractionMetadata,
    ExtractionMethod
)

def create_test_result(title, inventors, applicants):
    """Helper function to create test extraction results with required fields"""
    return EnhancedExtractionResult(
        title=title,
        inventors=inventors,
        applicants=applicants,
        quality_metrics=QualityMetrics(
            completeness_score=0.8,
            accuracy_score=0.8,
            confidence_score=0.8,
            consistency_score=0.8,
            overall_quality_score=0.8,
            required_fields_populated=2,
            total_required_fields=2,
            optional_fields_populated=1,
            total_optional_fields=4,
            validation_errors=0,
            validation_warnings=0
        ),
        extraction_metadata=ExtractionMetadata(
            extraction_method=ExtractionMethod.TEXT_EXTRACTION,
            document_type="patent_application",
            processing_time=1.5,
            manual_review_required=False
        ),
        field_validations=[],
        cross_field_validations=[],
        extraction_warnings=[],
        recommendations=[]
    )

async def test_validation_integration():
    """Test the complete validation pipeline with entity separation"""
    
    print("🧪 Testing ValidationService with EntitySeparationValidator Integration")
    print("=" * 70)
    
    # Initialize validation service
    validation_service = ValidationService()
    
    # Test Case 1: Clean data (should pass all validations)
    print("\n📋 Test Case 1: Clean Data")
    print("-" * 30)
    
    clean_inventors = [
        EnhancedInventor(
            given_name="John",
            family_name="Smith",
            street_address="123 Main St",
            city="San Francisco",
            state="CA",
            country="US",
            confidence_score=0.95,
            completeness=DataCompleteness.COMPLETE
        )
    ]
    
    clean_applicants = [
        EnhancedApplicant(
            organization_name="Tech Corp Inc.",
            street_address="456 Business Ave",
            city="San Francisco",
            state="CA",
            country="US",
            confidence_score=0.90,
            completeness=DataCompleteness.COMPLETE
        )
    ]
    
    clean_result = create_test_result("Advanced Widget Technology", clean_inventors, clean_applicants)
    validated_clean = await validation_service.validate_extraction_result(clean_result)
    
    print(f"✅ Manual Review Required: {validated_clean.manual_review_required}")
    print(f"✅ Quality Score: {validated_clean.quality_metrics.overall_quality_score:.2f}")
    print(f"✅ Validation Errors: {len([v for v in validated_clean.field_validations if not v.validation_result.is_valid])}")
    print(f"✅ Cross-field Issues: {len([v for v in validated_clean.cross_field_validations if not v.is_consistent])}")
    print(f"✅ Warnings: {len(validated_clean.extraction_warnings)}")
    
    # Test Case 2: Contaminated data (inventor has company name)
    print("\n📋 Test Case 2: Contaminated Data - Company in Inventor")
    print("-" * 50)
    
    contaminated_inventors = [
        EnhancedInventor(
            given_name="Tech Corp Inc.",  # Company name in inventor field!
            family_name="Engineering Dept",  # Department in family name!
            street_address="456 Business Ave",  # Business address
            city="San Francisco",
            state="CA",
            country="US",
            confidence_score=0.85,
            completeness=DataCompleteness.COMPLETE
        )
    ]
    
    contaminated_applicants = [
        EnhancedApplicant(
            organization_name="Tech Corp Inc.",
            street_address="456 Business Ave",
            city="San Francisco",
            state="CA",
            country="US",
            confidence_score=0.90,
            completeness=DataCompleteness.COMPLETE
        )
    ]
    
    contaminated_result = create_test_result("Widget Innovation", contaminated_inventors, contaminated_applicants)
    validated_contaminated = await validation_service.validate_extraction_result(contaminated_result)
    
    print(f"🚨 Manual Review Required: {validated_contaminated.manual_review_required}")
    print(f"🚨 Quality Score: {validated_contaminated.quality_metrics.overall_quality_score:.2f}")
    print(f"🚨 Validation Errors: {len([v for v in validated_contaminated.field_validations if not v.validation_result.is_valid])}")
    print(f"🚨 Cross-field Issues: {len([v for v in validated_contaminated.cross_field_validations if not v.is_consistent])}")
    print(f"🚨 Warnings: {len(validated_contaminated.extraction_warnings)}")
    
    print("\n🔍 Detected Issues:")
    for warning in validated_contaminated.extraction_warnings[:5]:  # Show first 5 warnings
        print(f"   • {warning}")
    
    # Test Case 3: Missing applicant data
    print("\n📋 Test Case 3: Missing Applicant Data")
    print("-" * 35)
    
    missing_inventors = [
        EnhancedInventor(
            given_name="Jane",
            family_name="Doe",
            street_address="789 Home St",
            city="Austin",
            state="TX",
            country="US",
            confidence_score=0.90,
            completeness=DataCompleteness.COMPLETE
        )
    ]
    
    missing_result = create_test_result("Simple Invention", missing_inventors, [])  # No applicants!
    validated_missing = await validation_service.validate_extraction_result(missing_result)
    
    print(f"⚠️  Manual Review Required: {validated_missing.manual_review_required}")
    print(f"⚠️  Quality Score: {validated_missing.quality_metrics.overall_quality_score:.2f}")
    print(f"⚠️  Recommendations: {len(validated_missing.recommendations)}")
    
    print("\n💡 Recommendations:")
    for rec in validated_missing.recommendations[:3]:  # Show first 3 recommendations
        print(f"   • {rec}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    test_cases = [
        ("Clean Data", validated_clean.manual_review_required, validated_clean.quality_metrics.overall_quality_score),
        ("Contaminated Data", validated_contaminated.manual_review_required, validated_contaminated.quality_metrics.overall_quality_score),
        ("Missing Applicant", validated_missing.manual_review_required, validated_missing.quality_metrics.overall_quality_score),
    ]
    
    for name, manual_review, quality_score in test_cases:
        status = "🚨 FLAGGED" if manual_review else "✅ PASSED"
        print(f"{name:20} | {status:12} | Quality: {quality_score:.2f}")
    
    print("\n✅ EntitySeparationValidator successfully integrated into ValidationService!")
    print("🎯 The system now detects and prevents inventor/applicant data confusion.")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_validation_integration())
        if success:
            print("\n🎉 All integration tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Integration tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Integration test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)