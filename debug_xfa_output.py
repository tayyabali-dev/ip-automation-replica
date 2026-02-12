#!/usr/bin/env python3
"""
Debug script to examine the XFA XML output and see what correspondence data is included.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.llm import LLMService
from app.services.ads_xfa_builder import build_from_patent_metadata

async def debug_xfa_output():
    """Debug the XFA XML output to see correspondence address data."""
    
    print("🔍 Debugging XFA XML Output")
    print("=" * 50)
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test with the DOCX file
    docx_file = "test_data/patent_application_test.docx"
    
    if not os.path.exists(docx_file):
        print(f"❌ Test DOCX file not found: {docx_file}")
        return
    
    try:
        # Extract metadata
        with open(docx_file, "rb") as f:
            file_content = f.read()
        
        result = await llm_service.analyze_cover_sheet(
            file_path=docx_file,
            file_content=file_content
        )
        
        print("📊 Extracted Correspondence Address:")
        if result.correspondence_address:
            corr = result.correspondence_address
            print(f"  Name: '{corr.name}'")
            print(f"  Address1: '{corr.address1}'")
            print(f"  City: '{corr.city}'")
            print(f"  State: '{corr.state}'")
            print(f"  Country: '{corr.country}'")
            print(f"  Phone: '{corr.phone}'")
            print(f"  Email: '{corr.email}'")
            print(f"  Customer Number: '{corr.customer_number}'")
        else:
            print("  None extracted")
        
        # Generate XFA XML
        print(f"\n🔧 Generating XFA XML...")
        xml_output = build_from_patent_metadata(result)
        
        print(f"📄 XFA XML Length: {len(xml_output)} characters")
        
        # Search for correspondence-related content
        print(f"\n🔍 Searching for correspondence data in XML:")
        
        # Check for various correspondence-related strings
        search_terms = [
            "Blakely",
            "Sokoloff", 
            "Taylor",
            "Zafman",
            "1279 Oakmead",
            "Sunnyvale",
            "(408) 720-8000",
            "patents@bstlaw.com",
            "12345",
            "corr_name1",
            "corr_address1",
            "corr_city",
            "Name1",
            "address1",
            "customerNumber"
        ]
        
        found_terms = []
        for term in search_terms:
            if term in xml_output:
                found_terms.append(term)
                print(f"  ✅ Found: '{term}'")
            else:
                print(f"  ❌ Missing: '{term}'")
        
        # Show correspondence section of XML
        print(f"\n📋 Correspondence Section of XML:")
        print("-" * 40)
        
        # Find correspondence section
        start_markers = ["<sfCorrepondInfo>", "<sfCorrCustNo>", "<sfCorrAddress>"]
        end_markers = ["</sfCorrAddress>", "<sfemail>"]
        
        for start_marker in start_markers:
            start_idx = xml_output.find(start_marker)
            if start_idx != -1:
                # Find end of correspondence section
                end_idx = start_idx + 500  # Show next 500 chars
                for end_marker in end_markers:
                    marker_idx = xml_output.find(end_marker, start_idx)
                    if marker_idx != -1:
                        end_idx = min(end_idx, marker_idx + len(end_marker) + 50)
                
                corr_section = xml_output[start_idx:end_idx]
                print(corr_section)
                print("-" * 40)
                break
        
        # Save full XML for inspection
        with open("debug_xfa_full.xml", "w") as f:
            f.write(xml_output)
        print(f"\n💾 Full XML saved to: debug_xfa_full.xml")
        
        print(f"\n📈 Summary:")
        print(f"  Found {len(found_terms)}/{len(search_terms)} search terms")
        print(f"  Correspondence extracted: {'Yes' if result.correspondence_address else 'No'}")
        print(f"  XML contains correspondence: {'Yes' if any(found_terms) else 'No'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_xfa_output())