#!/usr/bin/env python3
"""
Test script to verify the end-to-end workflow with the new fields:
- correspondence_address
- application_type  
- suggested_figure

This script tests:
1. DOCX upload and extraction
2. New fields are extracted correctly
3. Frontend can receive and display the data
4. ADS generation includes all new fields
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.llm import LLMService
from app.services.ads_xfa_builder import build_from_patent_metadata

async def test_end_to_end_workflow():
    """Test the complete workflow with new fields."""
    
    print("🧪 Testing End-to-End Workflow with New Fields")
    print("=" * 60)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test with the DOCX file
    docx_file = "test_data/patent_application_test.docx"
    
    if not os.path.exists(docx_file):
        print(f"❌ Test DOCX file not found: {docx_file}")
        return False
    
    try:
        print("📄 Step 1: Extract metadata from DOCX...")
        
        # Read file content
        with open(docx_file, "rb") as f:
            file_content = f.read()
        
        # Analyze the DOCX document (simulating backend extraction)
        result = await llm_service.analyze_cover_sheet(
            file_path=docx_file,
            file_content=file_content
        )
        
        print("✅ Extraction completed successfully!")
        
        # Step 2: Simulate frontend API response format
        print("\n📡 Step 2: Simulate API response format...")
        
        # Convert to frontend-compatible format
        frontend_data = {
            "title": result.title,
            "application_number": result.application_number,
            "entity_status": result.entity_status,
            "total_drawing_sheets": result.total_drawing_sheets,
            "application_type": result.application_type,
            "suggested_figure": result.suggested_figure,
            "correspondence_address": {
                "name": result.correspondence_address.name if result.correspondence_address else None,
                "address1": result.correspondence_address.address1 if result.correspondence_address else None,
                "city": result.correspondence_address.city if result.correspondence_address else None,
                "state": result.correspondence_address.state if result.correspondence_address else None,
                "country": result.correspondence_address.country if result.correspondence_address else None,
                "postcode": result.correspondence_address.postcode if result.correspondence_address else None,
                "phone": result.correspondence_address.phone if result.correspondence_address else None,
                "email": result.correspondence_address.email if result.correspondence_address else None,
                "customer_number": result.correspondence_address.customer_number if result.correspondence_address else None,
            } if result.correspondence_address else None,
            "inventors": [
                {
                    "first_name": inv.first_name,
                    "middle_name": inv.middle_name,
                    "last_name": inv.last_name,
                    "city": inv.city,
                    "state": inv.state,
                    "zip_code": inv.zip_code,
                    "country": inv.country,
                    "citizenship": inv.citizenship,
                    "street_address": inv.street_address
                }
                for inv in result.inventors
            ],
            "applicants": [
                {
                    "name": app.name,
                    "street_address": app.street_address,
                    "city": app.city,
                    "state": app.state,
                    "zip_code": app.zip_code,
                    "country": app.country
                }
                for app in result.applicants
            ]
        }
        
        print("✅ Frontend data format created")
        
        # Step 3: Display extracted data (simulating frontend display)
        print("\n📊 Step 3: Display extracted data (Frontend View)...")
        print("-" * 50)
        
        print(f"📋 Basic Information:")
        print(f"  Title: {frontend_data['title']}")
        print(f"  Application Number: {frontend_data['application_number']}")
        print(f"  Entity Status: {frontend_data['entity_status']}")
        print(f"  Total Drawing Sheets: {frontend_data['total_drawing_sheets']}")
        
        print(f"\n🆕 New Fields:")
        print(f"  Application Type: {frontend_data['application_type']}")
        print(f"  Suggested Figure: {frontend_data['suggested_figure']}")
        
        if frontend_data['correspondence_address']:
            print(f"\n📮 Correspondence Address:")
            corr = frontend_data['correspondence_address']
            print(f"  Name: {corr['name']}")
            print(f"  Address: {corr['address1']}")
            print(f"  City: {corr['city']}, {corr['state']} {corr['postcode']}")
            print(f"  Country: {corr['country']}")
            print(f"  Phone: {corr['phone']}")
            print(f"  Email: {corr['email']}")
            print(f"  Customer Number: {corr['customer_number']}")
        
        print(f"\n👥 Inventors ({len(frontend_data['inventors'])}):")
        for i, inv in enumerate(frontend_data['inventors'], 1):
            print(f"  {i}. {inv['first_name']} {inv['middle_name'] or ''} {inv['last_name']}")
            print(f"     {inv['city']}, {inv['state']} {inv['zip_code']}")
            print(f"     Citizenship: {inv['citizenship']}")
        
        print(f"\n🏢 Applicants ({len(frontend_data['applicants'])}):")
        for i, app in enumerate(frontend_data['applicants'], 1):
            print(f"  {i}. {app['name']}")
            print(f"     {app['street_address']}")
            print(f"     {app['city']}, {app['state']} {app['zip_code']}")
        
        # Step 4: Test ADS generation with new fields
        print(f"\n🔧 Step 4: Generate ADS XML with new fields...")
        
        xml_output = build_from_patent_metadata(result)
        print(f"✅ ADS XML generated successfully ({len(xml_output)} characters)")
        
        # Verify new fields are in XML
        verification_checks = [
            ("Application Type", result.application_type in xml_output if result.application_type else False),
            ("Suggested Figure", result.suggested_figure in xml_output if result.suggested_figure else False),
            ("Correspondence Name", result.correspondence_address.name.replace("&", "&amp;") in xml_output if result.correspondence_address and result.correspondence_address.name else False),
            ("Correspondence Address", result.correspondence_address.address1 in xml_output if result.correspondence_address and result.correspondence_address.address1 else False),
            ("Correspondence Phone", result.correspondence_address.phone in xml_output if result.correspondence_address and result.correspondence_address.phone else False),
        ]
        
        print(f"\n🔍 Step 5: Verify new fields in ADS XML...")
        all_verified = True
        for field_name, is_present in verification_checks:
            status = "✅" if is_present else "❌"
            print(f"  {status} {field_name}: {'Found' if is_present else 'Missing'}")
            if not is_present:
                all_verified = False
        
        # Step 6: Save test results
        print(f"\n💾 Step 6: Save test results...")
        
        test_results = {
            "extraction_successful": True,
            "frontend_data": frontend_data,
            "xml_length": len(xml_output),
            "verification_checks": {name: result for name, result in verification_checks},
            "all_fields_verified": all_verified
        }
        
        with open("test_frontend_new_fields_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        print(f"✅ Test results saved to: test_frontend_new_fields_results.json")
        
        # Final summary
        print(f"\n📈 Final Summary:")
        print(f"  ✅ DOCX Extraction: Success")
        print(f"  ✅ Frontend Data Format: Success")
        print(f"  ✅ New Fields Extracted: {len([c for c in verification_checks if c[1]])}/{len(verification_checks)}")
        print(f"  ✅ ADS XML Generation: Success")
        print(f"  {'✅' if all_verified else '⚠️'} All Fields in XML: {'Yes' if all_verified else 'Partial'}")
        
        if all_verified:
            print(f"\n🎉 End-to-End Workflow Test: PASSED")
            print(f"   The new fields are working correctly across the entire pipeline!")
        else:
            print(f"\n⚠️ End-to-End Workflow Test: PARTIAL")
            print(f"   Some fields may need additional verification.")
        
        return all_verified
        
    except Exception as e:
        print(f"❌ Error during workflow test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_end_to_end_workflow())
    sys.exit(0 if success else 1)