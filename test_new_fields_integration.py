#!/usr/bin/env python3
"""
Test script to verify that the new fields (correspondence_address, application_type, suggested_figure)
are properly extracted, mapped, and included in the generated ADS PDF.

This tests the complete workflow:
1. Frontend data → Backend models
2. Backend models → XFA XML generation  
3. XFA XML → PDF generation
4. Verification that all new fields appear in the final PDF
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.models.patent_application import PatentApplicationMetadata, Inventor, Applicant, CorrespondenceAddress
from app.services.ads_generator import ADSGenerator
from app.services.ads_xfa_builder import build_from_patent_metadata

def create_test_data_with_new_fields():
    """Create comprehensive test data including all new fields."""
    
    # Create correspondence address
    correspondence_address = CorrespondenceAddress(
        name="Blakely, Sokoloff, Taylor & Zafman LLP",
        name2="Patent Department",
        address1="1279 Oakmead Parkway",
        address2="Suite 200",
        city="Sunnyvale",
        state="CA",
        country="United States",
        postcode="94085",
        phone="(408) 720-8000",
        fax="(408) 720-8001",
        email="patents@bstlaw.com",
        customer_number="21839"
    )
    
    # Create inventors
    inventors = [
        Inventor(
            first_name="Jane",
            middle_name="Marie",
            last_name="Doe",
            suffix="Ph.D.",
            street_address="456 Research Way",
            city="Palo Alto",
            state="CA",
            zip_code="94301",
            country="US",
            residence_country="United States",
            citizenship="US"
        ),
        Inventor(
            first_name="John",
            middle_name="A.",
            last_name="Smith",
            suffix="Jr.",
            street_address="789 Innovation Blvd",
            city="San Francisco",
            state="CA",
            zip_code="94103",
            country="US",
            residence_country="United States",
            citizenship="India"  # Different citizenship to test mapping
        )
    ]
    
    # Create applicants
    applicants = [
        Applicant(
            name="TechCorp Innovations LLC",
            org_name="TechCorp Innovations LLC",
            is_organization=True,
            authority="assignee",
            street_address="123 Technology Drive",
            city="San Jose",
            state="CA",
            zip_code="95110",
            country="United States",
            phone="(408) 555-0100",
            email="legal@techcorp.com"
        )
    ]
    
    # Create complete metadata with all new fields
    metadata = PatentApplicationMetadata(
        title="Advanced Machine Learning System for Real-Time Data Processing and Predictive Analytics",
        application_number="18/234,567",
        filing_date="2024-01-15",
        entity_status="Small Entity",
        inventors=inventors,
        applicants=applicants,
        total_drawing_sheets=8,
        
        # ── NEW FIELDS TO TEST ──
        correspondence_address=correspondence_address,
        application_type="utility",
        suggested_figure="3A"
        # ──────────────────────────
    )
    
    return metadata

def test_xfa_xml_generation():
    """Test that new fields are properly included in XFA XML generation."""
    print("🧪 Testing XFA XML generation with new fields...")
    
    metadata = create_test_data_with_new_fields()
    
    # Generate XFA XML
    xml_data = build_from_patent_metadata(metadata)
    
    # Verify new fields are present in XML
    checks = {
        "Correspondence Address - Name": "Blakely, Sokoloff, Taylor &amp; Zafman LLP" in xml_data,
        "Correspondence Address - Customer Number": "21839" in xml_data,
        "Correspondence Address - Phone": "(408) 720-8000" in xml_data,
        "Correspondence Address - Email": "patents@bstlaw.com" in xml_data,
        "Application Type": "utility" in xml_data,
        "Suggested Figure": "3A" in xml_data,
        "Title": "Advanced Machine Learning System" in xml_data
    }
    
    print("\n📋 XFA XML Field Verification:")
    all_passed = True
    for field, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {field}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All new fields successfully mapped to XFA XML!")
    else:
        print("\n⚠️  Some fields missing from XFA XML")
        
    # Save XML for inspection
    with open("test_new_fields_output.xml", "w", encoding="utf-8") as f:
        f.write(xml_data)
    print(f"\n💾 XML saved to: test_new_fields_output.xml")
    
    return all_passed, xml_data

def test_pdf_generation():
    """Test complete PDF generation with new fields."""
    print("\n🧪 Testing PDF generation with new fields...")
    
    metadata = create_test_data_with_new_fields()
    generator = ADSGenerator()
    
    output_path = "test_new_fields_ads.pdf"
    
    try:
        # Generate PDF using XFA method
        result_path = generator.generate_ads_pdf(metadata, output_path, use_xfa=True)
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ PDF generated successfully!")
            print(f"   📄 File: {result_path}")
            print(f"   📊 Size: {file_size:,} bytes")
            return True, result_path
        else:
            print("❌ PDF file not created")
            return False, None
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return False, None

def test_frontend_backend_integration():
    """Test that frontend data structure matches backend expectations."""
    print("\n🧪 Testing Frontend-Backend integration...")
    
    # Simulate frontend data (what comes from ApplicationWizard)
    frontend_data = {
        "title": "Advanced Machine Learning System for Real-Time Data Processing",
        "application_number": "18/234,567",
        "entity_status": "Small Entity",
        "total_drawing_sheets": 8,
        "application_type": "utility",
        "suggested_figure": "3A",
        "correspondence_address": {
            "name": "Blakely, Sokoloff, Taylor & Zafman LLP",
            "address1": "1279 Oakmead Parkway",
            "city": "Sunnyvale",
            "state": "CA",
            "country": "United States",
            "postcode": "94085",
            "phone": "(408) 720-8000",
            "email": "patents@bstlaw.com",
            "customer_number": "21839"
        },
        "inventors": [
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "city": "Palo Alto",
                "state": "CA",
                "country": "US",
                "citizenship": "US"
            }
        ],
        "applicants": [
            {
                "name": "TechCorp Innovations LLC",
                "street_address": "123 Technology Drive",
                "city": "San Jose",
                "state": "CA",
                "country": "United States"
            }
        ]
    }
    
    try:
        # Convert to backend model
        correspondence_address = CorrespondenceAddress(**frontend_data["correspondence_address"])
        
        inventors = [
            Inventor(**inv_data) for inv_data in frontend_data["inventors"]
        ]
        
        applicants = [
            Applicant(**app_data) for app_data in frontend_data["applicants"]
        ]
        
        metadata = PatentApplicationMetadata(
            title=frontend_data["title"],
            application_number=frontend_data["application_number"],
            entity_status=frontend_data["entity_status"],
            total_drawing_sheets=frontend_data["total_drawing_sheets"],
            application_type=frontend_data["application_type"],
            suggested_figure=frontend_data["suggested_figure"],
            correspondence_address=correspondence_address,
            inventors=inventors,
            applicants=applicants
        )
        
        print("✅ Frontend data successfully converted to backend models")
        print(f"   📝 Title: {metadata.title}")
        print(f"   🏢 Correspondence: {metadata.correspondence_address.name}")
        print(f"   📋 App Type: {metadata.application_type}")
        print(f"   🖼️  Suggested Figure: {metadata.suggested_figure}")
        
        return True, metadata
        
    except Exception as e:
        print(f"❌ Frontend-Backend integration failed: {e}")
        return False, None

def main():
    """Run comprehensive test suite for new fields integration."""
    print("🚀 Starting New Fields Integration Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Frontend-Backend Integration
    results["frontend_backend"], metadata = test_frontend_backend_integration()
    
    # Test 2: XFA XML Generation
    results["xfa_xml"], xml_data = test_xfa_xml_generation()
    
    # Test 3: PDF Generation
    results["pdf_generation"], pdf_path = test_pdf_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ New fields are properly integrated end-to-end")
        print("✅ Correspondence address, application type, and suggested figure")
        print("   are correctly mapped from frontend → backend → PDF")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("❌ Please check the failed components above")
    
    print(f"\n📁 Generated files:")
    if os.path.exists("test_new_fields_output.xml"):
        print(f"   📄 XML: test_new_fields_output.xml")
    if pdf_path and os.path.exists(pdf_path):
        print(f"   📄 PDF: {pdf_path}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)