#!/usr/bin/env python3
"""
Debug script to diagnose the SOM expression issue with sfSigHeader.
This script will help validate our assumptions about the XFA template and XML structure.
"""

import sys
import os
from pathlib import Path
import pikepdf
import logging

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.ads_xfa_builder import build_from_patent_metadata, ApplicationData, InventorInfo, ApplicantInfo
from app.services.pdf_injector import PDFInjector

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def analyze_xfa_template():
    """Analyze the XFA template to understand its structure."""
    template_path = "backend/app/templates/xfa_ads_template.pdf"
    
    print("🔍 Analyzing XFA Template Structure")
    print("=" * 50)
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return False
    
    try:
        with pikepdf.Pdf.open(template_path) as pdf:
            print(f"✅ Template opened successfully")
            print(f"📄 Pages: {len(pdf.pages)}")
            
            # Check for XFA structure
            if hasattr(pdf, 'Root') and '/AcroForm' in pdf.Root:
                acroform = pdf.Root['/AcroForm']
                print(f"📋 AcroForm found")
                
                if '/XFA' in acroform:
                    xfa_array = acroform['/XFA']
                    print(f"🔧 XFA array found with {len(xfa_array)} elements")
                    
                    # Examine XFA structure
                    for i in range(0, len(xfa_array), 2):
                        if i + 1 < len(xfa_array):
                            key = str(xfa_array[i])
                            print(f"  XFA Key: {key}")
                            
                            if key == "datasets":
                                print("  📊 Found datasets section")
                                try:
                                    datasets_stream = xfa_array[i + 1]
                                    if hasattr(datasets_stream, 'read_bytes'):
                                        datasets_content = datasets_stream.read_bytes().decode('utf-8', errors='ignore')
                                        print(f"  📏 Datasets size: {len(datasets_content)} bytes")
                                        
                                        # Look for sfSigHeader references
                                        if 'sfSigHeader' in datasets_content:
                                            print("  ✅ sfSigHeader found in template datasets")
                                            # Extract context around sfSigHeader
                                            idx = datasets_content.find('sfSigHeader')
                                            context = datasets_content[max(0, idx-100):idx+200]
                                            print(f"  📝 Context: ...{context}...")
                                        else:
                                            print("  ❌ sfSigHeader NOT found in template datasets")
                                except Exception as e:
                                    print(f"  ⚠️ Could not read datasets: {e}")
                            
                            elif key == "template":
                                print("  📋 Found template section")
                                try:
                                    template_stream = xfa_array[i + 1]
                                    if hasattr(template_stream, 'read_bytes'):
                                        template_content = template_stream.read_bytes().decode('utf-8', errors='ignore')
                                        print(f"  📏 Template size: {len(template_content)} bytes")
                                        
                                        # Look for sfSigHeader field definitions
                                        if 'sfSigHeader' in template_content:
                                            print("  ✅ sfSigHeader found in template definition")
                                            # Extract field definition
                                            idx = template_content.find('sfSigHeader')
                                            context = template_content[max(0, idx-200):idx+300]
                                            print(f"  📝 Field definition: ...{context}...")
                                        else:
                                            print("  ❌ sfSigHeader NOT found in template definition")
                                except Exception as e:
                                    print(f"  ⚠️ Could not read template: {e}")
                else:
                    print("❌ No XFA array found in AcroForm")
            else:
                print("❌ No AcroForm found in PDF")
                
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing template: {e}")
        return False

