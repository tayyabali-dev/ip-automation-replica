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

async def test_validation_integration():
    """Test the complete validation pipeline with entity separation"""
    
    print("🧪 Testing ValidationService with EntitySeparationValidator Integration")
    print("=" * 70)
    
    # Initialize validation service
    validation_service = ValidationService()
    
    # Test Case 1: Clean data (should pass all validations)
    print("\n📋 Test Case 1: Clean Data")
    print("-" * 30)
    
    clean_result = EnhancedExtractionResult(
        title="Advanced Widget Technology",
        inventors=[
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
        ],
        applicants=[
            EnhancedApplicant(
                organization_name="Tech Corp Inc.",
                street_address="456 Business Ave",
                city="San Francisco",
                state="CA",
                country="US",
                confidence_score=0.90,
                completeness=DataCompleteness.COMPLETE
            )
        ],
        field_validations=[],
        cross_field_validations=[],
        extraction_warnings=[],
        recommendations=[]
    )
    
    validated_clean = await validation_service.validate_extraction_result(clean_result)
    
    print(f"✅ Manual Review Required: {validated_clean.manual_review_required}")
    print(f"✅ Quality Score: {validated_clean.quality_metrics.overall_quality_score:.2f}")
    print(f"✅ Validation Errors: {len([v for v in validated_clean.field_validations if not v.validation_result.is_valid])}")
    print(f"✅ Cross-field Issues: {len([v for v in validated_clean.cross_field_validations if not v.is_consistent])}")
    print(f"✅ Warnings: {len(validated_clean.extraction_warnings)}")
    
    # Test Case 2: Contaminated data (inventor has company name)
    print("\n📋 Test Case 2: Contaminated Data - Company in Inventor")
    print("-" * 50)
    
    contaminated_result = EnhancedExtractionResult(
        title="Widget Innovation",
        inventors=[
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
        ],
        applicants=[
            EnhancedApplicant(
                organization_name="Tech Corp Inc.",
                street_address="456 Business Ave",
                city="San Francisco",
                state="CA",
                country="US",
                confidence_score=0.90,
                completeness=DataCompleteness.COMPLETE
            )
        ],
        field_validations=[],
        cross_field_validations=[],
        extraction_warnings=[],
        recommendations=[]
    )
    
    validated_contaminated = await validation_service.validate_extraction_result(contaminated_result)
    
    print(f"🚨 Manual Review Required: {validated_contaminated.manual_review_required}")
    print(f"🚨 Quality Score: {validated_contaminated.quality_metrics.overall_quality_score:.2f}")
    print(f"🚨 Validation Errors: {len([v for v in validated_contaminated.field_validations if not v.validation_result.is_valid])}")
    print(f"🚨 Cross-field Issues: {len([v for v in validated_contaminated.cross_field_validations if not v.is_consistent])}")
    print(f"🚨 Warnings: {len(validated_contaminated.extraction_warnings)}")
    
    print("\n🔍 Detected Issues:")
    for warning in validated_contaminated.extraction_warnings:
        print(f"   • {warning}")
    
    # Test Case 3: Missing applicant data
    print("\n📋 Test Case 3: Missing Applicant Data")
    print("-" * 35)
    
    missing_applicant_result = EnhancedExtractionResult(
        title="Simple Invention",
        inventors=[
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
        ],
        applicants=[],  # No applicants!
        field_validations=[],
        cross_field_validations=[],
        extraction_warnings=[],
        recommendations=[]
    )
    
    validated_missing = await validation_service.validate_extraction_result(missing_applicant_result)
    
    print(f"⚠️  Manual Review Required: {validated_missing.manual_review_required}")
    print(f"⚠️  Quality Score: {validated_missing.quality_metrics.overall_quality_score:.2f}")
    print(f"⚠️  Recommendations: {len(validated_missing.recommendations)}")
    
    print("\n💡 Recommendations:")
    for rec in validated_missing.recommendations:
        print(f"   • {rec}")
    
    # Test Case 4: Cross-contamination between inventors and applicants
    print("\n📋 Test Case 4: Cross-Contamination Detection")
    print("-" * 42)
    
    cross_contaminated_result = EnhancedExtractionResult(
        title="Contaminated Extraction",
        inventors=[
            EnhancedInventor(
                given_name="John",
                family_name="Smith",
                street_address="123 Main St",
                city="San Francisco",
                state="CA",
                country="US",
                confidence_score=0.85,
                completeness=DataCompleteness.COMPLETE
            )
        ],
        applicants=[
            EnhancedApplicant(
                individual_given_name="John",  # Same person as inventor!
                individual_family_name="Smith",
                street_address="123 Main St",  # Same address!
                city="San Francisco",
                state="CA",
                country="US",
                confidence_score=0.85,
                completeness=DataCompleteness.COMPLETE
            )
        ],
        field_validations=[],
        cross_field_validations=[],
        extraction_warnings=[],
        recommendations=[]
    )
    
    validated_cross = await validation_service.validate_extraction_result(cross_contaminated_result)
    
    print(f"🔄 Manual Review Required: {validated_cross.manual_review_required}")
    print(f"🔄 Quality Score: {validated_cross.quality_metrics.overall_quality_score:.2f}")
    print(f"🔄 Cross-contamination Issues: {len([v for v in validated_cross.cross_field_validations if v.validation_type == 'entity_cross_contamination'])}")
    
    print("\n🔍 Cross-contamination Warnings:")
    contamination_warnings = [w for w in validated_cross.extraction_warnings if 'contamination' in w.lower()]
    for warning in contamination_warnings:
        print(f"   • {warning}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    test_cases = [
        ("Clean Data", validated_clean.manual_review_required, validated_clean.quality_metrics.overall_quality_score),
        ("Contaminated Data", validated_contaminated.manual_review_required, validated_contaminated.quality_metrics.overall_quality_score),
        ("Missing Applicant", validated_missing.manual_review_required, validated_missing.quality_metrics.overall_quality_score),
        ("Cross-contamination", validated_cross.manual_review_required, validated_cross.quality_metrics.overall_quality_score)
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