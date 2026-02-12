#!/usr/bin/env python3
"""
Test our ADS extraction fixes with a complex PDF containing:
- Middle names: Michael, Elizabeth, Wei
- Citizenship data: United States
- Total drawing sheets: 8
- Entity status: Small Entity
"""

import asyncio
import sys
sys.path.append('backend')
from app.services.llm import LLMService

async def test_complex_extraction():
    print("🧪 Testing ADS Extraction Fixes with Complex PDF")
    print("=" * 60)
    
    llm = LLMService()
    
    # Test with our complex PDF
    print("📄 Testing with: tests/complex_ads_test.pdf")
    print("   Expected data:")
    print("   - Middle names: Michael, Elizabeth, Wei")
    print("   - Citizenship: United States (all inventors)")
    print("   - Total Drawing Sheets: 8")
    print("   - Entity Status: Small Entity")
    print("   - 3 inventors with complete data")
    
    print("\n🔍 Running extraction...")
    result = await llm.analyze_cover_sheet('tests/complex_ads_test.pdf')
    
    print("\n📊 EXTRACTION RESULTS:")
    print("=" * 30)
    print(f"Title: {result.title}")
    print(f"Application Number: {result.application_number}")
    print(f"Entity Status: {result.entity_status}")
    print(f"Total Drawing Sheets: {result.total_drawing_sheets}")
    print(f"Number of Inventors: {len(result.inventors)}")
    
    print(f"\n👥 INVENTOR DETAILS:")
    print("=" * 30)
    for i, inv in enumerate(result.inventors, 1):
        middle = inv.middle_name if inv.middle_name else "(no middle)"
        citizenship = inv.citizenship if inv.citizenship else "(missing)"
        
        print(f"Inventor {i}:")
        print(f"  Name: {inv.first_name} {middle} {inv.last_name}")
        print(f"  Citizenship: {citizenship}")
        print(f"  Address: {inv.street_address}")
        print(f"  City/State: {inv.city}, {inv.state}")
        print()
    
    print("🔍 VALIDATION CHECKS:")
    print("=" * 30)
    
    # Check 1: Entity Status
    if result.entity_status == "Small Entity":
        print("✅ Entity Status: CORRECT - 'Small Entity'")
    else:
        print(f"❌ Entity Status: Expected 'Small Entity', got '{result.entity_status}'")
    
    # Check 2: Total Drawing Sheets
    if result.total_drawing_sheets == 8:
        print("✅ Total Drawing Sheets: CORRECT - 8")
    else:
        print(f"❌ Total Drawing Sheets: Expected 8, got '{result.total_drawing_sheets}'")
    
    # Check 3: Middle Names (no truncation)
    middle_names = [inv.middle_name for inv in result.inventors if inv.middle_name]
    expected_middles = ["Michael", "Elizabeth", "Wei"]
    
    print(f"\n📝 Middle Name Analysis:")
    for i, inv in enumerate(result.inventors):
        expected = expected_middles[i] if i < len(expected_middles) else "None"
        actual = inv.middle_name or "None"
        
        if actual == expected:
            print(f"✅ Inventor {i+1}: Expected '{expected}', got '{actual}' - CORRECT")
        else:
            print(f"❌ Inventor {i+1}: Expected '{expected}', got '{actual}' - ISSUE")
            if len(actual) < len(expected) and expected.startswith(actual):
                print(f"   ⚠️  Possible truncation: '{actual}' vs '{expected}'")
    
    # Check 4: Citizenship
    citizenship_count = sum(1 for inv in result.inventors if inv.citizenship == "United States")
    total_inventors = len(result.inventors)
    
    if citizenship_count == total_inventors and citizenship_count > 0:
        print(f"✅ Citizenship: ALL {citizenship_count} inventors have 'United States' - CORRECT")
    else:
        print(f"❌ Citizenship: Expected all inventors to have 'United States'")
        print(f"   Got: {citizenship_count}/{total_inventors} with correct citizenship")
        for i, inv in enumerate(result.inventors, 1):
            print(f"   Inventor {i}: {inv.citizenship or 'MISSING'}")
    
    # Check 5: Complete extraction
    if result.title and "Quantum" in result.title:
        print("✅ Title: Contains 'Quantum' - CORRECT")
    else:
        print(f"❌ Title: Expected to contain 'Quantum', got '{result.title}'")
    
    print(f"\n🎯 SUMMARY:")
    print("=" * 20)
    
    fixes_working = []
    fixes_issues = []
    
    if result.entity_status == "Small Entity":
        fixes_working.append("Entity Status")
    else:
        fixes_issues.append("Entity Status")
    
    if result.total_drawing_sheets == 8:
        fixes_working.append("Total Drawing Sheets")
    else:
        fixes_issues.append("Total Drawing Sheets")
    
    if citizenship_count == total_inventors and citizenship_count > 0:
        fixes_working.append("Citizenship Data")
    else:
        fixes_issues.append("Citizenship Data")
    
    # Check for middle name truncation by comparing with expected values
    expected_middles = ["Michael", "Elizabeth", "Wei"]
    middle_names_correct = True
    
    for i, inv in enumerate(result.inventors):
        if i < len(expected_middles):
            expected = expected_middles[i]
            actual = inv.middle_name or ""
            if actual != expected:
                middle_names_correct = False
                break
    
    if middle_names_correct:
        fixes_working.append("Middle Name Preservation")
    else:
        fixes_issues.append("Middle Name Truncation")
    
    print(f"✅ WORKING FIXES: {', '.join(fixes_working) if fixes_working else 'None'}")
    print(f"❌ ISSUES REMAINING: {', '.join(fixes_issues) if fixes_issues else 'None'}")
    
    if not fixes_issues:
        print("\n🎉 ALL FIXES ARE WORKING PERFECTLY!")
    else:
        print(f"\n⚠️  {len(fixes_issues)} issue(s) need attention")

if __name__ == "__main__":
    asyncio.run(test_complex_extraction())