def test_xml_generation():
    """Test XML generation and look for sfSigHeader issues."""
    print("\n🔧 Testing XML Generation")
    print("=" * 50)
    
    # Create test data
    test_data = ApplicationData(
        title="Test Application for SOM Expression Debug",
        inventors=[
            InventorInfo(
                first_name="John",
                last_name="Doe",
                residence_city="San Francisco",
                residence_state="CA",
                residence_country="United States",
                citizenship="US"
            )
        ],
        applicants=[
            ApplicantInfo(
                org_name="Test Company LLC",
                authority="assignee",
                city="San Francisco",
                state="CA",
                country="United States"
            )
        ]
    )
    
    try:
        # Generate XML
        from app.services.ads_xfa_builder import build_ads_datasets_xml
        xml_output = build_ads_datasets_xml(test_data)
        
        print(f"✅ XML generated successfully")
        print(f"📏 XML size: {len(xml_output)} characters")
        
        # Analyze sfSigHeader in XML
        if 'sfSigHeader' in xml_output:
            print("✅ sfSigHeader found in generated XML")
            
            # Find all occurrences
            idx = 0
            occurrences = []
            while True:
                idx = xml_output.find('sfSigHeader', idx)
                if idx == -1:
                    break
                occurrences.append(idx)
                idx += 1
            
            print(f"📊 Found {len(occurrences)} occurrence(s) of sfSigHeader")
            
            for i, pos in enumerate(occurrences):
                context = xml_output[max(0, pos-50):pos+100]
                print(f"  {i+1}. Context: ...{context}...")
                
                # Check if it's self-closing or has content
                if xml_output[pos:pos+50].find('</sfSigHeader>') != -1:
                    print(f"     Type: Container with closing tag")
                elif xml_output[pos:pos+20].find('/>') != -1:
                    print(f"     Type: Self-closing tag (POTENTIAL ISSUE)")
                else:
                    print(f"     Type: Opening tag")
        else:
            print("❌ sfSigHeader NOT found in generated XML")
            
        return xml_output
        
    except Exception as e:
        print(f"❌ Error generating XML: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_pdf_injection(xml_data):
    """Test PDF injection to reproduce the SOM expression error."""
    if not xml_data:
        print("\n❌ Skipping PDF injection test - no XML data")
        return
        
    print("\n💉 Testing PDF Injection")
    print("=" * 50)
    
    template_path = "backend/app/templates/xfa_ads_template.pdf"
    
    try:
        # Attempt injection
        pdf_buffer = PDFInjector.inject_xml(template_path, xml_data)
        print("✅ PDF injection completed successfully")
        print(f"📏 Output PDF size: {len(pdf_buffer.getvalue())} bytes")
        
        # Save for testing
        with open("debug_som_test_output.pdf", "wb") as f:
            f.write(pdf_buffer.getvalue())
        print("💾 Test PDF saved as: debug_som_test_output.pdf")
        
    except Exception as e:
        print(f"❌ PDF injection failed: {e}")
        
        # Check if this is the SOM expression error
        error_str = str(e).lower()
        if 'som expression' in error_str and 'sfSigHeader' in error_str:
            print("🎯 CONFIRMED: This is the SOM expression error we're debugging!")
            print(f"   Error details: {e}")
        else:
            print("ℹ️  Different error encountered")
            
        import traceback
        traceback.print_exc()

def main():
    """Main debugging function."""
    print("🐛 SOM Expression Debug Tool")
    print("🎯 Target: sfSigHeader dataRef incompatible node type error")
    print("=" * 60)
    
    # Step 1: Analyze template
    template_ok = analyze_xfa_template()
    
    # Step 2: Test XML generation
    xml_data = test_xml_generation()
    
    # Step 3: Test PDF injection (this should reproduce the error)
    test_pdf_injection(xml_data)
    
    print("\n📋 Diagnosis Summary:")
    print("=" * 30)
    print("1. Template analysis:", "✅ OK" if template_ok else "❌ FAILED")
    print("2. XML generation:", "✅ OK" if xml_data else "❌ FAILED")
    print("3. Check the PDF injection results above for SOM expression error")
    
    print("\n🔍 Next Steps:")
    print("- If SOM error reproduced: The issue is confirmed")
    print("- Check template field definitions vs XML structure")
    print("- Consider sfSigHeader should be container, not empty element")

if __name__ == "__main__":
    main()