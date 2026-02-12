#!/usr/bin/env python3
"""
Comprehensive test for data verification functionality.
Tests all aspects of the validation framework to ensure data quality.
"""

import sys
import os
import asyncio
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_field_validation_comprehensive():
    """Test comprehensive field validation functionality"""
    print("🔍 TESTING FIELD VALIDATION FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from app.services.validation_service import FieldValidator
        from app.models.enhanced_extraction import ValidationResult
        
        validator = FieldValidator()
        test_results = []
        
        # Test 1: Name Validation
        print("\n📝 Testing Name Validation...")
        test_cases = [
            ("John Doe", "full_name", True),
            ("Dr. Sarah Elizabeth Johnson", "full_name", True),
            ("", "full_name", False),
            ("123", "full_name", False),
            ("John", "given_name", True),
            ("", "given_name", False)
        ]
        
        for name, field_type, expected in test_cases:
            result = validator.validate_name(name, field_type)
            status = "✅" if result.is_valid == expected else "❌"
            print(f"  {status} '{name}' ({field_type}): {result.is_valid} (expected {expected})")
            test_results.append(result.is_valid == expected)
        
        # Test 2: State Validation
        print("\n🗺️ Testing State Validation...")
        state_cases = [
            ("CA", "US", True),
            ("California", "US", True),
            ("NY", "US", True),
            ("New York", "US", True),
            ("XX", "US", False),
            ("Invalid", "US", False)
        ]
        
        for state, country, expected in state_cases:
            result = validator.validate_state(state, country)
            status = "✅" if result.is_valid == expected else "❌"
            print(f"  {status} '{state}' ({country}): {result.is_valid} (expected {expected})")
            test_results.append(result.is_valid == expected)
        
        # Test 3: Email Validation
        print("\n📧 Testing Email Validation...")
        email_cases = [
            ("test@example.com", True),
            ("user.name@domain.co.uk", True),
            ("patents@techcorp.com", True),
            ("invalid-email", False),
            ("@domain.com", False),
            ("user@", False),
            ("", False)
        ]
        
        for email, expected in email_cases:
            result = validator.validate_email(email)
            status = "✅" if result.is_valid == expected else "❌"
            print(f"  {status} '{email}': {result.is_valid} (expected {expected})")
            test_results.append(result.is_valid == expected)
        
        # Test 4: Date Validation
        print("\n📅 Testing Date Validation...")
        date_cases = [
            ("2023-12-31", True),
            ("2023-01-01", True),
            ("2023-02-29", False),  # Not a leap year
            ("2024-02-29", True),   # Leap year
            ("invalid-date", False),
            ("12/31/2023", False),  # Wrong format
            ("", False)
        ]
        
        for date, expected in date_cases:
            result = validator.validate_date(date)
            status = "✅" if result.is_valid == expected else "❌"
            print(f"  {status} '{date}': {result.is_valid} (expected {expected})")
            test_results.append(result.is_valid == expected)
        
        # Test 5: Country Validation
        print("\n🌍 Testing Country Validation...")
        country_cases = [
            ("US", True),
            ("United States", True),
            ("CA", True),
            ("Canada", True),
            ("XX", False),
            ("Invalid Country", False)
        ]
        
        for country, expected in country_cases:
            result = validator.validate_country(country)
            status = "✅" if result.is_valid == expected else "❌"
            print(f"  {status} '{country}': {result.is_valid} (expected {expected})")
            test_results.append(result.is_valid == expected)
        
        passed = sum(test_results)
        total = len(test_results)
        print(f"\n📊 Field Validation Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Field validation test failed: {e}")
        return False

def test_cross_field_validation():
    """Test cross-field validation functionality"""
    print("\n🔗 TESTING CROSS-FIELD VALIDATION FUNCTIONALITY")
    print("=" * 55)
    
    try:
        from app.services.validation_service import CrossFieldValidator
        from app.models.enhanced_extraction import EnhancedInventor, EnhancedApplicant, DataCompleteness
        
        validator = CrossFieldValidator()
        test_results = []
        
        # Test 1: Inventor Consistency Validation
        print("\n👤 Testing Inventor Consistency...")
        
        # Valid inventor
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
        status = "✅" if result.is_consistent else "❌"
        print(f"  {status} Valid inventor consistency: {result.is_consistent}")
        test_results.append(result.is_consistent)
        
        # Inconsistent inventor (name mismatch)
        inconsistent_inventor = EnhancedInventor(
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
        
        result = validator.validate_inventor_consistency(inconsistent_inventor)
        status = "✅" if not result.is_consistent else "❌"
        print(f"  {status} Inconsistent inventor (name mismatch): {not result.is_consistent}")
        if result.issues:
            for issue in result.issues:
                print(f"    ⚠️ Issue: {issue}")
        test_results.append(not result.is_consistent)
        
        # Test 2: Address Consistency Validation
        print("\n🏠 Testing Address Consistency...")
        
        # Test geographic consistency
        valid_address = {
            "city": "Springfield",
            "state": "IL",
            "country": "US"
        }
        
        result = validator.validate_geographic_consistency(
            valid_address["city"], 
            valid_address["state"], 
            valid_address["country"]
        )
        status = "✅" if result.is_consistent else "❌"
        print(f"  {status} Valid geographic consistency: {result.is_consistent}")
        test_results.append(result.is_consistent)
        
        # Invalid geographic consistency
        invalid_address = {
            "city": "Toronto",
            "state": "CA",  # California state code but Toronto is in Canada
            "country": "CA"  # Canada
        }
        
        result = validator.validate_geographic_consistency(
            invalid_address["city"], 
            invalid_address["state"], 
            invalid_address["country"]
        )
        status = "✅" if not result.is_consistent else "❌"
        print(f"  {status} Invalid geographic consistency: {not result.is_consistent}")
        if result.issues:
            for issue in result.issues:
                print(f"    ⚠️ Issue: {issue}")
        test_results.append(not result.is_consistent)
        
        passed = sum(test_results)
        total = len(test_results)
        print(f"\n📊 Cross-Field Validation Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Cross-field validation test failed: {e}")
        return False

async def test_validation_service_integration():
    """Test the complete validation service integration"""
    print("\n🔧 TESTING VALIDATION SERVICE INTEGRATION")
    print("=" * 45)
    
    try:
        from app.services.validation_service import ValidationService
        from app.models.enhanced_extraction import (
            EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
            QualityMetrics, ExtractionMetadata, DataCompleteness, ExtractionMethod
        )
        from datetime import datetime
        
        validation_service = ValidationService()
        test_results = []
        
        # Create a test extraction result
        print("\n📊 Creating test extraction result...")
        
        # Create test inventor
        inventor = EnhancedInventor(
            given_name="Sarah Elizabeth",
            family_name="Johnson",
            full_name="Sarah Elizabeth Johnson",
            street_address="1234 Innovation Drive, Suite 100",
            city="Palo Alto",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        # Create test applicant
        applicant = EnhancedApplicant(
            organization_name="TechCorp Innovations LLC",
            street_address="1234 Innovation Drive, Suite 100",
            city="Palo Alto",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.90
        )
        
        # Create test extraction result
        extraction_result = EnhancedExtractionResult(
            title="ADVANCED MACHINE LEARNING SYSTEM FOR AUTOMATED PATENT ANALYSIS",
            attorney_docket_number="TECH-2024-001",
            customer_number="12345",
            correspondence_email="patents@techcorp.com",
            extraction_metadata=ExtractionMetadata(
                extraction_method=ExtractionMethod.TEXT_EXTRACTION,
                document_type="patent_application",
                processing_time=1.5
            ),
            quality_metrics=QualityMetrics(
                completeness_score=0.95,
                accuracy_score=0.98,
                confidence_score=0.92,
                consistency_score=0.90,
                overall_quality_score=0.94,
                required_fields_populated=8,
                total_required_fields=10,
                optional_fields_populated=5,
                total_optional_fields=8,
                validation_errors=0,
                validation_warnings=1
            )
        )
        
        extraction_result.inventors.append(inventor)
        extraction_result.applicants.append(applicant)
        
        print("✅ Test extraction result created")
        
        # Test validation service
        print("\n🔍 Running validation service...")
        validation_results = await validation_service.validate_extraction_result(extraction_result)
        
        print(f"✅ Validation completed: Overall valid = {validation_results.overall_valid}")
        print(f"📊 Field validations: {len(validation_results.field_validations)}")
        print(f"🔗 Cross-field validations: {len(validation_results.cross_field_validations)}")
        
        # Check specific validations
        for field, result in validation_results.field_validations.items():
            status = "✅" if result.is_valid else "❌"
            print(f"  {status} {field}: {result.normalized_value}")
            if result.issues:
                for issue in result.issues:
                    print(f"    ⚠️ {issue}")
        
        test_results.append(validation_results.overall_valid)
        
        # Test quality metrics calculation
        print("\n📈 Testing quality metrics calculation...")
        updated_metrics = validation_service.calculate_quality_metrics(
            extraction_result, validation_results
        )
        
        print(f"✅ Quality metrics calculated:")
        print(f"  📊 Completeness: {updated_metrics.completeness_score:.2f}")
        print(f"  🎯 Accuracy: {updated_metrics.accuracy_score:.2f}")
        print(f"  🔒 Confidence: {updated_metrics.confidence_score:.2f}")
        print(f"  🔄 Consistency: {updated_metrics.consistency_score:.2f}")
        print(f"  ⭐ Overall: {updated_metrics.overall_quality_score:.2f}")
        
        # Verify metrics are reasonable
        metrics_valid = (
            0.0 <= updated_metrics.completeness_score <= 1.0 and
            0.0 <= updated_metrics.accuracy_score <= 1.0 and
            0.0 <= updated_metrics.confidence_score <= 1.0 and
            0.0 <= updated_metrics.overall_quality_score <= 1.0
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

def test_data_completeness_validation():
    """Test data completeness validation functionality"""
    print("\n📋 TESTING DATA COMPLETENESS VALIDATION")
    print("=" * 42)
    
    try:
        from app.services.validation_service import ValidationService
        from app.models.enhanced_extraction import EnhancedInventor, DataCompleteness
        
        validation_service = ValidationService()
        test_results = []
        
        # Test 1: Complete inventor
        print("\n✅ Testing complete inventor...")
        complete_inventor = EnhancedInventor(
            given_name="John",
            family_name="Doe",
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        completeness = validation_service.assess_inventor_completeness(complete_inventor)
        print(f"  Completeness assessment: {completeness}")
        test_results.append(completeness == DataCompleteness.COMPLETE)
        
        # Test 2: Incomplete inventor (missing address)
        print("\n⚠️ Testing incomplete inventor...")
        incomplete_inventor = EnhancedInventor(
            given_name="Jane",
            family_name="Smith",
            # Missing address fields
            completeness=DataCompleteness.INCOMPLETE,
            confidence_score=0.60
        )
        
        completeness = validation_service.assess_inventor_completeness(incomplete_inventor)
        print(f"  Completeness assessment: {completeness}")
        test_results.append(completeness in [DataCompleteness.INCOMPLETE, DataCompleteness.PARTIAL_ADDRESS])
        
        # Test 3: Partial name inventor
        print("\n🔤 Testing partial name inventor...")
        partial_name_inventor = EnhancedInventor(
            given_name="Bob",
            # Missing family name
            street_address="456 Oak Ave",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.PARTIAL_NAME,
            confidence_score=0.70
        )
        
        completeness = validation_service.assess_inventor_completeness(partial_name_inventor)
        print(f"  Completeness assessment: {completeness}")
        test_results.append(completeness == DataCompleteness.PARTIAL_NAME)
        
        passed = sum(test_results)
        total = len(test_results)
        print(f"\n📊 Data Completeness Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Data completeness validation test failed: {e}")
        return False

async def main():
    """Run all data verification functionality tests"""
    print("🧪 COMPREHENSIVE DATA VERIFICATION FUNCTIONALITY TEST")
    print("=" * 60)
    print("Testing all aspects of the validation framework...")
    print()
    
    tests = [
        ("Field Validation", test_field_validation_comprehensive),
        ("Cross-Field Validation", test_cross_field_validation),
        ("Validation Service Integration", test_validation_service_integration),
        ("Data Completeness Validation", test_data_completeness_validation)
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
    
    print(f"\n📋 DATA VERIFICATION FUNCTIONALITY TEST RESULTS")
    print("=" * 55)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL DATA VERIFICATION FUNCTIONALITY TESTS PASSED!")
        print("=" * 50)
        print("✅ Field validation is working correctly")
        print("✅ Cross-field validation is operational")
        print("✅ Validation service integration is functional")
        print("✅ Data completeness validation is working")
        print("\n🚀 Data verification functionality is fully operational!")
        
        print("\n📋 VERIFIED CAPABILITIES:")
        print("  • Name, email, date, state, country validation")
        print("  • Cross-field consistency checking")
        print("  • Geographic validation")
        print("  • Data completeness assessment")
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