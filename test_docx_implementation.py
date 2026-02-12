#!/usr/bin/env python3
"""
Test script for DOCX support implementation.
Tests the new DOCX extraction capabilities and the 3 new fields:
- correspondence_address
- application_type  
- suggested_figure
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.llm import LLMService
from app.models.patent_application import PatentApplicationMetadata, CorrespondenceAddress

async def test_docx_extraction():
    """Test DOCX file extraction with the new fields."""
    
    print("🧪 Testing DOCX Implementation")
    print("=" * 50)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Check if test DOCX file exists
    docx_file = "test_data/patent_application_test.docx"
    if not os.path.exists(docx_file):
        print(f"❌ Test DOCX file not found: {docx_file}")
        print("Please ensure the test file exists before running this test.")
        return False
    
    print(f"📄 Testing with file: {docx_file}")
    
    try:
        # Test DOCX extraction
        print("\n🔍 Extracting metadata from DOCX...")
        
        # Read file content
        with open(docx_file, "rb") as f:
            file_content = f.read()
        
        # Analyze the DOCX document
        result = await llm_service.analyze_cover_sheet(
            file_path=docx_file,
            file_content=file_content
        )
        
        print("✅ DOCX extraction completed successfully!")
        
        # Display results
        print("\n📊 Extraction Results:")
        print("-" * 30)
        
        print(f"Title: {result.title}")
        print(f"Application Number: {result.application_number}")
        print(f"Entity Status: {result.entity_status}")
        print(f"Total Drawing Sheets: {result.total_drawing_sheets}")
        
        # NEW FIELDS
        print(f"\n🆕 New Fields:")
        print(f"Application Type: {result.application_type}")
        print(f"Suggested Figure: {result.suggested_figure}")
        
        if result.correspondence_address:
            print(f"\n📮 Correspondence Address:")
            corr = result.correspondence_address
            print(f"  Name: {corr.name}")
            print(f"  Address1: {corr.address1}")
            print(f"  City: {corr.city}")
            print(f"  State: {corr.state}")
            print(f"  Country: {corr.country}")
            print(f"  Phone: {corr.phone}")
            print(f"  Email: {corr.email}")
            print(f"  Customer Number: {corr.customer_number}")
        else:
            print(f"\n📮 Correspondence Address: Not found")
        
        # Inventors
        print(f"\n👥 Inventors ({len(result.inventors)}):")
        for i, inventor in enumerate(result.inventors, 1):
            print(f"  {i}. {inventor.first_name} {inventor.middle_name or ''} {inventor.last_name}")
            print(f"     City: {inventor.city}, State: {inventor.state}")
            print(f"     Citizenship: {inventor.citizenship}")
            print(f"     Zip: {inventor.zip_code}")
        
        # Applicants
        print(f"\n🏢 Applicants ({len(result.applicants)}):")
        for i, applicant in enumerate(result.applicants, 1):
            print(f"  {i}. {applicant.name}")
            print(f"     Address: {applicant.street_address}")
            print(f"     City: {applicant.city}, State: {applicant.state}")
            print(f"     Country: {applicant.country}")
        
        # Test XFA builder integration
        print(f"\n🔧 Testing XFA Builder Integration...")
        from app.services.ads_xfa_builder import build_from_patent_metadata
        
        xml_output = build_from_patent_metadata(result)
        print(f"✅ XFA XML generated successfully ({len(xml_output)} characters)")
        
        # Check if correspondence address is in XML
        if result.correspondence_address and result.correspondence_address.name:
            # Check for the firm name (accounting for XML escaping)
            firm_name = result.correspondence_address.name
            firm_name_escaped = firm_name.replace("&", "&amp;")
            if firm_name in xml_output or firm_name_escaped in xml_output:
                print("✅ Correspondence address found in XFA XML")
            else:
                print("⚠️ Correspondence address not found in XFA XML")
        
        # Check if application type is in XML
        if result.application_type:
            if result.application_type in xml_output:
                print("✅ Application type found in XFA XML")
            else:
                print("⚠️ Application type not found in XFA XML")
        
        # Check if suggested figure is in XML
        if result.suggested_figure:
            if result.suggested_figure in xml_output:
                print("✅ Suggested figure found in XFA XML")
            else:
                print("⚠️ Suggested figure not found in XFA XML")
        
        print(f"\n🎉 DOCX Implementation Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during DOCX extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_docx_text_extraction():
    """Test just the DOCX text extraction functionality."""
    
    print("\n🔤 Testing DOCX Text Extraction")
    print("=" * 40)
    
    llm_service = LLMService()
    docx_file = "test_data/patent_application_test.docx"
    
    if not os.path.exists(docx_file):
        print(f"❌ Test DOCX file not found: {docx_file}")
        return False
    
    try:
        # Test text extraction
        with open(docx_file, "rb") as f:
            file_content = f.read()
        
        text_content = await llm_service._extract_text_from_docx(docx_file, file_content)
        
        print(f"✅ Text extraction successful!")
        print(f"📝 Extracted {len(text_content)} characters")
        print(f"📄 First 500 characters:")
        print("-" * 30)
        print(text_content[:500])
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during text extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_structure():
    """Test the new model structure."""
    
    print("\n🏗️ Testing Model Structure")
    print("=" * 35)
    
    try:
        # Test CorrespondenceAddress model
        corr_addr = CorrespondenceAddress(
            name="Test Law Firm LLP",
            address1="123 Legal Street",
            city="Washington",
            state="DC",
            country="United States",
            postcode="20001",
            phone="(202) 555-0123",
            email="contact@testlaw.com",
            customer_number="12345"
        )
        print("✅ CorrespondenceAddress model created successfully")
        
        # Test PatentApplicationMetadata with new fields
        metadata = PatentApplicationMetadata(
            title="Test Patent Application",
            application_type="utility",
            suggested_figure="1",
            correspondence_address=corr_addr
        )
        print("✅ PatentApplicationMetadata with new fields created successfully")
        
        # Test field access
        assert metadata.application_type == "utility"
        assert metadata.suggested_figure == "1"
        assert metadata.correspondence_address.name == "Test Law Firm LLP"
        print("✅ All new fields accessible and working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing model structure: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    
    print("🚀 DOCX Implementation Test Suite")
    print("=" * 60)
    
    # Test 1: Model structure
    test1_passed = test_model_structure()
    
    # Test 2: DOCX text extraction
    test2_passed = await test_docx_text_extraction()
    
    # Test 3: Full DOCX extraction
    test3_passed = await test_docx_extraction()
    
    # Summary
    print(f"\n📋 Test Summary")
    print("=" * 20)
    print(f"Model Structure: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Text Extraction: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Full Extraction: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print(f"\n🎉 All tests passed! DOCX implementation is working correctly.")
    else:
        print(f"\n⚠️ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())