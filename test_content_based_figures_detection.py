#!/usr/bin/env python3
"""
Test Content-Based Figures PDF Detection

This test verifies that the updated is_figures_pdf() function correctly
identifies figures PDFs based on content rather than filename.
"""

import sys
import os
import io
import fitz  # PyMuPDF

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.jobs import is_figures_pdf, count_pdf_pages

def create_test_pdf_with_text(text_content: str) -> bytes:
    """Create a PDF with the specified text content."""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add text to the page
    text_rect = fitz.Rect(50, 50, 500, 700)
    page.insert_textbox(text_rect, text_content, fontsize=12)
    
    # Convert to bytes
    pdf_bytes = doc.tobytes()
    doc.close()
    
    return pdf_bytes

def create_test_pdf_minimal_text() -> bytes:
    """Create a PDF with minimal text (simulating figures PDF)."""
    return create_test_pdf_with_text("Figure 1\nPage 1")

def create_test_pdf_substantial_text() -> bytes:
    """Create a PDF with substantial text (simulating cover sheet)."""
    text = """
    PATENT APPLICATION DATA SHEET
    
    TITLE OF INVENTION:
    SYSTEM AND METHOD FOR VIRTUAL REALITY INTERACTION
    
    INVENTOR INFORMATION:
    
    INVENTOR 1:
    DAVID CHEN
    123 MAIN STREET
    VANCOUVER, BC V6B 1A1 (CA)
    
    INVENTOR 2:
    SARAH WILSON
    456 OAK AVENUE
    SEATTLE, WA 98101 (US)
    
    APPLICANT INFORMATION:
    TECH INNOVATIONS CORP.
    789 SILICON VALLEY BLVD
    PALO ALTO, CA 94301 (US)
    
    ABSTRACT:
    A system and method for virtual reality interaction that enables
    users to interact with virtual objects using natural hand gestures
    and voice commands. The system includes sensors for tracking user
    movements and a processing unit for interpreting gestures.
    """
    return create_test_pdf_with_text(text)

def test_content_based_detection():
    """Test the content-based figures detection."""
    print("🧪 Testing Content-Based Figures PDF Detection")
    print("=" * 60)
    
    # Test 1: Minimal text PDF (should be detected as figures)
    print("\n📋 Test 1: Minimal Text PDF (Figures)")
    minimal_pdf = create_test_pdf_minimal_text()
    is_figures_minimal = is_figures_pdf(minimal_pdf)
    page_count_minimal = count_pdf_pages(minimal_pdf)
    
    print(f"   PDF Size: {len(minimal_pdf)} bytes")
    print(f"   Page Count: {page_count_minimal}")
    print(f"   Detected as Figures: {is_figures_minimal}")
    print(f"   Expected: True")
    print(f"   Result: {'✅ PASS' if is_figures_minimal else '❌ FAIL'}")
    
    # Test 2: Substantial text PDF (should NOT be detected as figures)
    print("\n📋 Test 2: Substantial Text PDF (Cover Sheet)")
    substantial_pdf = create_test_pdf_substantial_text()
    is_figures_substantial = is_figures_pdf(substantial_pdf)
    page_count_substantial = count_pdf_pages(substantial_pdf)
    
    print(f"   PDF Size: {len(substantial_pdf)} bytes")
    print(f"   Page Count: {page_count_substantial}")
    print(f"   Detected as Figures: {is_figures_substantial}")
    print(f"   Expected: False")
    print(f"   Result: {'✅ PASS' if not is_figures_substantial else '❌ FAIL'}")
    
    # Test 3: Edge case - exactly at threshold
    print("\n📋 Test 3: Edge Case - Custom Threshold")
    # Test with a lower threshold to see behavior
    is_figures_low_threshold = is_figures_pdf(substantial_pdf, min_text_threshold=100)
    print(f"   Substantial PDF with 100-char threshold: {is_figures_low_threshold}")
    print(f"   Expected: False (should still have >100 chars)")
    print(f"   Result: {'✅ PASS' if not is_figures_low_threshold else '❌ FAIL'}")
    
    # Test 4: Filename-based vs Content-based comparison
    print("\n📋 Test 4: Filename vs Content Comparison")
    
    # Simulate the old problem: filename suggests figures, but content suggests cover sheet
    problematic_filename = "File 2_ Two Inventors & Complex Figures.pdf"
    
    # Old logic (filename-based) - simulate what would happen
    old_logic_result = any(keyword in problematic_filename.lower() 
                          for keyword in ['figure', 'figures', 'drawing', 'drawings', 'fig', 'figs'])
    
    # New logic (content-based)
    new_logic_result = is_figures_pdf(substantial_pdf)
    
    print(f"   Filename: '{problematic_filename}'")
    print(f"   Old Logic (filename-based): {old_logic_result} ❌")
    print(f"   New Logic (content-based): {new_logic_result} ✅")
    print(f"   Improvement: {'✅ FIXED' if old_logic_result != new_logic_result else '❌ NO CHANGE'}")
    
    # Summary
    print("\n🏁 Test Summary")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    if is_figures_minimal:
        tests_passed += 1
    if not is_figures_substantial:
        tests_passed += 1
    if not is_figures_low_threshold:
        tests_passed += 1
    if old_logic_result != new_logic_result:
        tests_passed += 1
    
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Content-based detection is working correctly.")
        print("\n✅ Benefits:")
        print("   • Figures PDFs with minimal text are correctly identified")
        print("   • Cover sheets with substantial text proceed to LLM extraction")
        print("   • No longer fooled by misleading filenames")
        print("   • More reliable than filename-based detection")
    else:
        print("❌ SOME TESTS FAILED! The implementation needs review.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    try:
        success = test_content_based_detection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)