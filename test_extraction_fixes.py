#!/usr/bin/env python3
"""
Test script to validate ADS extraction fixes for:
1. Middle name truncation issues
2. Missing citizenship data
3. Missing total drawing sheets
4. Missing entity status
5. Suffix field handling
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.llm import LLMService
from app.services.enhanced_extraction_service import EnhancedExtractionService
from app.models.patent_application import PatentApplicationMetadata

async def test_extraction_fixes():
    """Test the extraction fixes with a sample PDF"""
    
    print("🔧 Testing ADS Extraction Fixes")
    print("=" * 50)
    
    # Initialize services
    llm_service = LLMService()
    enhanced_service = EnhancedExtractionService(llm_service)
    
    # Test file path (you'll need to provide a sample PDF)
    test_pdf_path = "tests/standard.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF not found: {test_pdf_path}")
        print("Please provide a sample ADS PDF for testing")
        return
    
    try:
        print(f"📄 Testing with: {test_pdf_path}")
        print("\n1. Testing Enhanced Extraction Service...")
        
        # Test enhanced extraction
        enhanced_result = await enhanced_service.extract_with_two_step_process(
            file_path=test_pdf_path,
            document_type="patent_application"
        )
        
        print("\n✅ Enhanced Extraction Results:")
        print(f"   Title: {enhanced_result.title}")
        print(f"   Application Number: {enhanced_result.application_number}")
        print(f"   Entity Status: {enhanced_result.entity_status}")
        print(f"   Total Drawing Sheets: {enhanced_result.total_drawing_sheets}")
        
        print(f"\n👥 Inventors ({len(enhanced_result.inventors)}):")
        for i, inventor in enumerate(enhanced_result.inventors, 1):
            print(f"   {i}. {inventor.given_name} {inventor.middle_name or ''} {inventor.family_name}")
            print(f"      Citizenship: {inventor.citizenship}")
            print(f"      Address: {inventor.street_address}, {inventor.city}, {inventor.state}")
            print(f"      Confidence: {inventor.confidence_score}")
        
        print(f"\n🏢 Applicants ({len(enhanced_result.applicants)}):")
        for i, applicant in enumerate(enhanced_result.applicants, 1):
            print(f"   {i}. {applicant.organization_name or 'Individual'}")
            print(f"      Address: {applicant.street_address}, {applicant.city}, {applicant.state}")
        
        print("\n2. Testing Legacy LLM Service...")
        
        # Test legacy extraction for comparison
        legacy_result = await llm_service.analyze_cover_sheet(test_pdf_path)
        
        print("\n✅ Legacy Extraction Results:")
        print(f"   Title: {legacy_result.title}")
        print(f"   Application Number: {legacy_result.application_number}")
        print(f"   Entity Status: {legacy_result.entity_status}")
        print(f"   Total Drawing Sheets: {legacy_result.total_drawing_sheets}")
        
        print(f"\n👥 Inventors ({len(legacy_result.inventors)}):")
        for i, inventor in enumerate(legacy_result.inventors, 1):
            print(f"   {i}. {inventor.first_name} {inventor.middle_name or ''} {inventor.last_name}")
            print(f"      Citizenship: {inventor.citizenship}")
            print(f"      Address: {inventor.street_address}, {inventor.city}, {inventor.state}")
        
        # Validation checks
        print("\n🔍 Validation Checks:")
        print("=" * 30)
        
        # Check 1: Middle name truncation
        middle_name_issues = []
        for inventor in enhanced_result.inventors:
            if inventor.middle_name and len(inventor.middle_name) < 4:
                middle_name_issues.append(f"{inventor.given_name} {inventor.middle_name}")
        
        if middle_name_issues:
            print(f"⚠️  Potential middle name truncation: {middle_name_issues}")
        else:
            print("✅ No middle name truncation detected")
        
        # Check 2: Missing citizenship
        missing_citizenship = []
        for inventor in enhanced_result.inventors:
            if not inventor.citizenship:
                missing_citizenship.append(f"{inventor.given_name} {inventor.family_name}")
        
        if missing_citizenship:
            print(f"⚠️  Missing citizenship for: {missing_citizenship}")
        else:
            print("✅ All inventors have citizenship data")
        
        # Check 3: Entity status
        if not enhanced_result.entity_status:
            print("⚠️  Entity status is missing")
        else:
            print(f"✅ Entity status found: {enhanced_result.entity_status}")
        
        # Check 4: Total drawing sheets
        if not enhanced_result.total_drawing_sheets:
            print("⚠️  Total drawing sheets is missing")
        else:
            print(f"✅ Total drawing sheets found: {enhanced_result.total_drawing_sheets}")
        
        # Save results for inspection
        results = {
            "enhanced_extraction": {
                "title": enhanced_result.title,
                "application_number": enhanced_result.application_number,
                "entity_status": enhanced_result.entity_status,
                "total_drawing_sheets": enhanced_result.total_drawing_sheets,
                "inventors": [
                    {
                        "given_name": inv.given_name,
                        "middle_name": inv.middle_name,
                        "family_name": inv.family_name,
                        "citizenship": inv.citizenship,
                        "street_address": inv.street_address,
                        "city": inv.city,
                        "state": inv.state,
                        "confidence_score": inv.confidence_score
                    }
                    for inv in enhanced_result.inventors
                ],
                "applicants": [
                    {
                        "organization_name": app.organization_name,
                        "street_address": app.street_address,
                        "city": app.city,
                        "state": app.state
                    }
                    for app in enhanced_result.applicants
                ]
            },
            "legacy_extraction": {
                "title": legacy_result.title,
                "application_number": legacy_result.application_number,
                "entity_status": legacy_result.entity_status,
                "total_drawing_sheets": legacy_result.total_drawing_sheets,
                "inventors": [
                    {
                        "first_name": inv.first_name,
                        "middle_name": inv.middle_name,
                        "last_name": inv.last_name,
                        "citizenship": inv.citizenship,
                        "street_address": inv.street_address,
                        "city": inv.city,
                        "state": inv.state
                    }
                    for inv in legacy_result.inventors
                ]
            }
        }
        
        with open("extraction_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: extraction_test_results.json")
        print("\n🎉 Testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main entry point"""
    print("🚀 Starting ADS Extraction Fix Testing...")
    asyncio.run(test_extraction_fixes())

if __name__ == "__main__":
    main()