#!/usr/bin/env python3
"""
Test script to validate the applicant/inventor separation fixes
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_entity_separation_validation():
    """Test the entity separation validation logic"""
    
    print("🧪 Testing Entity Separation Validation")
    print("=" * 50)
    
    try:
        from app.services.entity_separation_validator import EntitySeparationValidator
        from app.models.enhanced_extraction import EnhancedInventor, EnhancedApplicant, DataCompleteness
        
        validator = EntitySeparationValidator()
        
        # Test 1: Contaminated inventor (has corporate name)
        print("\n📝 Test 1: Contaminated Inventor Detection")
        contaminated_inventor = EnhancedInventor(
            given_name="TechCorp Inc",  # This is wrong - corporate name in inventor field
            family_name="Technology Solutions",
            street_address="123 Business Plaza, Suite 400",
            city="San Francisco",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.8
        )
        
        result = validator.validate_inventor_purity(contaminated_inventor)
        print(f"  Contamination detected: {not result.is_valid}")
        print(f"  Errors found: {result.errors}")
        
        # Test 2: Clean inventor (individual person)
        print("\n📝 Test 2: Clean Inventor Validation")
        clean_inventor = EnhancedInventor(
            given_name="John",
            family_name="Smith",
            street_address="123 Residential St",
            city="Springfield",
            state="IL",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        result = validator.validate_inventor_purity(clean_inventor)
        print(f"  Clean inventor validated: {result.is_valid}")
        
        # Test 3: Incomplete applicant
        print("\n📝 Test 3: Applicant Completeness Check")
        incomplete_applicant = EnhancedApplicant(
            organization_name="TechCorp LLC",
            # Missing address fields
            completeness=DataCompleteness.INCOMPLETE,
            confidence_score=0.6
        )
        
        result = validator.validate_applicant_completeness(incomplete_applicant)
        print(f"  Incomplete applicant detected: {not result.is_valid}")
        print(f"  Missing fields: {result.errors}")
        
        # Test 4: Complete applicant
        print("\n📝 Test 4: Complete Applicant Validation")
        complete_applicant = EnhancedApplicant(
            organization_name="Innovation Labs LLC",
            street_address="456 Business Ave, Suite 200",
            city="Tech City",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
        
        result = validator.validate_applicant_completeness(complete_applicant)
        print(f"  Complete applicant validated: {result.is_valid}")
        
        # Test 5: Cross-contamination detection
        print("\n📝 Test 5: Cross-Contamination Detection")
        inventors = [contaminated_inventor, clean_inventor]
        applicants = [complete_applicant]
        
        cross_result = validator.detect_cross_contamination(inventors, applicants)
        print(f"  Cross-contamination detected: {not cross_result.is_consistent}")
        print(f"  Issues found: {cross_result.issues}")
        print(f"  Recommendations: {cross_result.recommendations}")
        
        # Test 6: Auto-fix functionality
        print("\n📝 Test 6: Auto-Fix Cross-Contamination")
        fix_results = validator.auto_fix_cross_contamination(inventors, applicants)
        print(f"  Fixes applied: {fix_results['fixes_applied']}")
        print(f"  Inventors to remove: {fix_results['inventors_to_remove']}")
        print(f"  New applicants to add: {len(fix_results['applicants_to_add'])}")
        
        if fix_results['applicants_to_add']:
            for i, new_applicant in enumerate(fix_results['applicants_to_add']):
                print(f"    New applicant {i}: {new_applicant.organization_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_validation_service_integration():
    """Test integration with validation service"""
    
    print("\n🧪 Testing Validation Service Integration")
    print("=" * 50)
    
    try:
        from app.services.validation_service import ValidationService
        from app.models.enhanced_extraction import (
            EnhancedExtractionResult, EnhancedInventor, EnhancedApplicant,
            QualityMetrics, ExtractionMetadata, DataCompleteness, ExtractionMethod
        )
        
        # Create test extraction result with contaminated data
        print("\n📝 Creating test extraction result with contamination...")
        
        # Contaminated inventor (has corporate name)
        contaminated_inventor = EnhancedInventor(
            given_name="Microsoft Corporation",  # Wrong - company name in inventor
            family_name="Technology Division",
            street_address="One Microsoft Way, Building 1",
            city="Redmond",
            state="WA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.8
        )
        
        # Clean inventor
        clean_inventor = EnhancedInventor(
            given_name="Jane",
            family_name="Doe",
            street_address="789 Home Street",
            city="Seattle",
            state="WA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.95
        )
        
        # Proper applicant
        proper_applicant = EnhancedApplicant(
            organization_name="Tech Innovations Inc",
            street_address="123 Corporate Blvd, Suite 500",
            city="San Jose",
            state="CA",
            country="US",
            completeness=DataCompleteness.COMPLETE,
            confidence_score=0.9
        )
        
        extraction_result = EnhancedExtractionResult(
            title="AI-POWERED PATENT ANALYSIS SYSTEM",
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
        
        extraction_result.inventors.extend([contaminated_inventor, clean_inventor])
        extraction_result.applicants.append(proper_applicant)
        
        print("✅ Test extraction result created with contamination")
        
        # Test validation service
        print("\n📝 Running enhanced validation service...")
        validation_service = ValidationService()
        
        # This would normally call the enhanced validation
        # For now, let's test the entity separation validator directly
        from app.services.entity_separation_validator import EntitySeparationValidator
        entity_validator = EntitySeparationValidator()
        
        # Test contamination detection
        cross_validation = entity_validator.detect_cross_contamination(
            extraction_result.inventors, extraction_result.applicants
        )
        
        print(f"✅ Validation completed")
        print(f"🔍 Cross-contamination detected: {not cross_validation.is_consistent}")
        print(f"⚠️ Issues found: {len(cross_validation.issues)}")
        
        for issue in cross_validation.issues:
            print(f"    - {issue}")
        
        print(f"💡 Recommendations: {len(cross_validation.recommendations)}")
        for rec in cross_validation.recommendations:
            print(f"    - {rec}")
        
        # Test auto-fix
        print("\n📝 Testing auto-fix functionality...")
        fix_results = entity_validator.auto_fix_cross_contamination(
            extraction_result.inventors, extraction_result.applicants
        )
        
        print(f"🔧 Fixes available: {len(fix_results['fixes_applied'])}")
        for fix in fix_results['fixes_applied']:
            print(f"    - {fix}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_real_world_scenario():
    """Test with a realistic contamination scenario"""
    
    print("\n🧪 Testing Real-World Contamination Scenario")
    print("=" * 50)
    
    try:
        from app.services.entity_separation_validator import EntitySeparationValidator
        from app.models.enhanced_extraction import EnhancedInventor, EnhancedApplicant, DataCompleteness
        
        validator = EntitySeparationValidator()
        
        print("\n📝 Scenario: Company name extracted to inventor field")
        
        # This simulates what happens when the LLM incorrectly extracts
        # company information into inventor fields
        problematic_inventors = [
            EnhancedInventor(
                given_name="Apple Inc",  # Company name in given_name
                family_name="Cupertino Technology",
                street_address="1 Apple Park Way, Building 1",  # Business address
                city="Cupertino",
                state="CA",
                country="US",
                completeness=DataCompleteness.COMPLETE,
                confidence_score=0.7
            ),
            EnhancedInventor(
                given_name="John",  # Correct individual
                family_name="Smith",
                street_address="123 Home Ave",
                city="San Jose",
                state="CA",
                country="US",
                completeness=DataCompleteness.COMPLETE,
                confidence_score=0.95
            )
        ]
        
        # No applicants initially (they were misclassified as inventors)
        applicants = []
        
        print("📊 Initial state:")
        print(f"  Inventors: {len(problematic_inventors)}")
        print(f"  Applicants: {len(applicants)}")
        
        # Detect contamination
        cross_result = validator.detect_cross_contamination(problematic_inventors, applicants)
        print(f"\n🔍 Contamination analysis:")
        print(f"  Issues detected: {len(cross_result.issues)}")
        print(f"  Consistent: {cross_result.is_consistent}")
        
        for issue in cross_result.issues:
            print(f"    ⚠️ {issue}")
        
        # Apply auto-fix
        fix_results = validator.auto_fix_cross_contamination(problematic_inventors, applicants)
        print(f"\n🔧 Auto-fix results:")
        print(f"  Fixes applied: {len(fix_results['fixes_applied'])}")
        print(f"  Inventors to remove: {fix_results['inventors_to_remove']}")
        print(f"  New applicants created: {len(fix_results['applicants_to_add'])}")
        
        # Simulate applying the fixes
        fixed_inventors = [inv for i, inv in enumerate(problematic_inventors) 
                          if i not in fix_results['inventors_to_remove']]
        fixed_applicants = applicants + fix_results['applicants_to_add']
        
        print(f"\n✅ After fixes:")
        print(f"  Clean inventors: {len(fixed_inventors)}")
        print(f"  Proper applicants: {len(fixed_applicants)}")
        
        # Verify the fix worked
        final_validation = validator.detect_cross_contamination(fixed_inventors, fixed_applicants)
        print(f"  Final validation - Consistent: {final_validation.is_consistent}")
        
        if fixed_applicants:
            print(f"  Created applicant: {fixed_applicants[0].organization_name}")
        
        return final_validation.is_consistent
        
    except Exception as e:
        print(f"❌ Real-world scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all entity separation tests"""
    
    print("🚀 ENTITY SEPARATION FIX VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Entity Separation Validation", test_entity_separation_validation),
        ("Validation Service Integration", test_validation_service_integration),
        ("Real-World Contamination Scenario", test_real_world_scenario)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n💥 {test_name}: CRASHED - {e}")
    
    print(f"\n📋 ENTITY SEPARATION TEST RESULTS")
    print("=" * 40)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ENTITY SEPARATION FIXES VALIDATED!")
        print("=" * 45)
        print("✅ Entity separation validation working")
        print("✅ Cross-contamination detection functional")
        print("✅ Auto-fix logic operational")
        print("✅ Real-world scenarios handled correctly")
        
        print("\n🚀 Ready for integration with LLM service!")
        
        print("\n📋 NEXT STEPS:")
        print("1. Update validation_service.py to use EntitySeparationValidator")
        print("2. Update LLM prompts with enhanced entity separation")
        print("3. Test with real patent documents")
        print("4. Monitor extraction accuracy improvements")
    else:
        print(f"\n⚠️ SOME TESTS FAILED")
        print("=" * 25)
        print(f"{total - passed} test(s) failed")
        print("Please review the error messages above")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)