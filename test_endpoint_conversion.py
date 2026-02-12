#!/usr/bin/env python3
"""
Test the exact conversion process used in the endpoint.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import json
from app.models.enhanced_extraction import EnhancedExtractionResult, ExtractionMethod, DataCompleteness
from app.models.patent_application import PatentApplicationMetadata, Inventor, Applicant
from app.services.ads_generator import ADSGenerator
import tempfile
import io

def test_endpoint_conversion():
    """Test the exact conversion process used in the endpoint."""
    
    print("🔍 Testing Endpoint Conversion Process")
    print("=" * 50)
    
    # Load the clean data (same as endpoint)
    try:
        with open('clean_app_data_20260206_023028.json', 'r') as f:
            app_data = json.load(f)
        print("✅ Loaded saved application data")
    except FileNotFoundError:
        print("❌ Clean data file not found. Run debug script first.")
        return False
    
    # Step 1: Convert to EnhancedExtractionResult (same as endpoint)
    print("\n1. Converting to EnhancedExtractionResult...")
    try:
        def convert_enums(data):
            """Convert string enum values back to enum objects"""
            if isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    if key == 'extraction_method' and isinstance(value, str):
                        try:
                            result[key] = ExtractionMethod(value)
                        except ValueError:
                            result[key] = value
                    elif key == 'completeness' and isinstance(value, str):
                        try:
                            result[key] = DataCompleteness(value)
                        except ValueError:
                            result[key] = value
                    else:
                        result[key] = convert_enums(value)
                return result
            elif isinstance(data, list):
                return [convert_enums(item) for item in data]
            else:
                return data
        
        converted_data = convert_enums(app_data)
        extraction_result = EnhancedExtractionResult(**converted_data)
        print("✅ EnhancedExtractionResult conversion successful")
    except Exception as e:
        print(f"❌ EnhancedExtractionResult conversion failed: {e}")
        return False
    
    # Step 2: Convert to PatentApplicationMetadata (same as endpoint)
    print("\n2. Converting to PatentApplicationMetadata...")
    try:
        def convert_to_patent_metadata(enhanced_result: EnhancedExtractionResult) -> PatentApplicationMetadata:
            """Convert EnhancedExtractionResult to PatentApplicationMetadata for ADS generation"""
            
            # Convert inventors
            patent_inventors = []
            for inv in enhanced_result.inventors:
                patent_inventor = Inventor(
                    first_name=inv.given_name,
                    middle_name=inv.middle_name,
                    last_name=inv.family_name,
                    name=inv.full_name,
                    street_address=inv.street_address,
                    city=inv.city,
                    state=inv.state,
                    zip_code=inv.postal_code,
                    country=inv.country,
                    citizenship=inv.citizenship,
                    extraction_confidence=inv.confidence_score
                )
                patent_inventors.append(patent_inventor)
            
            # Convert applicants
            patent_applicants = []
            for app in enhanced_result.applicants:
                patent_applicant = Applicant(
                    name=app.organization_name or f"{app.individual_given_name or ''} {app.individual_family_name or ''}".strip(),
                    org_name=app.organization_name,
                    is_organization=bool(app.organization_name),
                    first_name=app.individual_given_name,
                    last_name=app.individual_family_name,
                    street_address=app.street_address,
                    city=app.city,
                    state=app.state,
                    zip_code=app.postal_code,
                    country=app.country,
                    phone=app.phone_number,
                    email=app.email_address
                )
                patent_applicants.append(patent_applicant)
            
            return PatentApplicationMetadata(
                title=enhanced_result.title,
                application_number=enhanced_result.application_number,
                filing_date=enhanced_result.filing_date,
                entity_status=enhanced_result.entity_status,
                total_drawing_sheets=enhanced_result.total_drawing_sheets,
                inventors=patent_inventors,
                applicants=patent_applicants,
                extraction_confidence=enhanced_result.quality_metrics.overall_quality_score
            )
        
        patent_metadata = convert_to_patent_metadata(extraction_result)
        print("✅ PatentApplicationMetadata conversion successful")
        print(f"   Title: {patent_metadata.title}")
        print(f"   App Number: {patent_metadata.application_number}")
        print(f"   Inventors: {len(patent_metadata.inventors)}")
        print(f"   Applicants: {len(patent_metadata.applicants)}")
        
    except Exception as e:
        print(f"❌ PatentApplicationMetadata conversion failed: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False
    
    # Step 3: Generate ADS PDF (same as endpoint)
    print("\n3. Generating ADS PDF...")
    try:
        ads_generator = ADSGenerator()
        
        # Create temporary file (same as endpoint)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Generate the PDF file
            ads_generator.generate_ads_pdf(patent_metadata, temp_path)
            
            # Check if file was created
            if not os.path.exists(temp_path):
                raise Exception("ADS PDF generation failed - no output file created")
            
            # Read the generated PDF and create a stream
            with open(temp_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            if not pdf_content:
                raise Exception("ADS PDF generation failed - empty output file")
            
            pdf_stream = io.BytesIO(pdf_content)
            print(f"✅ ADS PDF generated successfully ({len(pdf_content)} bytes)")
            
            # Save a copy for verification
            with open('test_endpoint_output.pdf', 'wb') as f:
                f.write(pdf_content)
            print(f"📄 PDF saved as: test_endpoint_output.pdf")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        return True
        
    except Exception as e:
        print(f"❌ ADS PDF generation failed: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_endpoint_conversion()
    if success:
        print(f"\n🎉 Endpoint conversion test passed!")
        print("The issue is not in the conversion logic.")
    else:
        print(f"\n💥 Endpoint conversion test failed!")
        print("Found the issue in the conversion process.")