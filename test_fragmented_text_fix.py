#!/usr/bin/env python3
"""
Test script to verify the fragmented PDF text cleaning fix.

This script tests the clean_fragmented_text() function with various
fragmented text patterns to ensure it properly normalizes text before
sending to the LLM.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm import clean_fragmented_text

def test_fragmented_text_cleaning():
    """Test the fragmented text cleaning function with various patterns."""
    
    print("🧪 Testing Fragmented PDF Text Cleaning Fix")
    print("=" * 60)
    
    # Test cases based on the reported issue
    test_cases = [
        {
            "name": "Word-per-line fragmentation (main issue)",
            "input": "DAVID\n \nCHEN\n \nVANCOUVER\n \n(CA)",
            "expected": "DAVID CHEN VANCOUVER (CA)"
        },
        {
            "name": "Multiple inventors fragmented",
            "input": "JOHN\n \nSMITH\n \nNEW\n \nYORK\n \n(US)\n\nMARY\n \nJOHNSON\n \nBOSTON\n \n(US)",
            "expected": "JOHN SMITH NEW YORK (US)\n\nMARY JOHNSON BOSTON (US)"
        },
        {
            "name": "Address fragmentation",
            "input": "123\n \nMAIN\n \nSTREET\n \nSUITE\n \n456\n \nANYTOWN\n \nCA\n \n94301",
            "expected": "123 MAIN STREET SUITE 456 ANYTOWN CA 94301"
        },
        {
            "name": "Company name fragmentation",
            "input": "APPLE\n \nINC.\n \nCUPERTINO\n \nCA\n \n95014",
            "expected": "APPLE INC. CUPERTINO CA 95014"
        },
        {
            "name": "Mixed content with proper paragraphs",
            "input": "TITLE\n \nOF\n \nINVENTION:\n \nSYSTEM\n \nFOR\n \nVR\n\n\nINVENTOR\n \nINFORMATION:\nJOHN\n \nDOE",
            "expected": "TITLE OF INVENTION: SYSTEM FOR VR\n\nINVENTOR INFORMATION:\nJOHN DOE"
        },
        {
            "name": "Spacing around punctuation",
            "input": "VANCOUVER\n \n(\n \nCA\n \n)\n \n,\n \nCOUNTRY",
            "expected": "VANCOUVER (CA), COUNTRY"
        },
        {
            "name": "Normal text (should remain unchanged)",
            "input": "This is normal text with proper spacing.\n\nThis is a new paragraph.",
            "expected": "This is normal text with proper spacing.\n\nThis is a new paragraph."
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Input:    '{test_case['input']}'")
        
        # Apply the cleaning function
        result = clean_fragmented_text(test_case['input'])
        print(f"Output:   '{result}'")
        print(f"Expected: '{test_case['expected']}'")
        
        # Check if the result matches expected
        if result == test_case['expected']:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
        
        print("-" * 40)
    
    print(f"\n🏁 Test Summary")
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED! The fragmented text cleaning fix is working correctly.")
        print("\n📝 What this means:")
        print("   • PDFs with word-per-line fragmentation will now be properly cleaned")
        print("   • Text like 'DAVID\\n \\nCHEN' will become 'DAVID CHEN'")
        print("   • The LLM will receive clean, readable text for extraction")
        print("   • Both inventors should now be extractable from problematic PDFs")
    else:
        print("❌ SOME TESTS FAILED! The cleaning function needs adjustment.")
    
    return all_passed

def test_real_world_example():
    """Test with a real-world example similar to the reported issue."""
    
    print("\n🌍 Real-World Example Test")
    print("=" * 60)
    
    # Simulate the actual problematic PDF text
    problematic_pdf_text = """--- PAGE 1 ---
PATENT\n \nAPPLICATION\n \nDATA\n \nSHEET

TITLE\n \nOF\n \nINVENTION:
SYSTEM\n \nAND\n \nMETHOD\n \nFOR\n \nVIRTUAL\n \nREALITY

INVENTOR\n \nINFORMATION:

INVENTOR\n \n1:
DAVID\n \nCHEN
VANCOUVER\n \n(CA)

INVENTOR\n \n2:
SARAH\n \nWILSON
SEATTLE\n \nWA\n \n98101\n \n(US)

APPLICANT\n \nINFORMATION:
TECH\n \nCORP\n \nINC.
123\n \nMAIN\n \nSTREET
SILICON\n \nVALLEY\n \nCA\n \n94301"""

    print("Before cleaning:")
    print(repr(problematic_pdf_text))
    
    cleaned_text = clean_fragmented_text(problematic_pdf_text)
    
    print("\nAfter cleaning:")
    print(repr(cleaned_text))
    
    print("\nReadable format:")
    print(cleaned_text)
    
    # Check if key information is now properly formatted
    checks = [
        ("DAVID CHEN" in cleaned_text, "David Chen's name is properly joined"),
        ("SARAH WILSON" in cleaned_text, "Sarah Wilson's name is properly joined"),
        ("VANCOUVER (CA)" in cleaned_text, "Vancouver address is properly formatted"),
        ("SEATTLE WA 98101 (US)" in cleaned_text, "Seattle address is properly formatted"),
        ("TECH CORP INC." in cleaned_text, "Company name is properly joined"),
        ("SILICON VALLEY CA 94301" in cleaned_text, "Company address is properly formatted")
    ]
    
    print(f"\n📊 Content Validation:")
    all_good = True
    for check_passed, description in checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
        if not check_passed:
            all_good = False
    
    if all_good:
        print("\n🎉 SUCCESS! The problematic PDF text is now properly cleaned and should extract correctly.")
    else:
        print("\n⚠️  Some issues remain. The cleaning function may need further refinement.")
    
    return all_good

if __name__ == "__main__":
    print("🔧 Fragmented PDF Text Cleaning Fix - Test Suite")
    print("=" * 80)
    
    # Run basic tests
    basic_tests_passed = test_fragmented_text_cleaning()
    
    # Run real-world example test
    real_world_passed = test_real_world_example()
    
    print(f"\n🏆 FINAL RESULT")
    print("=" * 80)
    if basic_tests_passed and real_world_passed:
        print("✅ ALL TESTS PASSED!")
        print("\n🚀 The fragmented PDF text cleaning fix is ready for deployment.")
        print("   The specific PDF that was extracting nothing should now work correctly.")
        print("   Both inventors should be extractable after this fix.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("   The fix needs further refinement before deployment.")
    
    print("\n📋 Next Steps:")
    print("   1. Deploy the updated llm.py with the clean_fragmented_text() function")
    print("   2. Test with the actual problematic PDF")
    print("   3. Verify that both inventors are now extracted correctly")
    print("   4. Compare results with the DOCX version to ensure consistency")