#!/usr/bin/env python3
"""
Test script to verify that applicant/company data extraction is working correctly.
"""

import sys
import os
import asyncio
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.llm import LLMService
from app.models.patent_application import PatentApplicationMetadata

async def test_extraction_schema():
    """Test that the extraction schemas include applicant information."""
    
    print("🧪 Testing Applicant/Company Data Extraction Enhancement")
    print("=" * 60)
    
    # Test 1: Check if schemas include applicant field
    llm_service = LLMService()
    
    # Create a mock text content that includes applicant information
    mock_text_content = """
    --- FORM FIELD DATA ---
    Title: Advanced AI System for Patent Processing
    ApplicationNumber: 18/123,456
    EntityStatus: Small Entity
    GivenName_1: John
    FamilyName_1: Doe
    Address_1: 123 Inventor St, Tech City, CA 90210
    ApplicantName: TechCorp Industries Inc
    CompanyAddress: 456 Business Ave, Corporate City, CA 94105
    CompanyCity: Corporate City
    CompanyState: CA
    CompanyZip: 94105
    CompanyCountry: USA
    --- END FORM DATA ---
    """
    
    print("📝 Testing text-only extraction with applicant data...")
    
    try:
        # Test the _analyze_text_only method
        result = await llm_service._analyze_text_only(mock_text_content)
        
        print(f"✅ Extraction completed successfully!")
        print(f"📊 Results:")
        print(f"   - Title: {result.title}")
        print(f"   - Application Number: {result.application_number}")
        print(f"   - Entity Status: {result.entity_status}")
        print(f"   - Inventors Count: {len(result.inventors) if result.inventors else 0}")
        print(f"   - Applicant: {result.applicant}")
        
        if result.applicant:
            print(f"   - Applicant Name: {result.applicant.name}")
            print(f"   - Applicant Address: {result.applicant.street_address}")
            print(f"   - Applicant City: {result.applicant.city}")
            print(f"   - Applicant State: {result.applicant.state}")
            print(f"   - Applicant ZIP: {result.applicant.zip_code}")
            print(f"   - Applicant Country: {result.applicant.country}")
        
        # Validate that applicant data was extracted
        if result.applicant and result.applicant.name:
            print("✅ SUCCESS: Applicant data extraction is working!")
            return True
        else:
            print("❌ ISSUE: Applicant data was not extracted")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Extraction failed with error: {e}")
        return False

async def test_csv_applicant_parsing():
    """Test CSV applicant parsing functionality."""
    
    print("\n📁 Testing CSV Applicant Parsing...")
    
    from app.services.csv_handler import parse_applicant_csv
    
    # Test CSV with applicant data
    test_csv = """company_name,company_address,company_city,company_state,company_zip,company_country
TechCorp Industries Inc,456 Business Ave,Corporate City,CA,94105,USA
"""
    
    try:
        applicant = parse_applicant_csv(test_csv.encode('utf-8'))
        
        if applicant:
            print(f"✅ CSV Applicant parsing successful!")
            print(f"   - Name: {applicant.name}")
            print(f"   - Address: {applicant.street_address}")
            print(f"   - City: {applicant.city}")
            print(f"   - State: {applicant.state}")
            print(f"   - ZIP: {applicant.zip_code}")
            print(f"   - Country: {applicant.country}")
            return True
        else:
            print("❌ ISSUE: No applicant data parsed from CSV")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: CSV parsing failed with error: {e}")
        return False

async def main():
    """Run all tests."""
    
    print("🚀 Starting Applicant/Company Data Extraction Tests")
    print("=" * 60)
    
    # Test 1: LLM Extraction
    extraction_success = await test_extraction_schema()
    
    # Test 2: CSV Parsing
    csv_success = await test_csv_applicant_parsing()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"LLM Extraction Test: {'✅ PASS' if extraction_success else '❌ FAIL'}")
    print(f"CSV Parsing Test: {'✅ PASS' if csv_success else '❌ FAIL'}")
    
    if extraction_success and csv_success:
        print("\n🎉 ALL TESTS PASSED! Applicant/Company data extraction is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)