#!/usr/bin/env python3
"""
Corrected test for data verification functionality.
Tests the actual implemented validation framework.
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_field_validation_basic():
    """Test basic field validation functionality"""
    print("🔍 TESTING FIELD VALIDATION FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from app.services.validation_service import FieldValidator
        
        validator = FieldValidator()
        test_results = []
        
        # Test 1: Name Validation
        print("\n📝 Testing Name Validation...")
        
        # Valid names
        result = validator.validate_name("John Doe", "full_name")
        print(f"  ✅ 'John Doe': {result.is_valid} - {result.normalized_value}")
        test_results.append(result.is_valid)
        
        # Empty name (should fail)
        result = validator.validate_name("", "full_name")
        print(f"  ❌ Empty name: {result.is_valid} (expected False)")
        test_results.append(not result.is_valid)
        
        # Test 2: State Validation
        print("\n🗺️ Testing State Validation...")
        
        # Valid US state
        result = validator.validate_state("CA", "US")
        print(f"  ✅ 'CA' (US): {result.is_valid} - {result.normalized_value}")
        test_results.append(result.is_valid)
        
        # Invalid US state
        result = validator.validate_state("XX", "US")
        print(f"  ❌ 'XX' (US): {result.is_valid} (expected False)")
        test_results.append(not result.is_valid)
        
        # Test 3: Email Validation
        print("\n📧 Testing Email Validation...")
        
        # Valid email
        result = validator.validate_email("test@example.com")
        print(f"  ✅ 'test@example.com': {result.is_valid} - {result.normalized_value}")
        test_results.append(result.is_valid)
        
        # Invalid email
        result = validator.validate_email("invalid-email")
        print(f"  ❌ 'invalid-email': {result.is_valid} (expected False)")
        test_results.append(not result.is_valid)
        
        # Test 4: Date Validation
        print("\n📅 Testing Date Validation...")
        
        # Valid date
        result = validator.validate_date("2023-12-31")
        print(f"  ✅ '2023-12-31': {result.is_valid} - {result.normalized_value}")
        test_results.append(result.is_valid)
        
        # Invalid date
        result = validator.validate_date("invalid-date")
        print(f"  ❌ 'invalid-date': {result.is_valid} (expected False)")
        test_results.append(not result.is_valid)
        
        passed = sum(test_results)
        total = len(test_results)
        print(f"\n📊 Field Validation Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Field validation test failed: {e}")
        return False

def test_cross_field_validation_basic():
    """Test basic cross-field validation functionality"""
    print("\n🔗 TESTING CROSS-FIELD VALIDATION FUNCTIONALITY")
    print("=" * 55)
    
    try:
        from app.services.validation_service import CrossFieldValidator
        from app.models.enhanced_extraction import EnhancedInventor, EnhancedApplicant, DataCompleteness
        
        validator = CrossFieldValidator()
        test_results = []
        
        # Test 1: Valid Inventor Consistency
        print("\n👤 Testing Inventor Consistency...")
        
        valid_inventor = EnhancedInventor(
            given_name="John",
            family_name="Doe",
            full_name="John Doe",
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        result = validator.validate_inventor_consistency(valid_inventor)
        print(f"  ✅ Valid inventor consistency: {result.is_consistent}")
        test_results.append(result.is_consistent)
        
        # Test 2: Invalid Inventor Consistency (name mismatch)
        invalid_inventor = EnhancedInventor(
            given_name="John",
            family_name="Doe",
            full_name="Jane Smith",  # Mismatch
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        result = validator.validate_inventor_consistency(invalid_inventor)
        print(f"  ❌ Invalid inventor (name mismatch): {not result.is_consistent}")
        if result.issues:
            for issue in result.issues:
                print(f"    ⚠️ Issue: {issue}")
        test_results.append(not result.is_consistent)
        
        # Test 3: Valid Applicant Consistency
        print("\n🏢 Testing Applicant Consistency...")
        
        valid_applicant = EnhancedApplicant(
            organization_name="TechCorp Inc",
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.90
        )
        
        result = validator.validate_applicant_consistency(valid_applicant)
        print(f"  ✅ Valid applicant consistency: {result.is_consistent}")
        test_results.append(result.is_consistent)
        
        passed = sum(test_results)
        total = len(test_results)
        print(f"\n📊 Cross-Field Validation Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Cross-field validation test failed: {e}")
        return False

async def test_validation_service_basic():
    """Test basic validation service integration"""
    print("\n🔧 TESTING VALIDATION SERVICE INTEGRATION")
    print("=" * 45)
    
    try:
        from app.services.validation_service import ValidationService
        from app.models.enhanced_extraction import (
            EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
            QualityMetrics, ExtractionMetadata, DataCompleteness, ExtractionMethod
        )
        
        validation_service = ValidationService()
        test_results = []
        
        # Create a simple test extraction result
        print("\n📊 Creating test extraction result...")
        
        inventor = EnhancedInventor(
            given_name="Sarah",
            family_name="Johnson",
            street_address="1234 Innovation Drive",
            city="Palo Alto",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        applicant = EnhancedApplicant(
            organization_name="TechCorp LLC",
            street_address="1234 Innovation Drive",
            city="Palo Alto",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.90
        )
        
        extraction_result = EnhancedExtractionResult(
            title="MACHINE LEARNING SYSTEM",
            extraction_metadata=ExtractionMetadata(
                extraction_method=ExtractionMethod.TEXT_EXTRACTION,
                document_type="patent_application",
                processing_time=1.5
            ),
            quality_metrics=QualityMetrics(
                completeness_score=0.0,  # Will be calculated
                accuracy_score=0.0,
                confidence_score=0.0,
                consistency_score=0.0,
                overall_quality_score=0.0,
                required_fields_populated=0,
                total_required_fields=0,
                optional_fields_populated=0,
                total_optional_fields=0,
                validation_errors=0,
                validation_warnings=0
            )
        )
        
        extraction_result.inventors.append(inventor)
        extraction_result.applicants.append(applicant)
        
        print("✅ Test extraction result created")
        
        # Test validation service
        print("\n🔍 Running validation service...")
        validated_result = await validation_service.validate_extraction_result(extraction_result)
        
        print(f"✅ Validation completed")
        print(f"📊 Field validations: {len(validated_result.field_validations)}")
        print(f"🔗 Cross-field validations: {len(validated_result.cross_field_validations)}")
        print(f"⚠️ Manual review required: {validated_result.manual_review_required}")
        
        # Check that validations were performed
        test_results.append(len(validated_result.field_validations) > 0)
        test_results.append(len(validated_result.cross_field_validations) > 0)
        
        # Test quality metrics
        print("\n📈 Testing quality metrics...")
        metrics = validated_result.quality_metrics
        
        print(f"  📊 Completeness: {metrics.completeness_score:.2f}")
        print(f"  🎯 Accuracy: {metrics.accuracy_score:.2f}")
        print(f"  🔒 Confidence: {metrics.confidence_score:.2f}")
        print(f"  ⭐ Overall: {metrics.overall_quality_score:.2f}")
        
        # Verify metrics are in valid range
        metrics_valid = (
            0.0 <= metrics.completeness_score <= 1.0 and
            0.0 <= metrics.accuracy_score <= 1.0 and
            0.0 <= metrics.confidence_score <= 1.0 and
            0.0 <= metrics.overall_quality_score <= 1.0
        )
        
        test_results.append(metrics_valid)
        print(f"✅ Quality metrics validation: {metrics_valid}")
        
        passed = sum(test_results)
        total = len(test_results)
        print(f"\n📊 Validation Service Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Validation service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all data verification functionality tests"""
    print("🧪 DATA VERIFICATION FUNCTIONALITY TEST")
    print("=" * 45)
    print("Testing the actual implemented validation framework...")
    print()
    
    tests = [
        ("Field Validation", test_field_validation_basic),
        ("Cross-Field Validation", test_cross_field_validation_basic),
        ("Validation Service Integration", test_validation_service_basic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n💥 {test_name}: CRASHED - {e}")
    
    print(f"\n📋 DATA VERIFICATION TEST RESULTS")
    print("=" * 40)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 DATA VERIFICATION FUNCTIONALITY IS WORKING!")
        print("=" * 45)
        print("✅ Field validation is operational")
        print("✅ Cross-field validation is working")
        print("✅ Validation service integration is functional")
        print("✅ Quality metrics calculation is working")
        print("\n🚀 Data verification functionality is confirmed operational!")
        
        print("\n📋 VERIFIED CAPABILITIES:")
        print("  • Name, email, date, state validation")
        print("  • Cross-field consistency checking")
        print("  • Inventor and applicant validation")
        print("  • Quality metrics calculation")
        print("  • Comprehensive error detection")
    else:
        print(f"\n⚠️ DATA VERIFICATION HAS ISSUES")
        print("=" * 35)
        print(f"{total - passed} test(s) failed")
        print("Please review the error messages above")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)