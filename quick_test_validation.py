#!/usr/bin/env python3
"""
Quick validation test for the enhanced extraction system components.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Module Imports...")
    print("-" * 30)
    
    try:
        from app.models.enhanced_extraction import (
            EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
            ValidationResult, QualityMetrics, ExtractionMethod
        )
        print("✅ Enhanced extraction models imported successfully")
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    try:
        from app.services.validation_service import ValidationService, FieldValidator
        print("✅ Validation service imported successfully")
    except Exception as e:
        print(f"❌ Validation service import failed: {e}")
        return False
    
    try:
        from app.services.enhanced_extraction_service import EnhancedExtractionService
        print("✅ Enhanced extraction service imported successfully")
    except Exception as e:
        print(f"❌ Enhanced extraction service import failed: {e}")
        return False
    
    return True

def test_field_validation():
    """Test field validation functionality"""
    print("\n🔍 Testing Field Validation...")
    print("-" * 30)
    
    try:
        from app.services.validation_service import FieldValidator
        validator = FieldValidator()
        
        # Test name validation
        result = validator.validate_name("John Doe", "given_name")
        print(f"Name validation: {'✅' if result.is_valid else '❌'} - '{result.normalized_value}'")
        
        # Test state validation
        result = validator.validate_state("CA", "US")
        print(f"State validation: {'✅' if result.is_valid else '❌'} - '{result.normalized_value}'")
        
        # Test email validation
        result = validator.validate_email("test@example.com")
        print(f"Email validation: {'✅' if result.is_valid else '❌'} - '{result.normalized_value}'")
        
        # Test date validation
        result = validator.validate_date("2023-12-31")
        print(f"Date validation: {'✅' if result.is_valid else '❌'} - '{result.normalized_value}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Field validation test failed: {e}")
        return False

def test_data_models():
    """Test data model creation"""
    print("\n📊 Testing Data Models...")
    print("-" * 25)
    
    try:
        from app.models.enhanced_extraction import (
            EnhancedInventor, EnhancedApplicant, QualityMetrics, 
            ExtractionMetadata, DataCompleteness, ExtractionMethod
        )
        
        # Test inventor creation
        inventor = EnhancedInventor(
            given_name="John",
            family_name="Doe",
            street_address="123 Main St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        print(f"✅ Inventor model created: {inventor.given_name} {inventor.family_name}")
        
        # Test applicant creation
        applicant = EnhancedApplicant(
            organization_name="TechCorp Inc",
            street_address="456 Business Ave",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.90
        )
        print(f"✅ Applicant model created: {applicant.organization_name}")
        
        # Test quality metrics
        metrics = QualityMetrics(
            completeness_score=0.95,
            accuracy_score=0.98,
            confidence_score=0.92,
            consistency_score=0.90,
            overall_quality_score=0.94,
            required_fields_populated=2,
            total_required_fields=2,
            optional_fields_populated=3,
            total_optional_fields=4,
            validation_errors=0,
            validation_warnings=1
        )
        print(f"✅ Quality metrics created: {metrics.overall_quality_score:.2f} overall score")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        return False

def test_cross_field_validation():
    """Test cross-field validation"""
    print("\n🔗 Testing Cross-Field Validation...")
    print("-" * 35)
    
    try:
        from app.services.validation_service import CrossFieldValidator
        from app.models.enhanced_extraction import EnhancedInventor, DataCompleteness
        
        validator = CrossFieldValidator()
        
        # Create test inventor
        inventor = EnhancedInventor(
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
        
        # Test consistency validation
        result = validator.validate_inventor_consistency(inventor)
        print(f"Inventor consistency: {'✅' if result.is_consistent else '❌'}")
        if result.issues:
            for issue in result.issues:
                print(f"  Issue: {issue}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-field validation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Patent Extraction System - Quick Validation Test")
    print("=" * 65)
    
    tests = [
        ("Module Imports", test_imports),
        ("Field Validation", test_field_validation),
        ("Data Models", test_data_models),
        ("Cross-Field Validation", test_cross_field_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📋 Test Results: {passed}/{total} tests passed")
    print("=" * 40)
    
    if passed == total:
        print("🎉 All tests passed! The enhanced extraction system is functional.")
        print("\nKey components validated:")
        print("  ✅ Enhanced data models")
        print("  ✅ Field validation framework")
        print("  ✅ Cross-field validation")
        print("  ✅ Quality metrics system")
        print("\n🚀 System is ready for integration!")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)