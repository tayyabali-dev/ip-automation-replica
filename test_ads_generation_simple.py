#!/usr/bin/env python3
"""
Simple test to isolate the ADS generation issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.patent_application import PatentApplicationMetadata, Inventor, Applicant
from app.services.ads_generator import ADSGenerator

def test_ads_generation():
    """Test ADS generation with minimal data."""
    
    print("🔍 Testing ADS Generation")
    print("=" * 40)
    
    # Create minimal test data
    test_data = PatentApplicationMetadata(
        title="Test Application",
        application_number="12/345,678",
        filing_date="2024-01-01",
        entity_status="Small Entity",
        inventors=[
            Inventor(
                first_name="John",
                last_name="Doe",
                street_address="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001",
                country="US",
                citizenship="US"
            )
        ],
        applicants=[],
        total_drawing_sheets=1
    )
    
    print("✅ Created test data")
    
    # Test ADS generator initialization
    try:
        ads_generator = ADSGenerator()
        print("✅ ADS generator initialized")
        
        # Check template paths
        print(f"📁 Template path: {ads_generator.template_path}")
        print(f"📁 XFA template path: {ads_generator.xfa_template_path}")
        
        template_exists = os.path.exists(ads_generator.template_path)
        xfa_template_exists = os.path.exists(ads_generator.xfa_template_path)
        
        print(f"📄 Template exists: {template_exists}")
        print(f"📄 XFA template exists: {xfa_template_exists}")
        
        if not template_exists and not xfa_template_exists:
            print("❌ No template files found!")
            return False
            
    except Exception as e:
        print(f"❌ ADS generator initialization failed: {e}")
        return False
    
    # Test PDF generation
    output_path = "test_ads_output.pdf"
    
    try:
        print(f"\n🔄 Generating ADS PDF...")
        result_path = ads_generator.generate_ads_pdf(test_data, output_path)
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ ADS PDF generated successfully!")
            print(f"📄 File: {result_path}")
            print(f"📊 Size: {file_size} bytes")
            return True
        else:
            print(f"❌ ADS PDF generation failed - no output file")
            return False
            
    except Exception as e:
        print(f"❌ ADS PDF generation failed: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_ads_generation()
    if success:
        print(f"\n🎉 ADS generation test passed!")
    else:
        print(f"\n💥 ADS generation test failed!")