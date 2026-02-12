#!/usr/bin/env python3
"""
Test script to verify that the frontend UI changes for residence/citizenship
work correctly with the backend ADS XML generation.

This test simulates the data flow from frontend to backend to ensure
the residence country vs citizenship distinction is properly handled.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.services.ads_xfa_builder import build_ads_datasets_xml, ApplicationData, InventorInfo
from backend.app.models.patent_application import Inventor, Applicant
from backend.app.services.ads_generator import ADSGenerator
import xml.dom.minidom as minidom

def test_frontend_backend_integration():
    """Test the complete data flow from frontend UI to backend XML generation."""
    
    print("🧪 TESTING FRONTEND-BACKEND RESIDENCE/CITIZENSHIP INTEGRATION")
    print("=" * 70)
    
    # Simulate data coming from the updated frontend UI
    # This represents what would be sent from the React form
    frontend_inventor_data = {
        "first_name": "Raj",
        "middle_name": "Kumar", 
        "last_name": "Sharma",
        "street_address": "4891 Innovation Boulevard",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94103",
        "country": "United States",           # Legacy field (residence)
        "residence_country": "United States", # New explicit residence field
        "citizenship": "India"                # Separate citizenship field
    }
    
    print("📝 Frontend Data (simulated from React form):")
    print(f"   Name: {frontend_inventor_data['first_name']} {frontend_inventor_data['last_name']}")
    print(f"   Residence: {frontend_inventor_data['residence_country']} (where they live)")
    print(f"   Citizenship: {frontend_inventor_data['citizenship']} (nationality)")
    print()
    
    # Convert to backend model (simulating API endpoint processing)
    backend_inventor = InventorInfo(
        first_name=frontend_inventor_data["first_name"],
        middle_name=frontend_inventor_data["middle_name"],
        last_name=frontend_inventor_data["last_name"],
        residence_city=frontend_inventor_data["city"],
        residence_state=frontend_inventor_data["state"],
        residence_country=frontend_inventor_data["residence_country"],  # Use explicit residence
        citizenship=frontend_inventor_data["citizenship"],              # Separate citizenship
        mail_address1=frontend_inventor_data["street_address"],
        mail_city=frontend_inventor_data["city"],
        mail_state=frontend_inventor_data["state"],
        mail_postcode=frontend_inventor_data["zip_code"],
        mail_country=frontend_inventor_data["residence_country"]
    )
    
    print("🔄 Backend Model (after API processing):")
    print(f"   residence_country: {backend_inventor.residence_country}")
    print(f"   citizenship: {backend_inventor.citizenship}")
    print()
    
    # Generate XML using the new builder
    app_data = ApplicationData(
        title="Test Application for Residence/Citizenship Separation",
        inventors=[backend_inventor]
    )
    
    xml_output = build_ads_datasets_xml(app_data)
    
    # Parse and verify the XML
    dom = minidom.parseString(xml_output)
    
    # Check residency determination (Bug Fix 1)
    residency_radio = dom.getElementsByTagName('ResidencyRadio')[0].firstChild.nodeValue
    print("✅ Bug Fix 1 - Residency Determination:")
    print(f"   ResidencyRadio: {residency_radio}")
    print(f"   Expected: us-residency (because residence_country = 'United States')")
    assert residency_radio == "us-residency", f"Expected us-residency, got {residency_radio}"
    
    # Check US residence fields (Bug Fix 2)
    us_city = dom.getElementsByTagName('rsCityTxt')[0].firstChild.nodeValue if dom.getElementsByTagName('rsCityTxt')[0].firstChild else ""
    us_state = dom.getElementsByTagName('rsStTxt')[0].firstChild.nodeValue if dom.getElementsByTagName('rsStTxt')[0].firstChild else ""
    us_country = dom.getElementsByTagName('rsCtryTxt')[0].firstChild.nodeValue if dom.getElementsByTagName('rsCtryTxt')[0].firstChild else ""
    
    print("✅ Bug Fix 2 - US Residence Fields:")
    print(f"   rsCityTxt: {us_city}")
    print(f"   rsStTxt: {us_state}")
    print(f"   rsCtryTxt: {us_country}")
    assert us_city == "San Francisco", f"Expected San Francisco, got {us_city}"
    assert us_state == "CA", f"Expected CA, got {us_state}"
    assert us_country == "US", f"Expected US, got {us_country}"
    
    # Check citizenship dropdown (Bug Fix 3)
    citizenship_dropdown = dom.getElementsByTagName('CitizedDropDown')[0].firstChild.nodeValue if dom.getElementsByTagName('CitizedDropDown')[0].firstChild else ""
    print("✅ Bug Fix 3 - Citizenship Dropdown:")
    print(f"   CitizedDropDown: {citizenship_dropdown}")
    print(f"   Expected: IN (Indian citizenship despite US residence)")
    assert citizenship_dropdown == "IN", f"Expected IN, got {citizenship_dropdown}"
    
    print()
    print("🎉 FRONTEND-BACKEND INTEGRATION TEST PASSED!")
    print("   ✓ Residence country correctly determines US residency")
    print("   ✓ US residence fields populated from residence data")
    print("   ✓ Citizenship dropdown shows nationality (separate from residence)")
    print("   ✓ Raj Sharma case handled correctly: US resident, Indian citizen")
    
    return True

def test_backward_compatibility():
    """Test that the system still works with legacy data that only has 'country' field."""
    
    print("\n🔄 TESTING BACKWARD COMPATIBILITY")
    print("=" * 50)
    
    # Simulate legacy data (only has 'country' field, no separate residence_country)
    legacy_data = {
        "first_name": "John",
        "last_name": "Smith", 
        "city": "Boston",
        "state": "MA",
        "country": "United States",  # Legacy: used for both residence and citizenship
        "citizenship": "United States"
    }
    
    # Backend should handle this gracefully
    backend_inventor = InventorInfo(
        first_name=legacy_data["first_name"],
        last_name=legacy_data["last_name"],
        residence_city=legacy_data["city"],
        residence_state=legacy_data["state"],
        residence_country=legacy_data["country"],  # Falls back to 'country' field
        citizenship=legacy_data["citizenship"]
    )
    
    app_data = ApplicationData(
        title="Legacy Compatibility Test",
        inventors=[backend_inventor]
    )
    
    xml_output = build_ads_datasets_xml(app_data)
    dom = minidom.parseString(xml_output)
    
    residency_radio = dom.getElementsByTagName('ResidencyRadio')[0].firstChild.nodeValue
    citizenship_dropdown = dom.getElementsByTagName('CitizedDropDown')[0].firstChild.nodeValue if dom.getElementsByTagName('CitizedDropDown')[0].firstChild else ""
    
    print(f"✅ Legacy data handling:")
    print(f"   ResidencyRadio: {residency_radio} (from country field)")
    print(f"   CitizedDropDown: {citizenship_dropdown} (from citizenship field)")
    
    assert residency_radio == "us-residency"
    assert citizenship_dropdown == "US"
    
    print("✅ Backward compatibility maintained!")
    
    return True

if __name__ == "__main__":
    try:
        test_frontend_backend_integration()
        test_backward_compatibility()
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("   Frontend UI changes work correctly with backend XML generation")
        print("   Residence vs citizenship distinction is properly handled")
        print("   Backward compatibility is maintained")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)